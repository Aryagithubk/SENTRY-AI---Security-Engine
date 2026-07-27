from typing import TypedDict, List, Dict, Any, Optional

class SecureOpsState(TypedDict):
    """
    Shared TypedDict State for LangGraph Multi-Agent Workflows in SENTRY.
    Maintains user query, user authorization context, conversation history,
    active agent delegates, telemetry data, risk assessments, HITL status, and audit records.
    """
    user_query: str
    auth_context: Dict[str, Any]       # username, name, email, role, role_display, permissions
    messages: List[Dict[str, Any]]
    active_agent: str
    agent_outputs: Dict[str, Any]
    tool_outputs: List[Dict[str, Any]]
    investigation_context: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    hitl_status: Dict[str, Any]
    audit_entries: List[Dict[str, Any]]
    errors: List[str]
    final_response: str
