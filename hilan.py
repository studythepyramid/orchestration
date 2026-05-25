#!/usr/bin/env -S .venv/bin/python

# #!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "ollama",
# ]
# ///


import datetime
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

import ollama

# --- Configuration ---
#MODEL_NAME = "gemma3:4b"  # Adjust to your active local model

# gemini, here it's 1b model to test small model first.
MODEL_NAME = "gemma3:1b"  # Adjust to your active local model
LINE_WIDTH = 70
HISTORY_FILE = Path("~/tmp/learn.words.en.md").expanduser()


def log_words_to_history(words: list[str]):
    """Appends the queried words and a timestamp to the markdown tracker."""
    # Ensure the ~/tmp directory exists before writing
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    words_str = ", ".join(words)
    
    log_entry = f"### {timestamp}\n- **Queried:** {words_str}\n\n"
    
    try:
        # gemini, the file mode is 'a+' to avoid no file case.
        # tell me if it's not necessary to use 'a+' mode.
        with open(HISTORY_FILE, "a+", encoding="utf-8") as f:
            f.write(log_entry)
    except IOError as e:
        print(f"⚠️ Warning: Could not write to history file {HISTORY_FILE}: {e}", file=sys.stderr)


def resolve_pager_cmd() -> list[str]:
    """Prefer batcat (Ubuntu/debian bat); fall back to less."""
    if shutil.which("batcat"):
        return ["batcat", "-p", "-l", "markdown", "--paging=always"]
    if shutil.which("bat"):
        return ["bat", "-p", "-l", "markdown", "--paging=always"]
    return ["less", "-R"]


def pager(content: str) -> None:
    """Send formatted text to a terminal pager."""
    if not content.strip():
        return

    pager_cmd = resolve_pager_cmd()
    pager_name = pager_cmd[0]
    print(f"\nOpening {pager_name}...", file=sys.stderr)

    try:
        proc = subprocess.Popen(pager_cmd, stdin=subprocess.PIPE, text=True)
        assert proc.stdin is not None
        proc.stdin.write(content)
        proc.stdin.close()
        proc.wait()
    except BrokenPipeError:
        # User quit the pager before reading everything.
        pass
    except FileNotFoundError:
        print(content)


def format_stream_line(line: str, wrapper: textwrap.TextWrapper) -> str:
    if line.strip() == "":
        return ""
    return wrapper.fill(line)


def main():
    if len(sys.argv) < 2:
        print("Usage: hilan <word1> [word2] [word3] ...")
        print("Example: hilan slit slot slab slap snip")
        sys.exit(1)

    target_words = sys.argv[1:]
    words_display = ", ".join(target_words)

    print(f"📚 Logging new words to {HISTORY_FILE}...")
    log_words_to_history(target_words)

    print(f"Querying LLM {MODEL_NAME} for: {words_display}...", file=sys.stderr)

    # Context Construction: The Tutor Persona and Challenge Logic
    system_instruction = (
        "You are an expert English linguistics tutor. The user will provide a list of words. "
        "For EACH word, provide:\n"
        "1. A concise, clear definition.\n"
        "2. A practical example sentence.\n\n"
        "After defining the user's words, analyze their approximate vocabulary difficulty tier. "
        "Then, generate a 'CHALLENGE TIER' section where you suggest 3 to 5 new words that are "
        "slightly more advanced or share a structural/thematic root with the provided words, "
        "briefly explaining why you chose them."
    )

    prompt_content = f"Please explain these words and challenge me: {words_display}"

    try:
        # Stream from Ollama, collect wrapped lines, then open the pager.
        stream = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt_content},
            ],
            stream=True,
            options={
                "temperature": 0.4, # Slight creativity for generating the challenge words
                "top_k": 20,
            }
        )

        wrapper = textwrap.TextWrapper(width=LINE_WIDTH)
        buffer = ""
        pager_lines: list[str] = [f"# Words: {words_display}", ""]

        for chunk in stream:
            buffer += chunk["message"]["content"]
            while True:
                idx = buffer.find("\n")
                if idx == -1:
                    break
                line = buffer[:idx]
                pager_lines.append(format_stream_line(line, wrapper))
                buffer = buffer[idx + 1 :]

        if buffer:
            pager_lines.append(format_stream_line(buffer, wrapper))

        pager_body = "\n".join(pager_lines)
        footer = "\n" + "-" * LINE_WIDTH
        pager(pager_body + footer)

    except Exception as e:
        print(f"\n❌ Ollama Communication Failure: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
