import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from backend.agents.reporting_agent import ReportingAgent

agent = ReportingAgent()

new_queries = [
    "Prepare executive summary for user cloud.admin@securetech.com",
    "Generate investigation report for host LAPTOP-DEV-88",
    "Prepare summary report for new user admin.alex@securetech.com"
]

for q in new_queries:
    res = agent.execute(q)
    print("=" * 60)
    print(f"QUERY: {q}")
    text = res["response"].encode("ascii", errors="ignore").decode("ascii")
    print(text[:400])
