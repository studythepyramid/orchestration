from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import chain
import textwrap

# 1. Define the LLM globally so all functions can use it
llm = OllamaLLM(model="gemma3:4b", base_url="http://127.0.0.1:11434")

def aa():
    print("--- Raw Call ---")
    print(llm.invoke("In one sentence, what is agentic programming?"))

# 2. Fix the custom pipe to RETURN the text
@chain
def easy_read_old(text, w=80):
    wrapped_text = textwrap.fill(text, width=w)
    print(wrapped_text)
    return wrapped_text # Pass it down the chain!

def bb():
    print("\n--- Template Call ---")
    template = """You are a senior Rust and Python developer.
    Explain the following concept to a beginner using a simple analogy: {concept}"""

    prompt = PromptTemplate.from_template(template)
    
    # 3. Added the parentheses to StrOutputParser()
    my_chain = prompt | llm | StrOutputParser() | easy_read

    my_chain.invoke({"concept": "the pipeline in LangChain expression language"})


@chain
def easy_read(text, w=80):
    # Split the text by double newlines (paragraphs)
    paragraphs = text.split('\n\n')
    
    wrapped_paragraphs = []
    for p in paragraphs:
        # Wrap each paragraph individually, preserving line breaks
        wrapped_p = textwrap.fill(p, width=w, replace_whitespace=False)
        wrapped_paragraphs.append(wrapped_p)
    
    # Rejoin them with a double newline
    final_text = '\n\n'.join(wrapped_paragraphs)
    
    print(final_text)
    return final_text

# 4. The Trigger: Tell Python to actually run bb() when you execute the file!
if __name__ == "__main__":
    bb()
