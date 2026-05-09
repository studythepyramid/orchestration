
import sys
import re
import subprocess
from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

DB_DIR = "./nomic-v-bunker"
STAGE_FILE = "/tmp/olddog.term.md"

def execute_autonomous_fix(bash_command: str):
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

def autonomous_terminal_agent(question: str):
    db = Chroma(persist_directory=DB_DIR, 
                embedding_function=OllamaEmbeddings(model="nomic-embed-text"))
    llm = OllamaLLM(model="gemma3:4b", base_url="http://127.0.0.1:11434")

    hits = db.similarity_search(question, k=3, filter={"source": STAGE_FILE})
    terminal_context = "\n\n---\n\n".join([doc.page_content for doc in hits])

    template = """You are an autonomous Linux Debugging Agent.
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
        execute_autonomous_fix(extracted_command)
    else:
        print("[-] No executable bash block found in Gemma's response.")

if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Fix the 'No such file' error."
    autonomous_terminal_agent(q)
