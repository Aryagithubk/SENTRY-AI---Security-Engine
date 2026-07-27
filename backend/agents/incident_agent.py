from typing import Any, Dict, Optional

from backend.services.api_client import SOCApiClient
from backend.services.audit_service import AuditService
from backend.services.rbac_service import RBACService
from backend.tools.create_incident import create_incident
from backend.utils.logger import log_stage


class IncidentAgent:
    """Creates an incident only for a resolved, approved request target."""

    def __init__(self):
        self.client = SOCApiClient()

    @staticmethod
    def _highest_severity(alerts):
        order = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
        return max((alert.get("severity", "MEDIUM").upper() for alert in alerts), key=lambda value: order.get(value, 0), default="MEDIUM")

    def _resolve_context(self, query: str) -> Dict[str, Any]:
        endpoints = self.client.get_endpoints(query)
        users = self.client.get_users(query)
        endpoint = endpoints[0] if endpoints else None
        user = users[0] if users else None
        if user is None and endpoint and endpoint.get("assigned_user"):
            matches = self.client.get_users(endpoint["assigned_user"])
            user = matches[0] if matches else None
        if endpoint is None and user:
            matches = self.client.get_endpoints(user.get("email"))
            endpoint = matches[0] if matches else None
        key = (endpoint or {}).get("hostname") or (user or {}).get("email") or query
        alerts = self.client.get_alerts(key)
        return {"endpoint": endpoint, "user": user, "alerts": alerts}

    def execute(self, query: str, approved: bool = False, auth_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        user_role = (auth_context or {}).get("role", "L1")
        user_id = (auth_context or {}).get("username", "analyst_l1")
        allowed, message = RBACService.authorize_action(user_role, "create_incident")
        if not allowed:
            AuditService.log_event(user_id=user_id, user_role=user_role, action="CREATE_INCIDENT", resource=query[:80], result="DENIED", details=message)
            return {"agent": "Incident Agent", "response": f"🔒 **Permission Denied: Elevated Authorization Required**\n\n{message}", "data": {"authorized": False}, "tool_calls": []}

        context = self._resolve_context(query)
        endpoint, affected_user, alerts = context["endpoint"], context["user"], context["alerts"]
        if endpoint is None and affected_user is None:
            return {"agent": "Incident Agent", "response": "ℹ️ **Incident Target Not Found**\n\nProvide a valid hostname, IP address, or user email before creating an incident.", "data": {"authorized": True, "found": False}, "tool_calls": []}

        host_name = (endpoint or {}).get("hostname", "Unspecified host")
        user_email = (affected_user or {}).get("email", (endpoint or {}).get("assigned_user", "Unspecified user"))
        severity = self._highest_severity(alerts)
        title = f"Security investigation: {host_name} / {user_email}"
        related_alerts = [alert.get("alert_id") for alert in alerts if alert.get("alert_id")]
        summary = f"Incident requested for {host_name} and {user_email}. Evidence references {len(related_alerts)} matching alert(s)."
        action_details = {"action": "Create Security Incident", "target_host": host_name, "target_user": user_email, "severity": severity, "description": summary, "query": query}

        if not approved:
            return {"agent": "Incident Agent", "requires_hitl": True, "hitl_action": "CREATE_SECURITY_INCIDENT", "action_details": action_details,
                    "response": f"⚠️ **Human-in-the-Loop Confirmation Required**\n\nAuthorize creation of a `{severity}` incident for host `{host_name}` and user `{user_email}`?"}

        log_stage("Incident Agent", f"Creating approved incident for {host_name} and {user_email}")
        incident = create_incident(title=title, severity=severity, summary=summary, affected_user=user_email, affected_host=host_name, related_alerts=related_alerts)
        AuditService.log_event(user_id=user_id, user_role=user_role, action="INCIDENT_CREATED", resource=incident.get("incident_id", "N/A"), result="SUCCESS", details=f"Created after HITL approval for {host_name}.")
        return {"agent": "Incident Agent", "requires_hitl": False,
                "response": f"✅ **Security Incident Created**\n\n- **Incident Ticket**: `{incident.get('incident_id')}`\n- **Severity**: `{incident.get('severity')}`\n- **Affected Target**: `{user_email}` (`{host_name}`)\n- **Status**: `{incident.get('status')}`",
                "data": incident, "tool_calls": [{"tool": "create_incident", "incident_id": incident.get("incident_id"), "approved_by": user_id}]}
