# coding: utf-8
import  ollama
ollama.embed(model='gemma3:1b', input=['The sky is blue because of rayleigh scattering', 'Grass is green because of chlorophyll'])
ollama.embed(model='gemma3:1b', input=['The sky is blue because of rayleigh scattering', 'Grass is green because of chlorophyll'])
ollama.embed(model='gemma3:4b', input=['The sky is blue because of rayleigh scattering', 'Grass is green because of chlorophyll'])
ollama.list()
get_ipython().run_line_magic('ed', '')
get_ipython().run_line_magic('run', 'oc.py')
ollama.show("gemma3")
ollama.show("gemma3:4b")
import pprint as pp
ge4b = ollama.show("gemma3:4b")
get_ipython().run_line_magic('pprint', 'ge4b')
get_ipython().run_line_magic('pprint(', 'ge4b)')
get_ipython().run_line_magic('pprint', '')
ge4b
ge4b.model_dump_json()
pp.pprint(ge4b.model_dump_json())
type(ge4b)
ge4bjson = ollama.show("gemma3:4b").model_dump_json()
ge4bjson
ge4bjson = ollama.show("gemma3:4b").model_dump_json(indent=2)
print(ge4bjson)
ollama.embed(model='gemma3:1b', input='The sky is blue because of rayleigh scattering')
get_ipython().run_line_magic('ed', '')
response.embeddings[0][-5]
len(response.embeddings[0])
len(response.embeddings)
type(response.embeddings)
