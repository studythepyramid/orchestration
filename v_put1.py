import os
from typing import List
from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
# from v_filelist import get_target_files # Assuming you have this locally

DB_DIR = "./nomic-v-bunker"

def get_bunker_db() -> Chroma:
    """Boot up the connection to the existing memory banks."""
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    return Chroma(persist_directory=DB_DIR, embedding_function=embeddings)


def vectorize_one_file(file_path: str,
                       vectorstore: Chroma,
                       text_splitter: CharacterTextSplitter) -> int:
    """Processes a single file, chunks it, and adds it to the vector store."""
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

    print(f"\n--- Booting up {DB_DIR} for INGESTION ---")
    vectorstore = get_bunker_db()
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)

    total_chunks = 0

    for file_path in file_list:
        chunks_processed = vectorize_one_file(file_path, vectorstore, text_splitter)
        total_chunks += chunks_processed

    print(f"\n--- Ingestion Complete! Matrix stabilized with {total_chunks} chunks. ---")


def double_chop(filepath: str) -> List[Document]:
    """
    Reads a markdown file and performs a two-stage chopping pipeline:
    1. MarkdownHeaderTextSplitter isolates logical sections (Tmux events).
    2. RecursiveCharacterTextSplitter ensures chunks are within LLM token limits.
    """
    if not os.path.exists(filepath):
        print(f"[-] Staging file {filepath} not found.")
        return []

    # Load the raw text directly
    with open(filepath, 'r', encoding='utf-8') as f:
        raw_text = f.read()

    print(f"-> Initiating Double Chop on: {filepath}")

    # --- First Pass: Isolate the Tmux Events and grab the Header metadata ---
    headers_to_split_on = [("##", "Event_ID")]
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    md_header_splits = markdown_splitter.split_text(raw_text)

    # THE METADATA HACK: Manually inject the source file path!
    for doc in md_header_splits:
        doc.metadata['source'] = filepath

    # --- Second Pass: The Safety Net (Recursive Splitter) ---
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=3000,
        chunk_overlap=300
    )

    # final_splits will automatically inherit the 'source' and 'Event_ID' we just made!
    final_splits = text_splitter.split_documents(md_header_splits)

    print(f"   [✓] Found {len(md_header_splits)} Terminal Events.")
    print(f"   [✓] Chopped into {len(final_splits)} safe, embeddable chunks.")

    return final_splits


def vectorize_terminal_history(file_path: str):
    """Orchestrates the ingestion of terminal history using double_chop."""
    print(f"\n--- Booting up {DB_DIR} for Terminal Ingestion ---")

    # Call our new refactored function
    final_splits = double_chop(file_path)

    if not final_splits:
        print("[-] No chunks generated. Aborting ingestion.")
        return

    vectorstore = get_bunker_db()

    # Generate strict IDs for the final chunks
    base_filename = os.path.basename(file_path)
    chunk_ids = [f"{base_filename}_chunk_{i}" for i in range(len(final_splits))]

    # Assimilate!
    try:
        vectorstore.add_documents(documents=final_splits, ids=chunk_ids)
        print(f"   [+] Success: {len(final_splits)} chunks locked into memory.")
    except Exception as e:
        print(f"   [-] FAILED to ingest. Error: {e}")


STAGE_FILE = "/tmp/olddog.terminal.md"

if __name__ == "__main__":
    print("\n--- name main. ---")

    # import v_filelist as vflist
    # db = get_bunker_db()
    # split500 = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    # my_files = vflist.get_files_according_to_gitignore("/my/tec/")
    # vectorize_files(my_files)

    #vectorize_terminal_history(STAGE_FILE)
    chunks = double_chop(STAGE_FILE)
