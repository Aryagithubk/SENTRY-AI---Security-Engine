import pytest
from backend.agents.supervisor import SupervisorAgent
from backend.agents.conversational_agent import ConversationalAgent
from backend.agents.alert_agent import AlertAgent
from backend.agents.identity_agent import IdentityAgent
from backend.agents.endpoint_agent import EndpointAgent
from backend.agents.incident_agent import IncidentAgent
from backend.agents.reporting_agent import ReportingAgent
from backend.workflows.graph import SecureOpsGraph

def test_supervisor_routing():
    supervisor = SupervisorAgent(provider="mock")
    agent, _ = supervisor.route("Show all critical alerts")
    assert agent == "Alert Agent"

    agent, _ = supervisor.route("Check login history for johndoe@securetech.com")
    assert agent == "Identity Agent"

    agent, _ = supervisor.route("Inspect endpoint status for WS-FINANCE-04")
    assert agent == "Endpoint Agent"

    agent, _ = supervisor.route("Generate executive report for INC-2026-001")
    assert agent == "Reporting Agent"

    agent, _ = supervisor.route("hi")
    assert agent == "Conversational Agent"

def test_conversational_agent():
    c_agent = ConversationalAgent(provider="mock")
    res = c_agent.execute("hi")
    assert "SENTRY" in res["response"]

    res_guardrail = c_agent.execute("you are total shit")
    assert "PROFANITY_TRIGGERED" in res_guardrail["data"].get("guardrail", "")

def test_alert_agent():
    alert_agent = AlertAgent()
    res = alert_agent.execute("Show critical alerts")
    assert "data" in res
    assert len(res["data"]) >= 0

def test_identity_agent():
    id_agent = IdentityAgent()
    res = id_agent.execute("Check user johndoe@securetech.com")
    assert "data" in res
    assert "user" in res["data"] or "found" in res["data"]

def test_endpoint_agent():
    ep_agent = EndpointAgent()
    res = ep_agent.execute("Check host WS-FINANCE-04")
    assert "data" in res

def test_incident_agent_hitl():
    inc_agent = IncidentAgent()
    mgr_auth = {"username": "manager", "role": "MANAGER"}
    res_unapproved = inc_agent.execute("Create security incident for WS-FINANCE-04", approved=False, auth_context=mgr_auth)
    assert res_unapproved.get("requires_hitl") is True

    res_approved = inc_agent.execute("Create security incident for WS-FINANCE-04", approved=True, auth_context=mgr_auth)
    assert res_approved.get("requires_hitl") is False
    assert "INC-2026-" in res_approved["response"]

def test_full_graph_execution():
    graph = SecureOpsGraph(provider="mock")
    res = graph.process_query("Generate executive report for INC-2026-001")
    assert res["status"] == "SUCCESS"
    assert "execution_trace" in res
    assert len(res["execution_trace"]) >= 3
