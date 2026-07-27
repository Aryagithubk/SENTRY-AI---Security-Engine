from typing import Dict, Any, Optional
from backend.tools.create_incident import create_incident
from backend.services.rbac_service import RBACService
from backend.services.audit_service import AuditService
from backend.utils.logger import log_stage

class IncidentAgent:
    """
    Specialized agent for Incident Management, Ticket Escalation, and Host Containment.
    Enforces RBAC permissions (SOC Manager required) and Human-in-the-Loop authorization.
    """

    def execute(self, query: str, approved: bool = False, auth_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        user_role = (auth_context or {}).get("role", "L1")
        user_id = (auth_context or {}).get("username", "analyst_l1")

        # 1. RBAC Permission Check
        is_auth, auth_msg = RBACService.authorize_action(user_role, "create_incident")
        if not is_auth:
            log_stage("Incident Agent", f"Incident escalation blocked for role '{user_role}': {auth_msg}", level="warning")
            AuditService.log_event(
                user_id=user_id,
                user_role=user_role,
                action="CREATE_INCIDENT",
                resource="WS-FINANCE-04",
                result="DENIED",
                details="Action requires SOC Manager / Incident Commander role."
            )
            return {
                "agent": "Incident Agent",
                "response": f"🔒 **Permission Denied: Elevated Authorization Required**\n\nDirect Incident Escalation and Creation requires **SOC Manager / Incident Commander** privileges. You are currently operating as **{user_role}**.\n\n*An escalation request has been logged in the audit trail for Manager review.*",
                "data": {"authorized": False, "requires_approval": True},
                "tool_calls": []
            }

        # 2. Human-in-the-Loop Authorization Check
        if not approved:
            log_stage("Incident Agent", "HITL Authorization Required: Pausing workflow for analyst approval", level="warning")
            return {
                "agent": "Incident Agent",
                "requires_hitl": True,
                "hitl_action": "CREATE_SECURITY_INCIDENT",
                "action_details": {
                    "action": "Create Security Incident & Isolate Host",
                    "target_host": "WS-FINANCE-04",
                    "target_user": "sarah.c@securetech.com",
                    "severity": "HIGH",
                    "description": "Active LockBit ransomware payload & Cobalt Strike C2 beaconing detected."
                },
                "response": "⚠️ **Human-in-the-Loop Confirmation Required**\n\nAuthorization requested to create a High-Severity Security Incident ticket for host **WS-FINANCE-04** (`10.0.4.45`) and user **sarah.c@securetech.com**.\n\n*Please confirm or abort this operation in the dialog below.*"
            }

        # 3. Execution upon HITL Approval
        log_stage("Incident Agent", f"Action Authorized by {user_id} ({user_role}). Creating incident ticket...")
        
        inc_data = create_incident(
            title="Active Ransomware & C2 Beaconing on WS-FINANCE-04",
            severity="CRITICAL",
            summary="Multi-stage attack involving PowerShell payload execution, Cobalt Strike C2 beaconing (185.220.101.5), and mass file encryption.",
            affected_user="sarah.c@securetech.com",
            affected_host="WS-FINANCE-04",
            related_alerts=["ALT-1003", "ALT-1004", "ALT-1005"]
        )

        # Log compliance audit record
        AuditService.log_event(
            user_id=user_id,
            user_role=user_role,
            action="INCIDENT_CREATED",
            resource=inc_data.get("incident_id", "INC-2026-001"),
            result="SUCCESS",
            details=f"Created incident ticket {inc_data.get('incident_id')} for WS-FINANCE-04 upon HITL authorization."
        )

        return {
            "agent": "Incident Agent",
            "requires_hitl": False,
            "response": f"✅ **Security Incident Created & Host Isolated**\n\n- **Incident Ticket**: `{inc_data.get('incident_id')}`\n- **Severity**: `{inc_data.get('severity')}`\n- **Affected Target**: `sarah.c@securetech.com` (`WS-FINANCE-04`)\n- **Status**: `{inc_data.get('status')}`\n- **Timestamp**: `{inc_data.get('created_at')}`\n\n*EDR Network Containment rule applied. Incident response team notified.*",
            "data": inc_data,
            "tool_calls": [{"tool": "create_incident", "incident_id": inc_data.get("incident_id"), "approved_by": user_id}]
        }
