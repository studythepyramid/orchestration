import os
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# 1. Setup paths
DB_DIR = "./sos_project_db"
FILE_PATH = "./checklist.md"

# 2. Initialize Embeddings (The math brain)
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# 3. Persistence Logic: Load or Create the Vector Store
if os.path.exists(DB_DIR):
    print(f"--- Loading existing memory from {DB_DIR} ---")
    vectorstore = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
else:
    print(f"--- First run: Indexing {FILE_PATH} ---")
    loader = TextLoader(FILE_PATH)
    documents = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    texts = text_splitter.split_documents(documents)
    vectorstore = Chroma.from_documents(
        documents=texts,
        embedding=embeddings,
        persist_directory=DB_DIR
    )

retriever = vectorstore.as_retriever()

# 4. Connect to local Gemma
llm = OllamaLLM(model="gemma3:4b", base_url="http://127.0.0.1:11434")

# 5. Define the Prompt
template = """You are an SOS Project Assistant. Use the context to answer the question.
Context:
{context}

Question:
{question}

Answer:"""
prompt = ChatPromptTemplate.from_template(template)

# 6. The LCEL Pipe
pipe_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# 7. Run the Query
print("\n--- SOS Project Helper Output ---")
print(pipe_chain.invoke("What are the main network techniques for the SOS project?"))
