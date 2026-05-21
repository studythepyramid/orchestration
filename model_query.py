import json
import re
import time
import urllib.request

from settings import OLLAMA_BASE_URL


def get_model_context_size(model_name: str) -> int:
    """
    Queries the local Ollama daemon on the fly to fetch the native
    maximum context length (context_length) of a specific model.
    """
    url = f"{OLLAMA_BASE_URL}/api/show"
    data = json.dumps({"model": model_name}).encode("utf-8")

    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode("utf-8"))

            # 1) Check for runtime num_ctx override in 'parameters'
            params_str = res.get("parameters", "")
            m = re.search(r"num_ctx\s+(\d+)", params_str)
            if m:
                return int(m.group(1))

            # 2) Fallback: native context_length from model_info
            model_info = res.get("model_info", {})
            for key, value in model_info.items():
                if key.endswith(".context_length"):
                    return int(value)

            return 2048
    except Exception:
        return 2048  # Default safe boundary if Ollama is unreachable


ollama_list = """
gemma4:e2b
gemma4:e4b
all-minilm:latest
nomic-embed-text:latest
phi4-mini:3.8b
chat-apr-22-gemma:latest
qwen2.5:14b
qwen2.5:latest
codellama:latest
qwen2.5-coder:7b
deepseek-coder:6.7b
llama3.2:latest
gemma3:1b
gemma3:4b
"""


def list_model_context_size(model_names: str):
    """
    # Task 2: Query each model in ollama_list, print, and write to context-size.txt
    """

    print("Querying context size for all models in model_names...")

    output_lines = []

    # Split the model_names, strip whitespace, and filter out empty lines
    models_to_process = [
        model.strip() for model in model_names.strip().split() if model.strip()
    ]

    for i, model_name in enumerate(models_to_process):
        print(f"Querying: {model_name}")
        context_size = get_model_context_size(model_name)
        output_lines.append(f"{model_name}: {context_size}")
        print(f"{model_name}  -> {context_size}")

        # Add a delay between queries, except for the last one
        if i < len(models_to_process) - 1:
            print("Waiting 2 minutes before next query...")

        # time.sleep(120) # 120 seconds, 2 minutes
        time.sleep(1)

    # Write results to context-size.txt
    try:
        with open("context-size.txt", "w+") as f:
            for line in output_lines:
                f.write(line + "\n")
        print(" Results written to context-size.txt")
    except Exception as e:
        print(f" Error writing to context-size.txt: {e}")


def test_query_one_model(model_name: str):
    context_size = get_model_context_size(model_name)
    print(f"Context size for {model_name}: {context_size}")
    print()


if __name__ == "__main__":
    # test 1
    model_name = "gemma3:1b"
    # model_name = "gemma3:4b"
    # test_query_one_model(model_name=model_name)

    list_model_context_size(ollama_list)

    """
    # interactive test
    local_model_names = [
        model.strip() for model in ollama_list.strip().split() if model.strip()
    ]

    url = f"{OLLAMA_BASE_URL}/api/show"
    data = json.dumps({"model": model_name}).encode("utf-8")

    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}
    )
    response = urllib.request.urlopen(req)
    dec_res = json.loads(response.read().decode("utf-8"))
    """
