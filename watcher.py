import sys
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 1. Catch the arguments from the Bash script
if len(sys.argv) < 3:
    print("Error: Missing context or question.")
    sys.exit(1)

question = sys.argv[1]
terminal_context = sys.argv[2]

# 2. Connect the Brain
llm = OllamaLLM(model="gemma3:4b", base_url="http://127.0.0.1:11434")

# 3. Define the AI Terminal Prompt
template = """You are an expert Linux Systems and Rust/Python Developer.
The user needs help debugging their terminal.

Here is the exact mirror of their current terminal screen:
<terminal_screen>
{context}
</terminal_screen>

The user asks: {question}

Provide a concise, highly technical answer. If there is a command to fix the issue, provide it clearly."""

prompt = ChatPromptTemplate.from_template(template)

# 4. The LCEL Pipe
chain = prompt | llm | StrOutputParser()

# 5. Run it!
print("\n--- 🤖 Gemma Analysis ---")
print(chain.invoke({"context": terminal_context, "question": question}))
