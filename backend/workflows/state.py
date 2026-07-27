from typing import TypedDict, List, Dict, Any, Optional

class SecureOpsState(TypedDict, total=False):
    """
    Shared TypedDict State for LangGraph Multi-Agent Workflows in SENTRY.
    Maintains user query, user authorization context, conversation history,
    active agent delegates, telemetry data, risk assessments, HITL status, and audit records.
    """
    # Request and authentication context (created before the graph starts).
    user_query: str
    query: str
    auth_context: Dict[str, Any]       # username, name, email, role, role_display, permissions
    user: Dict[str, Any]
    role: str
    permissions: List[str]
    conversation_history: List[Dict[str, Any]]
    investigation_id: str

    # LangGraph orchestration decisions.  These are deliberately concise
    # decision records, not model chain-of-thought.
    intent: str
    required_evidence: List[str]
    routing_reason: str
    next_step: str
    requires_correlation: bool
    report_requested: bool
    action_required: bool
    messages: List[Dict[str, Any]]
    active_agent: str
    selected_agent: str
    agent_outputs: Dict[str, Any]
    tool_outputs: List[Dict[str, Any]]
    investigation_context: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    hitl_status: Dict[str, Any]
    audit_entries: List[Dict[str, Any]]
    errors: List[str]
    final_response: str
    status: str
    execution_trace: List[Dict[str, Any]]
