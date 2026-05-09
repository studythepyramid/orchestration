
import subprocess
import os
from datetime import datetime

# The designated Staging Ground
STAGE_FILE = "/tmp/olddog.terminal.md"

def run_cmd(cmd: list) -> str:
    """Helper to execute shell commands and capture the output safely."""
    try:
        # capture_output=True grabs stdout, text=True returns a string instead of bytes
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"[-] Tmux command failed: {' '.join(cmd)}")
        print(f"    Error: {e.stderr.strip()}")
        return ""

def stage_tmux_history():
    print(f"[*] Accessing Tmux memory banks...")

    # 1. Gather the Metadata via subprocess
    pane_id = run_cmd(["tmux", "display-message", "-p", "session_#S_window_#W_pane_#P"])
    pane_path = run_cmd(["tmux", "display-message", "-p", "#{pane_current_path}"])

    if not pane_id:
        print("[-] Aborting. Are you sure you are inside a Tmux session?")
        return

    # 2. Capture the actual terminal text
    # -p (print to stdout), -S - (start from the very top of scrollback history)
    context = run_cmd(["tmux", "capture-pane", "-p", "-S", "-"])

    # 3. Format and Stash
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"[*] Staging {len(context.splitlines())} lines of history to {STAGE_FILE}...")

    # Open in 'a' (append) mode to build a continuous timeline!
    with open(STAGE_FILE, 'a+', encoding='utf-8') as f:
        f.write(f"\n\n## 📡 Tmux Capture: {pane_id}\n")
        f.write(f"- **Captured At:** {timestamp}\n")
        f.write(f"- **Working Dir:** {pane_path}\n")
        f.write("```console\n")
        f.write(context + "\n")
        f.write("```\n")
        f.write("---\n") # Visual separator for the next capture

    print(f"[+] Success! History safely quarantined.")

if __name__ == "__main__":
    stage_tmux_history()
