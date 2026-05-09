
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

# Import our scavenger tool!
from v_filelist import get_target_files

DB_DIR = "./nomic-v-bunker"

def get_bunker_db():
    """Boot up the connection to the existing memory banks."""
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    return Chroma(persist_directory=DB_DIR, embedding_function=embeddings)

def vectorize_files(file_list: list[str]):
    """Takes a list of absolute paths, chunks them, and appends to the DB."""
    if not file_list:
        print("No files provided. Aborting ingestion.")
        return

    print(f"\n--- Booting up {DB_DIR} for INGESTION ---")
    vectorstore = get_bunker_db()
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)

    total_chunks = 0

    for file_path in file_list:
        print(f"-> Assimilating: {file_path}")
        try:
            # 1. Load the file
            loader = TextLoader(file_path)
            documents = loader.load()

            # 2. Chop it into AI-sized bites
            texts = text_splitter.split_documents(documents)

            # 3. Add to the existing database (Does NOT overwrite old data)
            vectorstore.add_documents(documents=texts)

            total_chunks += len(texts)
            print(f"   Success: +{len(texts)} chunks.")

        except Exception as e:
            print(f"   FAILED to read {file_path}. Error: {e}")

    print(f"\n--- Ingestion Complete! Added {total_chunks} new vectors to the bunker. ---")

if __name__ == "__main__":
    # 1. Grab the list of files from your target directory
    #my_files = get_target_files("./", extensions=['.md', '.txt', '.log', ''])
    my_files = get_files_according_to_gitignore("./")

    # 2. Shove them into the vector matrix
    vectorize_files(my_files)
