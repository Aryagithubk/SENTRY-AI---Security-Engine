from typing import Dict, Any, List, Optional
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
from backend.utils.logger import log_stage

class SecureOpsGraph:
    """
    Multi-agent state graph orchestrator for SENTRY (Security Engine for Next-generation Triage, Recommendations & Yield).
    Flow: User Query -> Auth Context -> Supervisor Agent -> Worker Agents -> HITL Safeguard -> Audit Log -> Response
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

    def process_query(self, query: str, auth_context: Optional[Dict[str, Any]] = None, hitl_approved: bool = False) -> Dict[str, Any]:
        execution_trace = []
        user_auth = auth_context or {"username": "analyst_l1", "name": "Alex Mercer", "role": "L1", "role_display": "L1 SOC Analyst"}
        
        log_stage("Workflow Init", f"User: {user_auth.get('username')} ({user_auth.get('role')}) | Query: '{query}' | HITL Approved: {hitl_approved}")

        # Stage 1: Supervisor Agent Routing
        target_agent_name, routing_reason = self.supervisor.route(query, auth_context=user_auth)
        execution_trace.append({
            "stage_number": 1,
            "stage_title": "Stage 1: Intent Routing & Permission Check",
            "agent": "Supervisor Agent",
            "decision": target_agent_name,
            "reason": routing_reason
        })

        # Stage 2: Route to specialized worker agent with auth context
        worker_output = {}
        log_stage("Worker Execution", f"Invoking worker agent: '{target_agent_name}' for role '{user_auth.get('role')}'")
        
        if target_agent_name == "Conversational Agent":
            worker_output = self.conversational_agent.execute(query)
        elif target_agent_name == "Alert Agent":
            worker_output = self.alert_agent.execute(query)
        elif target_agent_name == "Identity Agent":
            worker_output = self.identity_agent.execute(query)
        elif target_agent_name == "Endpoint Agent":
            worker_output = self.endpoint_agent.execute(query)
        elif target_agent_name == "Incident Agent":
            worker_output = self.incident_agent.execute(query, approved=hitl_approved, auth_context=user_auth)
        elif target_agent_name == "Reporting Agent":
            worker_output = self.reporting_agent.execute(query)
        elif target_agent_name == "Threat Correlation Agent":
            worker_output = self.correlation_agent.execute(query, auth_context=user_auth)
        else:
            worker_output = self.conversational_agent.execute(query)

        execution_trace.append({
            "stage_number": 2,
            "stage_title": f"Stage 2: Telemetry & Task Execution ({target_agent_name})",
            "agent": worker_output.get("agent", target_agent_name),
            "tool_calls": worker_output.get("tool_calls", [])
        })

        # Stage 3: Human-in-the-Loop Interruption Check
        if worker_output.get("requires_hitl"):
            log_stage("HITL Interruption", f"Action requires analyst confirmation: {worker_output.get('hitl_action')}", level="warning")
            execution_trace.append({
                "stage_number": 3,
                "stage_title": "Stage 3: Human-in-the-Loop Interruption",
                "agent": "Human-in-the-Loop Controller",
                "status": "WAITING_FOR_ANALYST"
            })
            return {
                "status": "HITL_REQUIRED",
                "target_agent": worker_output.get("agent"),
                "response": worker_output.get("response"),
                "action_details": worker_output.get("action_details"),
                "execution_trace": execution_trace
            }

        # Stage 4: Conclusive Analysis & Final Synthesis
        log_stage("Workflow Completion", f"Workflow finished successfully via {worker_output.get('agent')}")
        execution_trace.append({
            "stage_number": 4,
            "stage_title": "Stage 4: Synthesis & Compliance Audit Log",
            "agent": worker_output.get("agent", "SENTRY Orchestrator"),
            "status": "COMPLETED"
        })

        return {
            "status": "SUCCESS",
            "target_agent": worker_output.get("agent"),
            "response": worker_output.get("response", ""),
            "data": worker_output.get("data"),
            "execution_trace": execution_trace
        }
