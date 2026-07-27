import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from backend.agents.reporting_agent import ReportingAgent
from backend.agents.identity_agent import IdentityAgent
from backend.agents.endpoint_agent import EndpointAgent

rep_agent = ReportingAgent()
id_agent = IdentityAgent()
ep_agent = EndpointAgent()

test_cases = [
    ("IDENTITY", id_agent, "Check login history for unknown.user@enterprise.org"),
    ("ENDPOINT", ep_agent, "Inspect endpoint status for HOST-UNKNOWN-99"),
    ("REPORTING USER", rep_agent, "Generate executive report for user unknown.user@enterprise.org"),
    ("REPORTING INCIDENT", rep_agent, "Generate executive report for incident INC-2026-999")
]

for label, agent, q in test_cases:
    print("=" * 60)
    print(f"[{label}] QUERY: {q}")
    res = agent.execute(q)
    print(res["response"].encode("ascii", errors="ignore").decode("ascii"))
