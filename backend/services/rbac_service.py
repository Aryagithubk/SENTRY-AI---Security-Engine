from typing import List, Dict, Any, Tuple

# Definitive Role Permissions Matrix
ROLE_PERMISSIONS: Dict[str, List[str]] = {
    "L1": [
        "VIEW_ALERTS",
        "SEARCH_USERS",
        "CHECK_ENDPOINTS",
        "VIEW_INCIDENTS",
        "VIEW_TIMELINE",
        "CONVERSATIONAL_GREETING"
    ],
    "L2": [
        "VIEW_ALERTS",
        "SEARCH_USERS",
        "CHECK_ENDPOINTS",
        "VIEW_INCIDENTS",
        "VIEW_TIMELINE",
        "CONVERSATIONAL_GREETING",
        "THREAT_HUNTING",
        "CORRELATE_EVENTS",
        "RECOMMEND_ESCALATION",
        "GENERATE_REPORTS",
        "INVESTIGATION_HANDOFF",
        "ASK_INVESTIGATION"
    ],
    "MANAGER": [
        "VIEW_ALERTS",
        "SEARCH_USERS",
        "CHECK_ENDPOINTS",
        "VIEW_INCIDENTS",
        "VIEW_TIMELINE",
        "CONVERSATIONAL_GREETING",
        "THREAT_HUNTING",
        "CORRELATE_EVENTS",
        "RECOMMEND_ESCALATION",
        "GENERATE_REPORTS",
        "INVESTIGATION_HANDOFF",
        "ASK_INVESTIGATION",
        "CREATE_INCIDENT",
        "ESCALATE_INCIDENT",
        "CLOSE_INVESTIGATION",
        "APPROVE_ACTIONS",
        "MANAGER_DASHBOARD"
    ],
    "CISO": [
        "VIEW_ALERTS",
        "VIEW_INCIDENTS",
        "CONVERSATIONAL_GREETING",
        "GENERATE_REPORTS",
        "VIEW_EXECUTIVE_SUMMARY",
        "VIEW_RISK_POSTURE",
        "CISO_DASHBOARD",
        "CAMPAIGN_VIEW"
    ],
    "ADMIN": [
        "VIEW_ALERTS",
        "SEARCH_USERS",
        "CHECK_ENDPOINTS",
        "VIEW_INCIDENTS",
        "CONVERSATIONAL_GREETING",
        "MANAGE_USERS",
        "MANAGE_ROLES",
        "VIEW_AUDIT_LOGS",
        "SYSTEM_CONFIG",
        "ADMIN_DASHBOARD"
    ]
}

# Action to Required Permission Mapping
ACTION_PERMISSIONS: Dict[str, str] = {
    "search_alert": "VIEW_ALERTS",
    "get_alert_details": "VIEW_ALERTS",
    "search_user": "SEARCH_USERS",
    "get_user_logins": "SEARCH_USERS",
    "check_endpoint": "CHECK_ENDPOINTS",
    "create_incident": "CREATE_INCIDENT",
    "escalate_incident": "ESCALATE_INCIDENT",
    "close_investigation": "CLOSE_INVESTIGATION",
    "generate_report": "GENERATE_REPORTS",
    "correlate_events": "CORRELATE_EVENTS",
    "threat_hunting": "THREAT_HUNTING",
    "view_audit_logs": "VIEW_AUDIT_LOGS"
}

class RBACService:
    """Service layer enforcing role-based authorization across UI, Orchestrator, Agents, and Tools."""

    @staticmethod
    def get_permissions_for_role(role: str) -> List[str]:
        return ROLE_PERMISSIONS.get(role.upper(), ROLE_PERMISSIONS["L1"])

    @classmethod
    def has_permission(cls, role: str, permission: str) -> bool:
        user_permissions = cls.get_permissions_for_role(role)
        return permission in user_permissions

    @classmethod
    def authorize_action(cls, role: str, action: str) -> Tuple[bool, str]:
        """
        Check if role has authorization for an action.
        Returns: (is_authorized, rationale_message)
        """
        required_perm = ACTION_PERMISSIONS.get(action.lower())
        if not required_perm:
            # Action has no explicit restriction
            return True, "Action authorized"

        if cls.has_permission(role, required_perm):
            return True, f"Role '{role}' possesses required permission '{required_perm}'"
        else:
            return False, f"Permission Denied: Role '{role}' lacks permission '{required_perm}' to execute '{action}'."
