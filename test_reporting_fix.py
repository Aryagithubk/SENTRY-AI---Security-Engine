import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from backend.agents.reporting_agent import ReportingAgent

agent = ReportingAgent()

queries = [
    "Generate executive report for incident INC-2026-001",
    "Prepare executive summary for user johndoe@securetech.com",
    "Generate investigation report for host WS-FINANCE-04"
]

for q in queries:
    res = agent.execute(q)
    print("=" * 60)
    print(f"QUERY: {q}")
    # Print target user and host extracted in report text
    text = res["response"].encode("ascii", errors="ignore").decode("ascii")
    print(text[:400])
