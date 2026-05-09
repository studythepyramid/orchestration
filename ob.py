

from ollama import chat

stream = chat(
        model='gemma3:1b',
        messages=[{'role': 'user', 
                   'content': 'how to compile c program on Linux? show me the hello world example.'}],
        stream=True,
        )

for chunk in stream:
    print(chunk['message']['content'], end='', flush=True)

