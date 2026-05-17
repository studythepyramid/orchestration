### ~/dev/orchestration/nscan.py
### How this architecture works:
# 1. You run `uv run nscan.py "I can't reach github.com"`.
# 2. LLM Modle may say: *"Let's check DNS. Run `nslookup github.com`"*.
# 3. You press `y`. Python runs it,
#   captures the IP addresses, and silently stores them in `ContextManager`.
# 4. The loop restarts.
#   Gemma automatically sees the IPs in the context and says,
#   *"DNS works. Let's trace the route: `traceroute github.com`"*.
# 5. If Gemma makes a mistake, you just type:
#   *"No, check my local IP first"*,
#   and the context manager feeds your exact feedback into her next turn!
###


import re
import subprocess
import sys
from datetime import datetime

from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM

CM_SYS_PROMPT = """You are an elite Network Diagnostic AI Copilot.
Your job is to help the user debug their Linux network step-by-step.

RULES:
1. Analyze the context and suggest ONE bash command to diagnose the issue.
2. You MUST wrap your command in a bash block like this:
```bash
<command>
```
3. NEVER suggest interactive or infinite commands (e.g.,
   use `ping -c 4` instead of `ping`, never use `top`, `vim`, or `nano`).
4. Keep your explanations extremely brief (1-2 sentences).
"""


class ContextManager:
    """Singleton-style State Holder for the HITL Loop"""

    _instance = None

    # THE LSP FIX: Declare the attributes so Pyright knows they exist
    history: list[str]
    system_prompt: str
    llm: OllamaLLM | None
    lalamo: OllamaLLM | None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ContextManager, cls).__new__(cls)

            cls._instance.history = []
            cls._instance.system_prompt = CM_SYS_PROMPT

            # python LLM model instance
            cls._instance.llm = OllamaLLM(
                model="gemma3:4b", base_url="http://127.0.0.1:11434"
            )

            # llm is tongue twisting to pronounce, so there's lalamo :)
            cls._instance.lalamo = cls._instance.llm
        return cls._instance

    def add_user_event(self, event_text: str):
        """Adds terminal output or human feedback to the context."""
        self.history.append(f"USER/SYSTEM: {event_text}")

    def add_ai_event(self, event_text: str):
        """Records what the AI previously decided."""
        self.history.append(f"AI: Suggested command -> {event_text}")

    def get_full_context(self) -> str:
        """Compiles the clean history for the LLM."""
        return "\n".join(self.history)


def run_cmd(bash_command: str) -> str:
    """Executes the command and returns the raw output for the Context Manager."""
    print(f"\n[⚡] EXECUTING -> {bash_command}")
    try:
        # Timeout added to prevent infinite hanging scripts
        result = subprocess.run(
            bash_command, shell=True, capture_output=True, text=True, timeout=15
        )
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        output = f"[{timestamp}]\n"
        output += (
            result.stdout.strip() if result.stdout.strip() else "[No stdout output]"
        )
        if result.stderr:
            output += f"\n[STDERR]: {result.stderr.strip()}"

        print("\n--- Execution Result ---")
        print(output)
        print("------------------------")
        return output
    except subprocess.TimeoutExpired:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        output = f"[{timestamp}]\n[ERROR]: Command timed out after 15 seconds."
        print(f"[-] Command timed out!")
        return output
    except Exception as e:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        output = f"[{timestamp}]\n[ERROR]: Execution failed: {e}"
        print(f"[-] Execution failed: {e}")
        return output


def network_copilot_loop():
    cm = ContextManager()

    assert cm.lalamo is not None, "Fatal: cm.llm failed to initialize!"
    llm = cm.lalamo

    template = (
        cm.system_prompt
        + """\n\nCURRENT STATE/HISTORY:
    \n{context}\n\nWhat is your next diagnostic command?"""
    )
    prompt = ChatPromptTemplate.from_template(template)

    assert llm is not None, "Fatal: LLM failed to initialize!"
    chain = prompt | llm

    print("\n[📶] Booting Network Diagnostic HITL Copilot...")
    print("[!] Type 'q' at any prompt to exit.\n")

    # Initial Kickstart
    if len(sys.argv) > 1:
        initial_issue = " ".join(sys.argv[1:])
    else:
        initial_issue = """My network connection seems to be failing or
        routing incorrectly. Where should I start?"""

    cm.add_user_event(f"Initial Report: {initial_issue}")

    while True:
        # 1. AI Turn
        print("\n--- 🤖 Gemma Diagnosis ---")
        full_context = cm.get_full_context()
        assert full_context is not None, "Fatal: cm context is None!"

        response = chain.invoke({"context": full_context})
        print(response)

        # 2. Extract Command
        match = re.search(r"```bash\n(.*?)\n```", response, re.DOTALL)
        suggested_cmd = match.group(1).strip() if match else None

        if not suggested_cmd:
            print("\n[-] Gemma didn't output a valid bash block.")
            user_input = input("Provide guidance to Gemma (or 'q' to quit): ")
            if user_input.lower() == "q":
                break
            cm.add_user_event(user_input)
            continue

        cm.add_ai_event(suggested_cmd)
        print("\n[USER ACTION REQUIRED]")
        print(f"Proposed execution: {suggested_cmd}")
        user_input = input(
            """Options:
                [y] Execute
                [q] Quit
                [Type feedback/alternate command]: """
        ).strip()

        if user_input.lower() == "q":
            print("[*] Terminating loop.")
            break
        elif user_input.lower() == "y":
            cmd_output = run_cmd(suggested_cmd)
            cm.add_user_event(f"Executed '{suggested_cmd}'. Result:\n{cmd_output}")
        else:
            # User typed their own command or feedback
            cm.add_user_event(f"User overrode AI with feedback/command: {user_input}")
            if user_input.startswith("!"):
                # Let user execute a command manually by prefixing with !
                cmd_output = run_cmd(user_input[1:])
                cm.add_user_event(
                    f"""User manually executed
                        '{user_input[1:]}'. Result:\n{cmd_output}"""
                )


if __name__ == "__main__":
    network_copilot_loop()
