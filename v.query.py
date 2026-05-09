
import os
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

DB_DIR = "./nomic-v-bunker"

# 1. Boot up the exact same translator you used to build the database
embeddings = OllamaEmbeddings(model="nomic-embed-text")

# 2. Connect to the existing filing cabinet
if not os.path.exists(DB_DIR):
    print("Error: Bunker not found! Run h.py first.")
    exit()

print(f"--- Accessing {DB_DIR} memory banks ---\n")
vectorstore = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)

# 3. Define the query you want to search for
# (I threw in one of your recent architectural shifts as a test!)
query = "What was the 4-step plan? did we pushed to cycles, and it C1b?"

print(f"[?] Querying memory for: '{query}'")
print("=" * 50)

# 4. The Magic: Find the 3 closest math vectors and return their text
# k=3 means "Top 3 results"
results = vectorstore.similarity_search(query, k=3)

# 5. Display your favorite plain text output
for i, doc in enumerate(results):
    print(f"\n--- MEMORY FRAGMENT {i+1} ---")
    print(doc.page_content)
    print("-" * 50)

print("\n--- Search Complete ---")
