
import requests

def wiki_bunker_search(query: str, lang="en"):
    session = requests.Session()
    URL = f"https://{lang}.wikipedia.org/w/api.php"

    # Step 1: Search for the most relevant page title
    search_params = {
        "action": "opensearch",
        "search": query,
        "limit": "1",
        "namespace": "0",
        "format": "json"
    }
    
    try:
        search_res = session.get(url=URL, params=search_params, timeout=10).json()
        if not search_res[1]:
            return "No Wikipedia article found."
        
        page_title = search_res[1][0]
        
        # Step 2: Fetch the plain-text content (the "Extract")
        content_params = {
            "action": "query",
            "format": "json",
            "titles": page_title,
            "prop": "extracts",
            "explaintext": True, # Get plain text, not HTML
            "exintro": True,    # Get only the summary (intro) to save context tokens
        }
        
        content_res = session.get(url=URL, params=content_params, timeout=10).json()
        pages = content_res["query"]["pages"]
        page_id = next(iter(pages))
        
        return pages[page_id].get("extract", "Content missing.")

    except Exception as e:
        return f"Wiki Error: {str(e)}"

if __name__ == "__main__":
    import sys
    q = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Large Language Model"
    print(f"--- Wiki Context for: {q} ---\n")
    print(wiki_bunker_search(q))
