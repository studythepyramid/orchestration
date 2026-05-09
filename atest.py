from langchain.chat_models import init_chat_model

# Initialize the local Ollama engine
model = init_chat_model(
    model="gemma3:4b",
    model_provider="ollama",
    base_url="http://127.0.0.1:11434" # Explicitly point to your local port
)

result = model.invoke("Hello, could people know AS is android studio?")
print(result.content)
