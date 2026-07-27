import re
from typing import Dict, Any, List, Optional
from uuid import uuid4

from langgraph.graph import END, START, StateGraph

from backend.workflows.state import SecureOpsState
from backend.agents.supervisor import SupervisorAgent
from backend.agents.conversational_agent import ConversationalAgent
from backend.agents.alert_agent import AlertAgent
from backend.agents.identity_agent import IdentityAgent
from backend.agents.endpoint_agent import EndpointAgent
from backend.agents.incident_agent import IncidentAgent
from backend.agents.reporting_agent import ReportingAgent
from backend.agents.correlation_agent import CorrelationAgent
from backend.workflows.human_loop import HumanInTheLoopController
from backend.services.audit_service import AuditService
from backend.services.rbac_service import RBACService
from backend.utils.intent_classifier import AlgorithmicIntentClassifier
from backend.utils.logger import log_stage

class SecureOpsGraph:
    """
    LangGraph implementation of the SENTRY investigation lifecycle.

    The graph follows the supplied SOC flow: preprocess -> supervisor ->
    specialist/tool -> state update -> re-evaluation -> optional correlation
    -> risk/action/HITL -> reporting -> evidence-bound synthesis -> audit.
    It records explainable routing decisions and evidence metadata, but never
    exposes private model reasoning.
    """

    def __init__(self, provider: str = None):
        self.provider = provider
        self.supervisor = SupervisorAgent(provider=provider)
        self.conversational_agent = ConversationalAgent(provider=provider)
        self.alert_agent = AlertAgent()
        self.identity_agent = IdentityAgent()
        self.endpoint_agent = EndpointAgent()
        self.incident_agent = IncidentAgent()
        self.reporting_agent = ReportingAgent(provider=provider)
        self.correlation_agent = CorrelationAgent()
        self.hitl_controller = HumanInTheLoopController()
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(SecureOpsState)
        workflow.add_node("preprocess", self._preprocess)
        workflow.add_node("orchestrator", self._orchestrate)
        workflow.add_node("conversational", self._run_conversational)
        workflow.add_node("alert", self._run_alert)
        workflow.add_node("identity", self._run_identity)
        workflow.add_node("endpoint", self._run_endpoint)
        workflow.add_node("incident", self._run_incident)
        workflow.add_node("correlation", self._run_correlation)
        workflow.add_node("reporting", self._run_reporting)
        workflow.add_node("report_generation", self._run_reporting)
        workflow.add_node("update_state", self._update_state)
        workflow.add_node("reevaluate", self._reevaluate)
        workflow.add_node("risk_findings", self._risk_findings)
        workflow.add_node("human_review", self._human_review)
        workflow.add_node("final_synthesis", self._final_synthesis)
        workflow.add_node("audit_log", self._audit_log)

        workflow.add_edge(START, "preprocess")
        workflow.add_edge("preprocess", "orchestrator")
        workflow.add_conditional_edges("orchestrator", self._worker_route, {
            "conversational": "conversational", "alert": "alert", "identity": "identity",
            "endpoint": "endpoint", "incident": "incident", "correlation": "correlation",
            "reporting": "reporting",
        })
        for worker in ("conversational", "alert", "identity", "endpoint", "incident", "correlation", "reporting"):
            workflow.add_edge(worker, "update_state")
        workflow.add_edge("update_state", "reevaluate")
        workflow.add_conditional_edges("reevaluate", self._re_evaluation_route, {
            "correlation": "correlation", "risk": "risk_findings", "human_review": "human_review",
            "reporting": "reporting", "synthesis": "final_synthesis",
        })
        # `reporting` is a primary worker and therefore returns through state
        # update/re-evaluation.  A correlation workflow uses this separate
        # terminal report node to avoid concurrent graph writes.
        workflow.add_conditional_edges("risk_findings", self._risk_route, {
            "reporting": "report_generation",
            "synthesis": "final_synthesis",
        })
        workflow.add_edge("human_review", "final_synthesis")
        workflow.add_edge("report_generation", "final_synthesis")
        workflow.add_edge("final_synthesis", "audit_log")
        workflow.add_edge("audit_log", END)
        return workflow.compile()

    @staticmethod
    def _trace(state: SecureOpsState, title: str, agent: str, **details: Any) -> List[Dict[str, Any]]:
        entry = {
            "stage_number": len(state.get("execution_trace", [])) + 1,
            "stage_title": title,
            "agent": agent,
            **details,
        }
        return [*state.get("execution_trace", []), entry]

    def _preprocess(self, state: SecureOpsState) -> Dict[str, Any]:
        query = state["query"]
        inferred_agent, _, intent_reason = AlgorithmicIntentClassifier.classify(query)
        report_requested = bool(re.search(r"\b(report|executive summary|ciso report)\b", query, re.IGNORECASE))
        required_evidence = {
            "Alert Agent": ["SIEM alerts"], "Identity Agent": ["identity and login telemetry"],
            "Endpoint Agent": ["EDR endpoint telemetry"], "Threat Correlation Agent": ["cross-domain telemetry"],
            "Incident Agent": ["incident request and authorization"], "Reporting Agent": ["investigation evidence"],
        }.get(inferred_agent, [])
        permissions = RBACService.get_permissions_for_role(state["role"])
        return {
            "intent": inferred_agent,
            "report_requested": report_requested,
            "required_evidence": required_evidence,
            "permissions": permissions,
            "investigation_context": {"intent_hint": inferred_agent, "intent_reason": intent_reason},
            "execution_trace": self._trace(state, "Stage 1: Preprocess & Understand Query", "Preprocess Node",
                                           reason=intent_reason),
        }

    def _orchestrate(self, state: SecureOpsState) -> Dict[str, Any]:
        agent, reason = self.supervisor.route(state["query"], auth_context=state["auth_context"],
                                              conversation_history=state.get("conversation_history", []))
        return {
            "active_agent": agent,
            "selected_agent": agent,
            "routing_reason": reason,
            "execution_trace": self._trace(state, "Stage 2: LLM Orchestrator / Supervisor", "Supervisor Agent",
                                           decision=agent, reason=reason),
        }

    @staticmethod
    def _worker_route(state: SecureOpsState) -> str:
        return {
            "Conversational Agent": "conversational", "Alert Agent": "alert", "Identity Agent": "identity",
            "Endpoint Agent": "endpoint", "Incident Agent": "incident", "Reporting Agent": "reporting",
            "Threat Correlation Agent": "correlation",
        }.get(state.get("active_agent"), "conversational")

    def _worker_result(self, state: SecureOpsState, output: Dict[str, Any], title: str) -> Dict[str, Any]:
        agent_name = output.get("agent", state.get("active_agent", "SENTRY Orchestrator"))
        return {
            "agent_outputs": {**state.get("agent_outputs", {}), agent_name: output},
            "active_agent": agent_name,
            "execution_trace": self._trace(state, title, agent_name, tool_calls=output.get("tool_calls", [])),
        }

    def _run_conversational(self, state: SecureOpsState) -> Dict[str, Any]:
        return self._worker_result(state, self.conversational_agent.execute(state["query"], state.get("conversation_history", [])), "Stage 3: Conversational Agent")

    def _run_alert(self, state: SecureOpsState) -> Dict[str, Any]:
        return self._worker_result(state, self.alert_agent.execute(state["query"]), "Stage 3: Alert Agent & SIEM Tools")

    def _run_identity(self, state: SecureOpsState) -> Dict[str, Any]:
        return self._worker_result(state, self.identity_agent.execute(state["query"]), "Stage 3: Identity Agent & IAM Tools")

    def _run_endpoint(self, state: SecureOpsState) -> Dict[str, Any]:
        return self._worker_result(state, self.endpoint_agent.execute(state["query"]), "Stage 3: Endpoint Agent & EDR Tools")

    def _run_incident(self, state: SecureOpsState) -> Dict[str, Any]:
        approved = state.get("hitl_status", {}).get("approved", False)
        return self._worker_result(state, self.incident_agent.execute(state["query"], approved=approved,
                                                                        auth_context=state["auth_context"]),
                                   "Stage 3: Incident Agent")

    def _run_correlation(self, state: SecureOpsState) -> Dict[str, Any]:
        return self._worker_result(state, self.correlation_agent.execute(state["query"], auth_context=state["auth_context"]),
                                   "Stage 4: Threat Correlation Agent")

    def _run_reporting(self, state: SecureOpsState) -> Dict[str, Any]:
        # A report is generated once per run. Other flows retain their primary response.
        if "Reporting Agent" in state.get("agent_outputs", {}):
            return {}
        return self._worker_result(state, self.reporting_agent.execute(state["query"]), "Stage 7: Reporting Agent")

    def _latest_output(self, state: SecureOpsState) -> Dict[str, Any]:
        return state.get("agent_outputs", {}).get(state.get("active_agent", ""), {})

    def _update_state(self, state: SecureOpsState) -> Dict[str, Any]:
        output = self._latest_output(state)
        tools = output.get("tool_calls", [])
        evidence = list(state.get("investigation_context", {}).get("evidence", []))
        evidence.extend({"agent": output.get("agent"), "tool": item.get("tool")} for item in tools)
        context = {**state.get("investigation_context", {}), "evidence": evidence, "latest_data": output.get("data")}
        return {
            "tool_outputs": [*state.get("tool_outputs", []), *tools],
            "investigation_context": context,
            "hitl_status": {**state.get("hitl_status", {}), "pending": bool(output.get("requires_hitl")),
                            "action_details": output.get("action_details")},
            "execution_trace": self._trace(state, "Stage 4: Update Graph State", "State Update Node",
                                           tool_calls=tools),
        }

    def _reevaluate(self, state: SecureOpsState) -> Dict[str, Any]:
        output = self._latest_output(state)
        active = state.get("active_agent", "")
        needs_correlation = state.get("intent") == "Threat Correlation Agent" and active != "Threat Correlation Agent"
        access_denied = isinstance(output.get("data"), dict) and output["data"].get("authorized") is False
        if output.get("requires_hitl"):
            next_step = "human_review"
            reason = "Sensitive action requires analyst authorization."
        elif access_denied:
            # RBAC denials are terminal. Never call another agent or LLM to
            # work around a denied action or produce a substitute answer.
            next_step = "synthesis"
            reason = "Request stopped because the current role is not authorized for this action."
        elif active == "Threat Correlation Agent":
            next_step = "risk"
            reason = "Correlation evidence is available for risk assessment."
        elif needs_correlation:
            next_step = "correlation"
            reason = "Cross-system evidence is required before findings are finalized."
        elif active == "Reporting Agent":
            next_step = "synthesis"
            reason = "Requested report already contains the available evidence."
        else:
            next_step = "synthesis"
            reason = "The requested evidence has been collected."
        return {"next_step": next_step, "requires_correlation": needs_correlation,
                "execution_trace": self._trace(state, "Stage 5: Orchestrator Re-evaluation", "Supervisor Agent",
                                                 decision=next_step, reason=reason)}

    @staticmethod
    def _re_evaluation_route(state: SecureOpsState) -> str:
        return state.get("next_step", "synthesis")

    def _risk_findings(self, state: SecureOpsState) -> Dict[str, Any]:
        output = self._latest_output(state)
        data = output.get("data", {})
        risk = {"level": data.get("risk_level", "UNKNOWN"), "confidence": data.get("confidence_pct"),
                "evidence_count": len(state.get("investigation_context", {}).get("evidence", []))} if isinstance(data, dict) else {}
        return {"risk_assessment": risk,
                "execution_trace": self._trace(state, "Stage 6: Risk / Findings", "Risk Findings Node",
                                                 reason="Risk is derived only from collected evidence.")}

    @staticmethod
    def _risk_route(state: SecureOpsState) -> str:
        """Generate a report only when the user explicitly requested one."""
        return "reporting" if state.get("report_requested", False) else "synthesis"

    def _human_review(self, state: SecureOpsState) -> Dict[str, Any]:
        output = self._latest_output(state)
        self.hitl_controller.request_approval(output.get("hitl_action", "SECURITY_ACTION"), output.get("action_details", {}))
        log_stage("HITL Interruption", "Action requires analyst confirmation", level="warning")
        return {"status": "HITL_REQUIRED",
                "execution_trace": self._trace(state, "Stage 6: Human-in-the-Loop Authorization", "Human-in-the-Loop Controller",
                                                 status="WAITING_FOR_ANALYST")}

    def _final_synthesis(self, state: SecureOpsState) -> Dict[str, Any]:
        primary_agent = state.get("active_agent", "")
        primary = self._latest_output(state)
        # Explicit reporting requests use the report. Other requests preserve the
        # original specialist answer while still retaining graph evidence.
        response = primary.get("response", "")
        return {"final_response": response, "status": state.get("status", "SUCCESS"),
                "execution_trace": self._trace(state, "Stage 8: Evidence-Based Final Synthesis", primary_agent,
                                                 reason="Response is limited to agent/tool evidence.")}

    def _audit_log(self, state: SecureOpsState) -> Dict[str, Any]:
        auth = state["auth_context"]
        event = AuditService.log_event(user_id=auth.get("username", "analyst_l1"), user_role=auth.get("role", "L1"),
                                       action="LANGGRAPH_INVESTIGATION", resource=state["query"][:80],
                                       investigation_id=state.get("investigation_id"), result=state.get("status", "SUCCESS"),
                                       details=f"Agents: {', '.join(state.get('agent_outputs', {}).keys())}")
        return {"audit_entries": [*state.get("audit_entries", []), event],
                "execution_trace": self._trace(state, "Stage 9: Compliance Audit Log", "Audit Log Node", status="COMPLETED")}

    def process_query(self, query: str, auth_context: Optional[Dict[str, Any]] = None,
                      hitl_approved: bool = False, conversation_history: Optional[List[Dict[str, Any]]] = None,
                      investigation_id: Optional[str] = None) -> Dict[str, Any]:
        user_auth = auth_context or {"username": "analyst_l1", "name": "Alex Mercer", "role": "L1", "role_display": "L1 SOC Analyst"}
        history = conversation_history or []
        contextual_query = self._apply_conversation_context(query, history)
        log_stage("Workflow Init", f"User: {user_auth.get('username')} ({user_auth.get('role')}) | Query: '{query}' | HITL Approved: {hitl_approved}")
        initial_state: SecureOpsState = {
            "query": contextual_query, "user_query": query, "auth_context": user_auth, "user": user_auth,
            "role": user_auth.get("role", "L1"), "conversation_history": history,
            "investigation_id": investigation_id or f"INV-{uuid4().hex[:8].upper()}", "messages": history,
            "agent_outputs": {}, "tool_outputs": [], "investigation_context": {}, "risk_assessment": {},
            "hitl_status": {"approved": hitl_approved}, "audit_entries": [], "errors": [], "execution_trace": [],
        }
        result = self.graph.invoke(initial_state)
        output = self._latest_output(result)
        log_stage("Workflow Completion", f"Workflow finished with status {result.get('status', 'SUCCESS')}")
        response = result.get("final_response") or output.get("response", "")
        return {
            "status": result.get("status", "SUCCESS"), "target_agent": result.get("selected_agent", output.get("agent", result.get("active_agent"))),
            "response": response, "data": output.get("data"), "action_details": output.get("action_details"),
            "execution_trace": result.get("execution_trace", []), "investigation_id": result.get("investigation_id"),
        }

    @staticmethod
    def _apply_conversation_context(query: str, history: List[Dict[str, Any]]) -> str:
        """Resolve a follow-up reference using the latest explicitly named entity."""
        lower_query = query.lower()
        has_entity = bool(re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}|\b(?:\d{1,3}\.){3}\d{1,3}\b|\b(?:WS|LAPTOP|SRV|HOST|DEV|PROD|PC|MAC|WIN)-[A-Za-z0-9-]+\b", query, re.I))
        refers_back = bool(re.search(r"\b(this|that|same|previous|it|them)\b", lower_query))
        if has_entity or not refers_back:
            return query
        for message in reversed(history):
            if message.get("role") != "user":
                continue
            match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}|\b(?:\d{1,3}\.){3}\d{1,3}\b|\b(?:WS|LAPTOP|SRV|HOST|DEV|PROD|PC|MAC|WIN)-[A-Za-z0-9-]+\b", message.get("content", ""), re.I)
            if match:
                return f"{query}\nPrior conversation entity: {match.group(0)}"
        return query
