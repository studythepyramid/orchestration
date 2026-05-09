
import sys
import re
import subprocess
from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

DB_DIR = "./nomic-v-bunker"
STAGE_FILE = "/tmp/olddog.term.md"

"""
Description:
    1, the context management is challenging, 
       how to maintain a recent clean history to terminal actions.
    2, If we stream the output of LLM to shell,
       we should avoid to feed the output of LLM back to the LLM,
       should we?
    3, how to make the loop task driven, 
       such as networking diagnosis or debug the python scripts?
       let's focus on networking things.
"""

def run_cmd(bash_command: str):
    """The Interceptor: This is where the text becomes an action!"""
    print(f"\n[!] AUTONOMOUS ACTION DETECTED: Executing -> {bash_command}")

    # SAFETY PROMPT: Because we are hackers, not maniacs.
    confirm = input("Execute this on your machine? (y/N): ")
    if confirm.lower() != 'y':
        print("[-] Execution aborted by user.")
        return

    try:
        result = subprocess.run(
                bash_command, shell=True, 
                capture_output=True, text=True)
        print("\n--- Execution Result ---")
        print(result.stdout)
        if result.stderr:
            print("ERROR:", result.stderr)
        print("------------------------")
    except Exception as e:
        print(f"[-] Execution failed: {e}")


# to manage the states and history
class States_Singleton:
    # history with time tags
    history: [str] 

    terminal_info: str

    llm_model: str

    def get_history(size_in_bytes: int = 2000):
        # return a good history record

    def set_history(new_history):
        # update the history


def deprecated_autonomous_terminal_agent(question: str):
    db = Chroma(persist_directory=DB_DIR, 
                embedding_function=OllamaEmbeddings(model="nomic-embed-text"))
    llm = OllamaLLM(model="gemma3:4b", base_url="http://127.0.0.1:11434")

    hits = db.similarity_search(question, k=3, filter={"source": STAGE_FILE})
    terminal_context = "\n\n---\n\n".join([doc.page_content for doc in hits])

    template = """You are an good programmer know Ubuntu Linux CLI.
    Analyze this terminal history:
    {context}

    The user asks: {question}

    You MUST respond using exactly this format:

    THOUGHT: [Explain exactly what you see in the logs, 
    what you think the error is, 
    and why your next command will help diagnose or fix it.]
    COMMAND:
    ```bash
    <your command here>
    ```
    """


    chain = ChatPromptTemplate.from_template(template) | llm | StrOutputParser()

    print("--- 🤖 Gemma Analysis ---")
    full_response = ""
    for chunk in chain.stream({"context": terminal_context, "question": question}):
        print(chunk, end="", flush=True)
        full_response += chunk
    print("\n-------------------------\n")

    # THE INTERCEPTOR LOGIC
    # We use regex to hunt down the exact block of text Gemma generated
    match = re.search(r"```bash\n(.*?)\n```", full_response, re.DOTALL)

    if match:
        extracted_command = match.group(1).strip()
        run_cmd(extracted_command)
    else:
        print("[-] No executable bash block found in Gemma's response.")


def network_copilot_loop():

    db = Chroma(persist_directory=DB_DIR, 
                embedding_function=OllamaEmbeddings(model="nomic-embed-text"))
    llm = OllamaLLM(model="gemma3:4b", base_url="http://127.0.0.1:11434")

    hits = db.similarity_search(question, k=3, filter={"source": STAGE_FILE})
    terminal_context = "\n\n---\n\n".join([doc.page_content for doc in hits])


    # pls. redo the template for good performance
    template = """You are an good programmer know Ubuntu Linux CLI.
    Analyze this terminal history:
    {context}

    The user asks: {question}

    You MUST respond using exactly this format:

    THOUGHT: [Explain exactly what you see in the logs, 
    what you think the error is, 
    and why your next command will help diagnose or fix it.]
    COMMAND:
    ```bash
    <your command here>
    ```
    """



    chain = ChatPromptTemplate.from_template(template) | llm | StrOutputParser()

    print("Starting Network Diagnosis Copilot...")

    while True:
        # Grab fresh (non-duplicated) context
        fresh_context = get_clean_tmux_history()

        # Gemma analyzes and suggests commands
        print("\n--- 🤖 Gemma Diagnosis ---")
        ai_suggestion = ""
        for chunk in chain.stream({"context": fresh_context}):
            print(chunk, end="", flush=True)
            ai_suggestion += chunk

        # THE PAUSE (State Management)
        print("\n\n[USER ACTION REQUIRED]")
        print("""Options: 
        [ y ] Execute AI command 
        [ q ] Quit | 
        [Type a question to ask Gemma]""")
        user_input = input(">> ")

        # Routing based on Human Input
        if user_input.lower().strip() == 'q':
            break
        elif user_input.lower().strip() == 'y':
            extract_and_run_bash(ai_suggestion)
            # The output goes to the screen, Tmux sees it, and the loop repeats!
        else:
            # The user asked a question! Append it to the staging file manually,
            # or pass it as a temporary variable to the next loop iteration.
            print(f"Adding context: {user_input}")

if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Analyse the network connection."
    network_copilot_loop(q)
