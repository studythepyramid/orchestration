
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# 1. Load your local SOS Checklist
loader = TextLoader("./checklist.md")
documents = loader.load()

# 2. Split text into chunks
# We use a slightly smaller chunk for local model precision
text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
texts = text_splitter.split_documents(documents)

# 3. Local Vector Store (No cloud costs)
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = Chroma.from_documents(documents=texts, embedding=embeddings)
retriever = vectorstore.as_retriever()

# 4. Connect to local Gemma
llm = OllamaLLM(model="gemma3:4b", base_url="http://127.0.0.1:11434")

# 5. Define the Prompt (The missing 'NameError' fix)
template = """You are an SOS Project Assistant. Use the following pieces of retrieved
context to answer the user's question about the project status.
If you don't know the answer based on the context, just say that you don't know.

Context:
{context}

Question:
{question}

Answer:"""

prompt = ChatPromptTemplate.from_template(template)

# 6. The Modern LCEL Pipe
rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# 7. Run the Query
print("\n--- SOS Project Helper Output ---")
query = "What are the current stages in the SOS project?"
print(rag_chain.invoke(query))
