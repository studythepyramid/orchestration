import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
#from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from v_filelist import get_target_files

DB_DIR = "./nomic-v-bunker"

def get_bunker_db():
    """Boot up the connection to the existing memory banks."""
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    return Chroma(persist_directory=DB_DIR, embedding_function=embeddings)

def vectorize_one_file(file_path: str, 
                       vectorstore: Chroma, 
                       text_splitter: CharacterTextSplitter) -> int:
    """Processes a single file, chunks it, and adds it to the vector store.

    Args:
        file_path: The absolute path to the file.
        vectorstore: The initialized Chroma vector store instance.
        text_splitter: The initialized CharacterTextSplitter instance.

    Returns:
        The number of chunks processed for this file, or 0 if an error occurred.
    """
    print(f"-> Assimilating: {file_path}")
    try:
        # 1. Load the file
        loader = TextLoader(file_path)
        documents = loader.load()

        # 2. Chop it into AI-sized bites
        texts = text_splitter.split_documents(documents)

        # 3. Generate strict IDs based on the filename
        base_filename = os.path.basename(file_path)
        chunk_ids = [f"{base_filename}_chunk_{i}" for i in range(len(texts))]

        # 4. Add to the database using our strict IDs
        # If the ID already exists, Chroma gracefully updates it!
        vectorstore.add_documents(documents=texts, ids=chunk_ids)

        print(f"   Success: +{len(texts)} chunks updated/added.")
        return len(texts)

    except Exception as e:
        print(f"   FAILED to read {file_path}. Error: {e}")
        return 0






def vectorize_files(file_list: list[str]):
    """Takes a list of absolute paths, chunks them, and strictly UPDATES the DB."""
    if not file_list:
        print("No files provided. Aborting ingestion.")
        return

    print(f"""
--- Booting up {DB_DIR} for INGESTION ---""")
    vectorstore = get_bunker_db()
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)

    total_chunks = 0

    for file_path in file_list:
        chunks_processed = vectorize_one_file(file_path, vectorstore, text_splitter)
        total_chunks += chunks_processed

    print(f"""
--- Ingestion Complete! Matrix stabilized with {total_chunks} chunks. ---""")




STAGE_FILE = "/tmp/olddog.terminal.md"


def vectorize_terminal_history(file_path: str):
    if not os.path.exists(file_path):
        print(f"[-] Staging file {file_path} not found.")
        return

    print(f"\n--- Booting up {DB_DIR} for Terminal Ingestion ---")
    vectorstore = get_bunker_db()



    # hi gemi, should we used documents instead of raw_text aside, 
    #loader = TextLoader(file_path)
    #documents = loader.load()

    # --- THE TWO-STAGE CHOPPING PIPELINE ---
    # Load the raw text directly (No TextLoader needed!)
    with open(file_path, 'r', encoding='utf-8') as f:
        raw_text = f.read()

    # --- THE TWO-STAGE CHOPPING PIPELINE ---
    
    # First Pass: Isolate the Tmux Events and grab the Header metadata
    headers_to_split_on = [("##", "Event_ID")]
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    md_header_splits = markdown_splitter.split_text(raw_text)

    # THE METADATA HACK: Manually inject the source file path!
    # This completely solves the Semantic Search Trap we fought earlier.
    for doc in md_header_splits:
        doc.metadata['source'] = file_path

    #  Second Pass: The Safety Net (Recursive Splitter)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=3000, 
        chunk_overlap=300 
    )
    # final_splits will automatically inherit the 'source' and 'Event_ID' we just made!
    final_splits = text_splitter.split_documents(md_header_splits)

    print(f"-> Found {len(md_header_splits)} Terminal Events.")
    print(f"-> Chopped into {len(final_splits)} safe, embeddable chunks.")

    # Generate strict IDs for the final chunks
    base_filename = os.path.basename(file_path)
    chunk_ids = [f"{base_filename}_chunk_{i}" for i in range(len(final_splits))]

    # Assimilate!
    try:
        vectorstore.add_documents(documents=final_splits, ids=chunk_ids)
        print(f"   [+] Success: {len(final_splits)} chunks locked into memory.")
    except Exception as e:
        print(f"   [-] FAILED to ingest. Error: {e}")


# refactor, to have a function take care of double chop. 
def double_chop(filepath)
    """
    """
    ## chop with markdown, then 2 chop with text_splitter,
    ## make sure all result text in good size


if __name__ == "__main__":
    print(f"""
--- name main. ---""")
    #import v_filelist as vflist

    #db = get_bunker_db()
    #split500 = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    ##my_files = get_target_files("/my/tec/", extensions=['.md', '.txt', '.log', ''])
    #my_files = vflist.get_files_according_to_gitignore("/my/tec/")
    ##vectorize_files(my_files)
    vectorize_terminal_history(STAGE_FILE)
