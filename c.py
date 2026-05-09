
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate

from langchain_core.output_parsers import StrOutputParser

from langchain_core.runnables import chain

import textwrap

def aa():
    # 1. Connect to your local brain (The no_proxy variable in your bashrc protects this!)
    llm = OllamaLLM(model="gemma3:4b", base_url="http://127.0.0.1:11434")

    # 2. Test a raw API call
    print("--- Raw Call ---")
    print(llm.invoke("In one sentence, what is agentic programming?"))


@chain
def easy_read(text, w=80):
    print(textwrap.fill(text, width=w))

# The Agentic Preview: Prompt Templates
def bb():
    print("\n--- Template Call ---")
    template = """You are a senior Rust and Python developer.
    Explain the following concept to a beginner using a simple analogy: {concept}"""

    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm | StrOutputParser | easy_read

    chain.invoke({"concept": "the pipeline in LangChain expression language"})


