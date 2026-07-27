import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from backend.services.llm import get_llm

print("Testing get_llm('ollama')...")
try:
    llm = get_llm("ollama")
    print(f"LLM Initialized: {llm}")
    res = llm.invoke("Hello Llama, confirm you are connected to SecureOps AI.")
    print("Ollama Live Response:")
    print(res.content)
except Exception as e:
    print(f"Error testing Ollama: {e}")
