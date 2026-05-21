
def add_man_to_db(collection, cmd_name: str, raw_text: str):
    """Indexes chunks while strictly locking them to a metadata tag."""
    paragraphs = [p.strip() for p in raw_text.split("\n\n") if p.strip()]
    
    documents = []
    metadatas = []
    ids = []
    
    for idx, para in enumerate(paragraphs):
        documents.append(para)
        # CRITICAL: Tag every single paragraph with its command owner
        metadatas.append({"command": cmd_name, "chunk_id": idx})
        ids.append(f"{cmd_name}_ch_{idx}")
        
    collection.add(documents=documents, metadatas=metadatas, ids=ids)

def query_man_from_db(collection, cmd_name: str, user_query: str):
    """Forces the database to scan ONLY chunks matching our current command context."""
    results = collection.query(
        query_texts=[user_query],
        n_results=4,
        # THIS IS THE FIX: The database instantly ignores all other man pages
        where={"command": cmd_name} 
    )
    return "\n\n---\n\n".join(results["documents"][0])
