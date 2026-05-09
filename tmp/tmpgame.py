
def get_input():
    """
    Handles user input with a cleaner, consistent prompt.
    """
    print("\n" + "="*40)
    print("[TURN: USER]")
    print(" (y)      -> Execute AI suggested command(s)")
    print(" (q)      -> Quit game")
    print(" (!cmd)   -> Manual override (e.g., !ls -p)")
    print(" (text)   -> Give feedback or instructions to AI")
    user_input = input(">> ").strip()

    return {"input": user_input}

def run_cmd(bash_command: str) -> str:
    """Executes the command and returns the raw output for the context."""
    print(f"\n[⚡] EXECUTING -> {bash_command}")
    try:
        result = subprocess.run(
            bash_command, shell=True,
            capture_output=True, text=True, timeout=20
        )
        output = result.stdout.strip()
        if result.stderr:
            output += f"\n[STDERR]: {result.stderr.strip()}"
        return output if output else "[No output returned]"
    except subprocess.TimeoutExpired:
        return "Command timed out after 20 seconds."
    except Exception as e:
        return f"Execution Error: {str(e)}"

# this is all left by copy/clone from other old thing,
# leave it along, deprecated
def mis_history():
    """Initializes the LLM chain and Context Manager."""
    global chain, ctx
    ctx = cm.ContextManager()

    # Using your local ollama instance via context manager
    llm = ctx.lalamo

    template = ctx.system_prompt + """

    CURRENT SYSTEM STATE & HISTORY:
    {context}

    YOUR TURN:
    Analyze the state and provide the next diagnostic move.
    Wrap all executable shell commands in ```bash blocks.
    """

    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llm
    print("\n[📶] Booting 'Game of Turns' Diagnostic System...")


def fetch_bash_cmds(text:str):
    # Extract Command

    # refactor, change to grab all bash cmds
    finds = re.findall(
            r"```bash\n(.*?)\n```", 
            text, re.DOTALL)
    suggested_cmd = finds #?
    return [suggested_cmd]



def start_turn_based_game():

    # Handle initial CLI arguments as the first user event
    initial_issue = " ".join( sys.argv[1:]) if len(sys.argv) > 1 else "Perform a general system health check."
    ctx.add_user_event(f"INITIAL REPORT: {initial_issue}")

    while True:
        # 1. AI TURN: Generate response based on current context
        full_context = ctx.get_full_context()
        print("\n[Thinking...]")
        response = chain.invoke({"context": full_context})
        print(f"\n[AI]: {response}")

        cmds = fetch_bash_cmds(response)

        # 2. USER TURN: Decide what to do
        user_choice = get_input()["input"]

        # 3. EVALUATE TURN
        match user_choice.lower():
            case "q" | "exit" | "quit":
                print("[*] Game Over. Terminating.")
                break

            case "y":
                if cmds:
                    for cmd in cmds:
                        output = run_cmd(cmd)
                        # Add both the action and the result to context
                        ctx.add_ai_event(f"I suggested: {cmd}")
                        ctx.add_user_event(f"EXECUTION RESULT OF '{cmd}':\n{output}")
                else:
                    print("[-] AI didn't suggest any code to run. Use 'text' to nudge it.")

            case _ if user_choice.startswith("!"):
                # Manual command execution via "!" prefix
                manual_cmd = user_choice[1:].strip()
                output = run_cmd(manual_cmd)
                ctx.add_user_event(f"USER OVERRIDE (Manual Cmd) '{manual_cmd}':\n{output}")

            case "":
                print("[!] Empty input. AI will re-analyze current state.")

            case _:
                # Treat everything else as natural language feedback/correction
                ctx.add_user_event(f"USER FEEDBACK: {user_choice}")

if __name__ == "__main__":
    try:
        start_turn_based_game()
    except KeyboardInterrupt:
        print("\n[*] Interrupted by user. Closing.")


