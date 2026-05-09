
import langchain

from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate

from langchain_core.output_parsers import StrOutputParser

Model="gemma3:4b" 
Base_url="http://127.0.0.1:11434"


import textwrap

long_text = """This is a very long sentence 
that needs to be wrapped at a specific width for 
better readability in the terminal."""

#print(textwrap.fill(long_text, width=40))


print("often used")

from langchain_core.runnables import chain

@chain
def easy_read(text, w=80):
    print(textwrap.fill(text, width=w))
