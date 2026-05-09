
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain_ollama import OllamaLLM

#from langchain.chains import RetrievalQA
#from langchain_community.chains import RetrievalQA

# 1. Load your local 'claws' (The Checklist)
loader = TextLoader("./checklist.md")
documents = loader.load()

# 2. Split text into bite-sized 'LEGO' pieces
text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
texts = text_splitter.split_documents(documents)

# 3. Create a local Vector Store (Reading Notes)
# This uses a tiny local model to 'embed' text into math vectors
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = Chroma.from_documents(documents=texts, embedding=embeddings)

# 4. Connect the Brain
llm = OllamaLLM(model="gemma3:4b", base_url="http://127.0.0.1:11434")

from langchain_core.runnables import RunnablePassthrough

# The modern way to build your SOS Helper
retriever = vectorstore.as_retriever()

# prompt need it's define
# from langchain_core.prompts import PromptTemplate ...
rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# Run it!
print(rag_chain.invoke("What are the current stages in the SOS project?"))
