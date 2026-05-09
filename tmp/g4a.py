
import requests
import json

def get_ai_response(user_card):
    """
    Sends the structured User_card to the local Gemma 4 model.
    """
    url = "http://localhost:11434/api/generate"

    # We craft a prompt that tells the AI to respect the Game Rules
    prompt = f"""
    [SYSTEM: Game of Turns - Strict Mode]
    User Intent: {user_card['intent']}
    User Input: {user_card['raw_input']}

    Rules:
    1. If intent is 'chat', provide a brief tactical suggestion.
    2. If intent is 'exec', acknowledge the manual override.
    3. Do not hallucinate code unless asked.
    """

    payload = {
        "model": "gemma4:e2b", # Or gemma4:e2b-it
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "No response from AI.")
        else:
            return f"[!] Error: Model returned status {response.status_code}"
    except Exception as e:
        return f"[!] Error connecting to Ollama: {str(e)}"
