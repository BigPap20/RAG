import os
from app.llm import LLM

llm = LLM(model='llama2')  # or another Ollama model
response = llm.chat("Your question here")
print(response)
