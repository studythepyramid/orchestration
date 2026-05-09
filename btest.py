
from langchain_ollama import ChatOllama

# Create the dedicated Ollama client
model = ChatOllama(
    model="gemma3:4b",
    base_url="http://127.0.0.1:11434",
    temperature=0.7 # You get direct access to model parameters here!
)

result = model.invoke("""""as a programmer, 
    explain list and iterator in python programming.""")

from langchain_ollama import ChatOllama

# Create the dedicated Ollama client
model = ChatOllama(
    model="gemma3:4b",
    base_url="http://127.0.0.1:11434",
    temperature=0.7 # You get direct access to model parameters here!
)

result = model.invoke("""""as a programmer, 
    explain list and iterator in python programming.""")
print(result.content)
print(result.content)
