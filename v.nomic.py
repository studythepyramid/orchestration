
import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_chroma import Chroma

# 1. NEW IMPORT: Drop HuggingFace and bring in the Ollama connector
#from langchain_community.embeddings import OllamaEmbeddings
from langchain_ollama import OllamaEmbeddings

# Define your target file and the new bunker database name
FILE_PATH = "./chat-apr-11.md"
DB_DIR = "./nomic-v-bunker"

# 2. NEW EMBEDDING ENGINE: Point it to your downloaded Nomic model
embeddings = OllamaEmbeddings(model="nomic-embed-text")
#embeddings = OllamaEmbeddings(model="nomic-embed-text:latest") # latest?

# 3. Persistence Logic: Load or Create the Vector Store
if os.path.exists(DB_DIR):
    print(f"--- Booting up {DB_DIR} memory banks ---")
    # LangChain handles the embedding function automatically behind the scenes
    vectorstore = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
else:
    print(f"--- First run: Indexing {FILE_PATH} into new bunker ---")
    loader = TextLoader(FILE_PATH)
    documents = loader.load()

    # Chopping the text into chunks to protect the LLM context window
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    texts = text_splitter.split_documents(documents)

    # Translating to 768-dimensional math and saving to disk
    vectorstore = Chroma.from_documents(
        documents=texts,
        embedding=embeddings,
        persist_directory=DB_DIR
    )

print("--- Bunker vectorstore ready ---")
