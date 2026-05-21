DB_DIR = "./nomic-v-bunker"  # keep for history
# embeddings = OllamaEmbeddings(model="nomic-embed-text")
# return Chroma(persist_directory=DB_DIR, embedding_function=embeddings)

VECTOR_DB_NAME = "nomic-v-bunker"
VECTOR_MODEL = "nomic-embed-text"

TMP_TERMINAL_LOG = "/tmp/olddog.terminal.md"

OLLAMA_BASE_URL = "http://127.0.0.1:11434"

func_dict = {
    "get_history.py": "get history of terminal.",
    "host_context.py": "get machine info",
    "v_filelist": "find file for later chopping",
    "v_put1.py": "put file content to Chroma",
    "...": "...",
    "hi.py": "summarize man page",
}


dir_snapshot = """
autofix.py  :  the initial auto fix the network approache
btest.py : langchain?
ddgs.agent.py : ?
e.py
f.py
g.py
get_history.py
h.py
host_context.py
i.py
ipy-saved.py
is_text.py
la.py
lc1.py
main.py
network_scan.py
nscan.py
oa.py
ob.py
oc.py
searxng.agent.py
settings.py
v.nomic.py
v.put.py
v.put1.py
v.query.py
v_filelist.py
v_put1.py
v_query.py
watcher.py
"""
