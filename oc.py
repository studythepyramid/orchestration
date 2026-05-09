
import ollama

from pprint import pprint

# You can dump it to a dictionary first for cleaner formatting
pprint(ollama.list().model_dump())

# Let Pydantic do the heavy lifting
models = ollama.list()
print(models.model_dump_json(indent=2))

print(f"{'MODEL NAME':<30} | {'FAMILY':<10} | {'SIZE (GB)'}")
print("-" * 55)

for m in ollama.list().models:
    # Convert bytes to Gigabytes for readability
    size_gb = m.size / (1024**3)
    print(f"{m.model:<30} | {m.details.family:<10} | {size_gb:.2f} GB")
