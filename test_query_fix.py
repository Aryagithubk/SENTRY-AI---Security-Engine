import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from backend.agents.alert_agent import AlertAgent

agent = AlertAgent()

queries = [
    "Show me all critical security alerts",
    "Find alerts related to ransomware",
    "List high severity alerts in the last 24 hours",
    "Search SIEM events for brute force"
]

for q in queries:
    res = agent.execute(q)
    print("=" * 60)
    print(f"QUERY: {q}")
    print(f"COUNT: {len(res['data'])}")
    for a in res['data']:
        print(f"  - [{a['severity']}] {a['alert_id']}: {a['title']}")
