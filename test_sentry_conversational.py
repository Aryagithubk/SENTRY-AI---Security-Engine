import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from backend.workflows.graph import SecureOpsGraph

graph = SecureOpsGraph(provider="mock")

test_queries = [
    "hi",
    "who are you and what can you do?",
    "what is the capital of France?",
    "you are total shit",
    "bye",
    "Show me all critical security alerts",
    "Check login history for johndoe@securetech.com"
]

for q in test_queries:
    print("=" * 60)
    print(f"QUERY: {q}")
    res = graph.process_query(q)
    print(f"TARGET AGENT: {res.get('target_agent')}")
    safe_resp = res.get('response', '').encode("ascii", errors="ignore").decode("ascii")
    print(f"RESPONSE:\n{safe_resp[:300]}...\n")
