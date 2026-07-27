import sys
import json
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.workflows.graph import SecureOpsGraph

DATASET_PATH = Path(__file__).resolve().parent / "dataset.json"

def run_evaluation():
    """Execute evaluation benchmark dataset and print accuracy and latency metrics."""
    if not DATASET_PATH.exists():
        print(f"Error: Evaluation dataset {DATASET_PATH} not found.")
        return

    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        eval_cases = json.load(f)

    graph = SecureOpsGraph(provider="mock")
    
    total = len(eval_cases)
    passed = 0
    latencies = []

    print("=" * 75)
    print("SENTRY AI Evaluation Benchmark Suite (LangSmith & Agentic Multi-Agent)")
    print("=" * 75)
    print(f"{'ID':<10} | {'Category':<22} | {'Target Agent':<25} | {'Latency':<8} | {'Status'}")
    print("-" * 75)

    for case in eval_cases:
        cid = case["id"]
        cat = case["category"]
        q = case["query"]
        expected_agent = case["expected_agent"]
        test_role = case.get("test_role", "MANAGER" if "Create" in q else "L1")

        auth_context = {
            "username": f"user_{test_role.lower()}",
            "role": test_role,
            "role_display": f"{test_role} Analyst"
        }

        start_time = time.time()
        res = graph.process_query(q, auth_context=auth_context)
        latency = (time.time() - start_time) * 1000.0
        latencies.append(latency)

        actual_agent = res.get("target_agent", "")
        response_text = res.get("response", "")

        # Verify agent routing and keyword checks
        agent_match = expected_agent in actual_agent or actual_agent in expected_agent
        keyword_match = any(kw.lower() in response_text.lower() for kw in case["expected_keywords"])

        if agent_match and keyword_match:
            status = "PASS"
            passed += 1
        else:
            status = "FAIL"

        print(f"{cid:<10} | {cat:<22} | {actual_agent[:24]:<25} | {latency:6.1f}ms | {status}")

    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    accuracy = (passed / total) * 100.0

    print("=" * 75)
    print(f"SUMMARY: Passed {passed}/{total} ({accuracy:.1f}%) | Avg Latency: {avg_latency:.1f}ms")
    print("=" * 75)

if __name__ == "__main__":
    run_evaluation()
