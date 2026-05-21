#!/home/za/dev/orchestration/.venv/bin/python

#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "ollama",
#   "google-genai",
# ]
# ///
# This is option for 'uv' run global links every time:

# old #! , this can be used in dev/orchestration/ folder only
#!/usr/bin/env python3
import re
import subprocess
import sys
import textwrap

import ollama

from model_query import get_model_context_size

# Configuration: Update this token direction vector to match your active model
MODEL_NAME = "gemma3:4b"  # e.g., llama3, qwen3-coder, deepseek-r1

LINE_WIDTH = 70  # Wrap LLM output to this many columns

# Query model's native context size in tokens, reserve 350 for overhead,
# then convert token budget to character budget (≈3.5 chars per token)
_TOKENS_RESERVE = 350
_TOKENS_TO_CHARS = 3.5
_model_token_limit = get_model_context_size(MODEL_NAME)
context_bytes = int((_model_token_limit - _TOKENS_RESERVE) * _TOKENS_TO_CHARS)


def clean_man_page(text: str) -> str:
    """Strips out raw terminal formatting backspaces and ANSI byte noise."""
    # Removes character-backspace overrides (e.g., 's\bsh\bh') used for bold formatting
    text = re.sub(r".\x08", "", text)
    # Removes residual terminal escape sequences
    text = re.sub(r"\x1b\[[0-9;]*[a-zA-Z]", "", text)
    return text


def get_man_page(topic: str) -> str:
    """Invokes system subprocess to read raw manual pages via cat."""
    try:
        # -P cat overrides the interactive pager block to stream directly to stdout
        result = subprocess.run(
            ["man", "-P", "cat", topic], capture_output=True, text=True, check=True
        )
        return clean_man_page(result.stdout)
    except subprocess.CalledProcessError:
        print(
            f"❌ Error: Manual page for '{topic}' not found on this system.",
            file=sys.stderr,
        )
        sys.exit(1)


def extract_man_section(man_text: str, section_name: str) -> str:
    """
    Extracts a specific section (e.g., 'EXAMPLES') from the raw man page text.
    Handles matching standard uppercase section headers.
    """
    normalized_text = clean_man_page(man_text)

    # Force uppercase for matching standard man sections
    target_header = section_name.strip().upper()

    # Regex logic: Find the target header at the start of a line,
    # then lazily capture everything until the next line starting with a capital letter header
    pattern = rf"(^|\n){target_header}\n(.*?)(?=\n[A-Z][A-Z\s_-]+\n|$)"

    match = re.search(pattern, normalized_text, re.DOTALL | re.MULTILINE)
    if match:
        return f"--- SECTION: {target_header} ---\n" + match.group(2).strip()

    return ""


def main():
    # We require at least 'hi man <topic>'
    if len(sys.argv) < 3 or sys.argv[1] != "man":
        print("Usage: hi man <topic> [optional specific questions...]")
        sys.exit(1)

    target_topic = sys.argv[2]

    # Capture any subsequent query elements passed beyond the topic argument
    user_question = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else ""

    print(f"📖 Fetching manual page for system control: '{target_topic}'...")
    man_content = get_man_page(target_topic)
    # Trim to context limit to avoid overflowing the model's window
    if len(man_content) > context_bytes:
        print(f"⚠️  Man page is large, truncating to {context_bytes} characters.")
        man_content = man_content[:context_bytes]

    # Context Construction: Packaging our system blueprint context sandbox
    system_instruction = (
        "You are an expert Linux system administrator assistant. Your task is to analyze "
        "the provided manual page context and provide accurate, actionable instructions. "
        "Keep your output highly technical, prioritizing real command structures, flags, "
        "and terminal configuration examples."
    )

    if user_question:
        prompt_content = (
            f"Context: Here is the man page for {target_topic}:\n\n{man_content}\n\n"
            f"User Query: {user_question}\n\n"
            f"Based STRICTLY on the man page context, answer the User Query precisely with examples."
        )
    else:
        prompt_content = (
            f"Context: Here is the man page for {target_topic}:\n\n{man_content}\n\n"
            f"Provide a concise, high-level summary of this command, listing its core structural "
            f"architecture, standard deployment use cases, and the top 5 most critical operation flags."
        )

    print(f"🤖 Processing turn via local Ollama engine [{MODEL_NAME}]...\n")
    print("-" * 60)

    # Execute streaming chat loop to feed tokens directly back to the terminal layout
    try:
        stream = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt_content},
            ],
            stream=True,
        )

        wrapper = textwrap.TextWrapper(width=LINE_WIDTH)
        buffer = ""

        for chunk in stream:
            buffer += chunk["message"]["content"]
            # Flush complete lines as they form
            while True:
                idx = buffer.find("\n")
                if idx == -1:
                    break
                line = buffer[:idx]
                print(wrapper.fill(line))
                buffer = buffer[idx + 1 :]

        # Flush any remaining text in the buffer
        if buffer:
            print(wrapper.fill(buffer))
        print("-" * 60)

    except Exception as e:
        print(f"\n❌ Ollama Communication Failure: {e}", file=sys.stderr)


def old_text():
    """
    # Force Ollama to unlock the model's true attention capabilities
    options = {
        "num_ctx": 32768,      # Force open the full 32K token architecture runway
        # 0.0 guarantees strict, factual analysis without hallucinating flags
        "temperature": 0.0,
        "top_k": 10,
        "top_p": 0.5
    }

    stream = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt_content}
        ],
        stream=True,
        options=options
    )
    """
    pass


if __name__ == "__main__":
    main()
