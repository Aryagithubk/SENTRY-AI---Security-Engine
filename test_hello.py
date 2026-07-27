import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from backend.workflows.graph import SecureOpsGraph

for prov in ["mock", "ollama"]:
    print("=" * 60)
    print(f"TESTING PROVIDER: {prov}")
    graph = SecureOpsGraph(provider=prov)
    res = graph.process_query("hello")
    print(f"TARGET AGENT: {res.get('target_agent')}")
    safe_resp = res.get("response", "").encode("ascii", errors="ignore").decode("ascii")
    print(f"RESPONSE:\n{safe_resp[:300]}")
