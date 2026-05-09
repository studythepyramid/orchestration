import re
import sys
import subprocess
from langchain_core.prompts import ChatPromptTemplate
import context_mgr as cm

# Global chain variable to be initialized in mis_prepare
chain = None
ctx = None

PROMPT_intro = """
CURRENT STATE:
    \n{context}\n\nWhat is your next diagnostic command?
    """

PROMPT_update = """
CURRENT STATE:
    {context}
    Then, what is your next move?
    """

def fetch_bash_cmds(text:str):
    # Extract Command

    # refactor, change to grab all bash cmds
    match = re.search(
            r"```bash\n(.*?)\n```", 
            text, re.DOTALL)
    suggested_cmd = match.group(1).strip() if match else None
    return [suggested_cmd]


def head_char(text) -> str:
    # peek the head of text, if it's [digit or letter] return it, 
    # else return a empty str ''

    pass


def get_input():
    print("\n[USER ACTION REQUIRED]")
    user_input = input(
            """Options: 
            [y] Execute 
            [q] Quit 
            [Type feedback/alternate command]: """).strip()

    input_dict ={ 
                 "case": '',
                 "input": user_input,
                 "cmd": ''
            }
    return input_dict


def chat():
    global chain
    if chain is None:
        print("Error: Chain not initialized. Run mis_prepare() first.")
        return
    
    full_context = ctx.get_full_context()
    response = chain.invoke({"context": full_context})
    print(response)


def run_cmd(bash_command: str) -> str:
    """Executes the command and returns the raw output for the Context Manager."""
    print(f"\n[⚡] EXECUTING -> {bash_command}")
    try:
        # Timeout added to prevent infinite hanging scripts
        result = subprocess.run(
            bash_command, shell=True,
            capture_output=True, text=True, timeout=15
        )
        output = result.stdout.strip()
        if result.stderr:
            output += f"\nERROR: {result.stderr.strip()}"

        print("\n--- Execution Result ---")
        print(output if output else "[No output returned]")
        print("------------------------")
        return output
    except subprocess.TimeoutExpired:
        print("[-] Command timed out!")
        return "Command timed out after 15 seconds."
    except Exception as e:
        print(f"[-] Execution failed: {e}")
        return str(e)


def cli_arguments():
    """Handles initial input from command line or defaults."""
    global ctx
    if ctx is None:
        ctx = cm.ContextManager()

    if len(sys.argv) > 1:
        initial_issue = " ".join(sys.argv[1:])
    else:
        initial_issue = """My network connection seems to be failing or
        routing incorrectly. Where should I start?"""

    ctx.add_user_event(f"Initial Report: {initial_issue}")


def mis_prepare():
    global chain, ctx
    ctx = cm.ContextManager()

    assert ctx.lalamo is not None, "Fatal: cm.llm failed to initialize!"
    llm = ctx.lalamo

    template = ctx.system_prompt + """\n\nCURRENT STATE/HISTORY:
    \n{context}\n\nWhat is your next diagnostic command?"""

    prompt = ChatPromptTemplate.from_template(template)

    assert llm is not None, "Fatal: LLM failed to initialize!"
    chain = prompt | llm

    print("\n[📶] Booting Network Diagnostic HITL Copilot...")
    print("[!] Type 'q' at any prompt to exit.\n")


    pass



def start_turn_based_game():
    mis_prepare()
    cli_arguments()

    while True:
        # Get AI response
        full_context = ctx.get_full_context()
        response = chain.invoke({"context": full_context})
        print(f"\n[AI]: {response}")
        
        cmds = fetch_bash_cmds(response)
        suggested_cmd = cmds[0] if cmds else None

        input_data = get_input()
        user_input = input_data["input"]

        match user_input.lower():
            case "q" | "exit" | "quit":
                print("[*] Terminating loop.")
                break 
            case "y":
                if suggested_cmd:
                    cmd_output = run_cmd(suggested_cmd)
                    ctx.add_ai_event(suggested_cmd)
                    ctx.add_user_event(f"Executed '{suggested_cmd}'. Result:\n{cmd_output}")
                else:
                    print("[-] No command suggested by AI to execute.")
            case "talk": 
                print("[Chat Mode - Not fully implemented]")
            case "query":
                print("[Query Mode - Not fully implemented]")
            case "help": 
                print("Options: y (execute AI cmd), q (quit), or type feedback/command")
            case _:  
                if user_input:
                    ctx.add_user_event(f"User feedback/override: {user_input}")
                    if user_input.startswith("!"):
                        manual_cmd = user_input[1:].strip()
                        cmd_output = run_cmd(manual_cmd)
                        ctx.add_user_event(f"User manually executed '{manual_cmd}'. Result:\n{cmd_output}")
                else:
                    print("No input provided.")





        #if user_input.lower() == 'q':
        #    print("[*] Terminating loop.")
        #    break
        #elif user_input.lower() == 'y':
        #else:
        #    # User typed their own command or feedback
        #    cm.add_user_event(f"User overrode AI with feedback/command: {user_input}")
        #    if user_input.startswith("!"):
        #        # Let user execute a command manually by prefixing with !
        #        cmd_output = run_cmd(user_input[1:])
        #        cm.add_user_event(
        #                f"""User manually executed 
        #                '{user_input[1:]}'. Result:\n{cmd_output}""")



