
import sys
from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

DB_DIR = "./nomic-v-bunker"
STAGE_FILE = "/tmp/olddog.term.md"

def get_bunker_db():
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    return Chroma(persist_directory=DB_DIR, embedding_function=embeddings)

def query_terminal_brain(question: str):
    print(f"[*] Waking up Gemma and accessing memory banks...")

    # 1. Boot up the DB and the LLM
    db = get_bunker_db()
    llm = OllamaLLM(model="gemma3:4b", base_url="http://127.0.0.1:11434")

    # 2. Retrieve the Memory (Strictly filtered to your terminal log)
    print(f"[*] Searching for context related to: '{question}'")
    hits = db.similarity_search(question, k=3, filter={"source": STAGE_FILE})

    if not hits:
        print("[-] No relevant terminal history found in the staging file.")
        return

    # Combine the top 3 chunks into one large context string
    terminal_context = "\n\n---\n\n".join([doc.page_content for doc in hits])

    print(f"[+] Found {len(hits)} relevant memory chunks. Feeding to Gemma...\n")

    # 3. Define the AI Persona and Prompt
    template = """You are an expert Linux Systems and Python/Rust Developer debugging a live system.

    Below is the raw, time-stamped terminal history retrieved from the user's Tmux session:
    <terminal_history>
    {context}
    </terminal_history>

    The user is asking: {question}

    Analyze the terminal history to answer the question. If there is an error, identify exactly what command caused it and provide the specific terminal command to fix it. Keep your answer technical, concise, and direct.
    """

    prompt = ChatPromptTemplate.from_template(template)

    # 4. The LCEL Pipe (Prompt -> LLM -> String Output)
    chain = prompt | llm | StrOutputParser()

    # 5. Execute the Chain!
    # We use .stream() instead of .invoke() so it types out the answer live like a real chat!
    print("--- 🤖 Gemma Analysis ---")
    for chunk in chain.stream({"context": terminal_context, "question": question}):
        print(chunk, end="", flush=True)
    print("\n-------------------------\n")

if __name__ == "__main__":
    # You can pass a question as a command line argument, or use a default
    if len(sys.argv) > 1:
        user_question = " ".join(sys.argv[1:])
    else:
        user_question = """What command caused the 
        'No such file or directory' error, and what is the context?"""

    query_terminal_brain(user_question)
