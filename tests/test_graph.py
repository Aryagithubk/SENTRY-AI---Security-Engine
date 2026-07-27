import pytest
from backend.workflows.graph import SecureOpsGraph

def test_graph_conversational_flow():
    graph = SecureOpsGraph(provider="mock")
    res = graph.process_query("hi")
    assert res["status"] == "SUCCESS"
    assert res["target_agent"] == "Conversational Agent"
    assert "SENTRY" in res["response"]

def test_graph_alert_flow():
    graph = SecureOpsGraph(provider="mock")
    res = graph.process_query("Show all critical alerts")
    assert res["status"] == "SUCCESS"
    assert res["target_agent"] == "Alert Agent"

def test_graph_incident_flow_rbac_blocked():
    graph = SecureOpsGraph(provider="mock")
    l1_auth = {"username": "analyst_l1", "role": "L1"}
    res = graph.process_query("Create security incident for WS-FINANCE-04", auth_context=l1_auth)
    assert res["status"] == "SUCCESS"
    assert "Permission Denied" in res["response"]

def test_graph_incident_flow_manager_hitl():
    graph = SecureOpsGraph(provider="mock")
    mgr_auth = {"username": "manager", "role": "MANAGER"}
    res = graph.process_query("Create security incident for WS-FINANCE-04", auth_context=mgr_auth, hitl_approved=False)
    assert res["status"] == "HITL_REQUIRED"

    res_approved = graph.process_query("Create security incident for WS-FINANCE-04", auth_context=mgr_auth, hitl_approved=True)
    assert res_approved["status"] == "SUCCESS"
    assert "INC-2026-" in res_approved["response"]

def test_graph_correlation_flow():
    graph = SecureOpsGraph(provider="mock")
    l2_auth = {"username": "analyst_l2", "role": "L2"}
    res = graph.process_query("Correlate malware and suspicious network activity for WS-FINANCE-04", auth_context=l2_auth)
    assert res["status"] == "SUCCESS"
    assert "Threat Correlation Agent" in res["target_agent"]
    assert "Multi-Vector Threat Correlation" in res["response"]
    assert all(step["agent"] != "Reporting Agent" for step in res["execution_trace"])

def test_graph_correlation_rbac_denial_is_terminal():
    graph = SecureOpsGraph(provider="mock")
    l1_auth = {"username": "analyst_l1", "role": "L1"}

    res = graph.process_query("Perform threat hunting for user johndoe@securetech.com", auth_context=l1_auth)

    assert res["status"] == "SUCCESS"
    assert "Permission Denied" in res["response"]
    assert all(step["agent"] not in {"Risk Findings Node", "Reporting Agent"} for step in res["execution_trace"])
