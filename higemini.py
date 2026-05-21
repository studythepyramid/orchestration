#!/home/za/dev/orchestration/.venv/bin/python

#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "ollama",
#   "google-genai",
# ]
# ///

# old #!
#!/usr/bin/env python3
import os
import sys
# ... keep your existing imports (subprocess, re, textwrap, ollama)

# Import the modern Google GenAI Client
try:
    from google import genai
except ImportError:
    genai = None

# 1. New Routing Configuration
ONLINE_MODEL = "gemini-2.5-flash"  # Blazing fast, massive context window
LOCAL_MODEL = "gemma3:4b"


def run_online_gemini(system_instruction: str, prompt_content: str):
    """Executes the analysis using the cloud-hosted Gemini API."""
    if not genai:
        print("❌ Error: 'google-genai' library not installed. Run 'uv add google-genai'.", file=sys.stderr)
        sys.exit(1)

    # The client automatically discovers os.environ["GEMINI_API_KEY"] natively!
    if "GEMINI_API_KEY" not in os.environ:
        print("❌ Error: $GEMINI_API_KEY environment variable not found.", file=sys.stderr)
        print("Please run: export GEMINI_API_KEY='your_key'", file=sys.stderr)
        sys.exit(1)

    try:
        client = genai.Client()
        
        # Request a streaming response from the cloud
        response = client.models.generate_content_stream(
            model=ONLINE_MODEL,
            contents=prompt_content,
            config={
                "system_instruction": system_instruction,
                "temperature": 0.0, # Keep it factual for system administration
            }
        )

        print(f"☁️ Processing turn via Gemini Cloud [{ONLINE_MODEL}]...\n")
        print("-" * 60)
        
        wrapper = textwrap.TextWrapper(width=70)
        for chunk in response:
            if chunk.text:
                print(wrapper.fill(chunk.text), end="")
        print("\n" + "-" * 60)

    except Exception as e:
        print(f"\n❌ Gemini API Communication Failure: {e}", file=sys.stderr)


def main():
    # Parse custom arguments
    args = sys.argv[1:]
    
    use_online = False
    if "--online" in args:
        use_online = True
        args.remove("--online") # Strip the flag so the rest of your parsing logic works

    # Re-map your original argument checks against the stripped list
    if len(args) < 2 or args[0] != "man":
        print("Usage: hi.py [--online] man <topic> [optional questions...]")
        sys.exit(1)

    target_topic = args[1]
    user_question = " ".join(args[2:]) if len(args) > 2 else ""

    # ... [Keep your excellent get_man_page and prompt assembly logic here] ...

    # 2. Dynamic Routing Engine Switch
    if use_online:
        run_online_gemini(system_instruction, prompt_content)
    else:
        # Fall back to your existing local Ollama chat execution block
        run_local_ollama(system_instruction, prompt_content)


if __name__ == "__main__":
    #!/usr/bin/env uv run
    # /// script
    # dependencies = ["google-genai"]
    # ///

    #from google import genai
    #import os

    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Confirm connectivity: say 'SOS System Online'"
    )
    print(response.text)
