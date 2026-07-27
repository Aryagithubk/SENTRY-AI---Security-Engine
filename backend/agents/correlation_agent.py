from typing import Any, Dict, Optional

from backend.services.audit_service import AuditService
from backend.services.correlation_service import ThreatCorrelationService
from backend.services.rbac_service import RBACService
from backend.utils.logger import log_stage


class CorrelationAgent:
    """Correlates the evidence in the user's requested scope after RBAC approval."""

    def execute(self, query: str, auth_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        user_role = (auth_context or {}).get("role", "L1")
        user_id = (auth_context or {}).get("username", "analyst_l1")
        is_authorized, authorization_message = RBACService.authorize_action(user_role, "correlate_events")
        if not is_authorized:
            log_stage("Correlation Agent", f"Access denied for role {user_role}: {authorization_message}", level="warning")
            AuditService.log_event(user_id=user_id, user_role=user_role, action="THREAT_CORRELATION", result="DENIED", details=authorization_message)
            return {
                "agent": "Threat Correlation Agent",
                "response": f"🔒 **Permission Denied: Elevated Authorization Required**\n\n{authorization_message}\n\n*Threat hunting and multi-event correlation require an L2 SOC Analyst or SOC Manager role.*",
                "data": {"authorized": False},
                "tool_calls": [],
            }

        result = ThreatCorrelationService.correlate_investigation(query=query)
        if result.get("no_evidence"):
            return {
                "agent": "Threat Correlation Agent",
                "response": "ℹ️ **No Correlated Evidence Found**\n\nNo telemetry matched the requested scope. Verify the user, host, or IP address and try again.",
                "data": result,
                "tool_calls": [{"tool": "correlate_investigation", "scope": result.get("scope"), "results_count": 0}],
            }

        user = result.get("target_user") or {}
        host = result.get("target_host") or {}
        evidence_rows = "\n".join(
            f"- `[{alert.get('severity')}]` `{alert.get('timestamp')}` - **{alert.get('title')}** ({alert.get('source')})"
            for alert in result["matched_alerts"]
        )
        reasons = "\n".join(f"- {reason}" for reason in result["explainability"]["reasons"])

        AuditService.log_event(
            user_id=user_id,
            user_role=user_role,
            action="THREAT_CORRELATION",
            resource=f"Target: {user.get('email', 'environment scope')} / {host.get('hostname', 'environment scope')}",
            result="SUCCESS",
            details=f"Risk Level: {result['risk_level']} ({result['composite_risk']}/100)",
        )
        response = f"""# 🕸️ Multi-Vector Threat Correlation
**Correlated User**: `{user.get('name', 'N/A')}` (`{user.get('email', 'N/A')}`) | **Endpoint**: `{host.get('hostname', 'N/A')}` (`{host.get('ip_address', 'N/A')}`)
**Risk**: `{result['risk_level']}` (`{result['composite_risk']}/100`) | **Confidence**: `{result['confidence_pct']}%`

### Evidence-Based Correlation Rationale
{reasons}

### Correlated Event Timeline
{evidence_rows}

### Recommended Analyst Actions
{result['explainability']['recommended_next_step']}
"""
        return {
            "agent": "Threat Correlation Agent",
            "response": response,
            "data": result,
            "tool_calls": [{
                "tool": "correlate_investigation",
                "target_user": user.get("email"),
                "target_host": host.get("hostname"),
                "alerts_correlated": len(result["matched_alerts"]),
            }],
        }
