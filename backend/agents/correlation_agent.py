from typing import Dict, Any, Optional
from backend.services.rbac_service import RBACService
from backend.services.audit_service import AuditService
from backend.services.correlation_service import ThreatCorrelationService
from backend.utils.logger import log_stage

class CorrelationAgent:
    """
    Phase 2 Agent specialized in Threat Hunting, Event Correlation, and Attack Chain Construction.
    Enforces RBAC authorization and logs compliance audit records.
    """

    def execute(self, query: str, auth_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        user_role = (auth_context or {}).get("role", "L1")
        user_id = (auth_context or {}).get("username", "analyst_l1")

        # 1. RBAC Authorization Check
        is_auth, auth_msg = RBACService.authorize_action(user_role, "correlate_events")
        if not is_auth:
            log_stage("Correlation Agent", f"Access Denied for role {user_role}: {auth_msg}", level="warning")
            AuditService.log_event(
                user_id=user_id, user_role=user_role, action="THREAT_CORRELATION", result="DENIED", details=auth_msg
            )
            return {
                "agent": "Threat Correlation Agent",
                "response": f"🔒 **Permission Denied: Elevated Authorization Required**\n\n{auth_msg}\n\n*Threat Hunting and Multi-Event Correlation requires **L2 SOC Analyst** or **SOC Manager** privileges.*",
                "data": {"authorized": False},
                "tool_calls": []
            }

        log_stage("Correlation Agent", f"Executing threat correlation analysis for query: '{query}'")

        # Extract potential entities from query
        correlation_result = ThreatCorrelationService.correlate_investigation()

        # Log compliance audit event
        AuditService.log_event(
            user_id=user_id,
            user_role=user_role,
            action="THREAT_CORRELATION",
            resource=f"Target: {correlation_result['target_user'].get('email')} / {correlation_result['target_host'].get('hostname')}",
            result="SUCCESS",
            details=f"Risk Level: {correlation_result['risk_level']} ({correlation_result['composite_risk']}/100)"
        )

        user = correlation_result["target_user"]
        host = correlation_result["target_host"]
        threat = correlation_result["threat_intel"]
        exp = correlation_result["explainability"]

        # Format Markdown Explanation
        summary_md = f"""# 🕸️ Multi-Vector Threat Correlation & Attack Chain Analysis
**Correlated Target**: `{user.get('name')}` (`{user.get('email')}`) | **Device**: `{host.get('hostname')}` (`{host.get('ip_address')}`)  
**Composite Risk Level**: **`{correlation_result['risk_level']}`** (`{correlation_result['composite_risk']}/100`) | **Confidence**: `{correlation_result['confidence_pct']}%`

---

### 🔍 1. Explainable Correlation Rationale ("Why Am I Seeing This?")
- **User Identity Anomaly**: User risk score `{user.get('risk_score')}/100` with Impossible Travel logins detected.
- **Endpoint Compromise**: `{host.get('hostname')}` status is `{host.get('health_status')}` with detected Cobalt Strike PowerShell beaconing.
- **Threat Actor Attribution**: C2 IP `{threat.get('indicator')}` positively identified as `{threat.get('threat_actor')}` infrastructure.
- **Correlated Events**: `{len(correlation_result['matched_alerts'])} SIEM alerts` linked across Identity, EDR, Firewall, and Cloud Trail.

---

### 🔗 2. Graphical Attack Chain Sequence
1. 🌐 **Malicious C2 IP** (`{threat.get('indicator')}`) → Outbound reconnaissance & credential harvesting.
2. 👤 **Identity Breach** (`{user.get('email')}`) → Brute force & Impossible travel login from Bucharest.
3. 💻 **Device Infection** (`{host.get('hostname')}`) → Base64 PowerShell execution downloading ransomware payload.
4. ⚠️ **C2 Beaconing** → Active TLS TCP 443 telemetry session to adversary server.
5. 🚨 **Impair Defenses & Encryption** → Rapid file modification (`.locked`) and AWS security group edits.

---

### 💡 3. Recommended Analyst Actions
{exp['recommended_next_step']}
"""

        return {
            "agent": "Threat Correlation Agent",
            "response": summary_md,
            "data": correlation_result,
            "tool_calls": [{"tool": "correlate_investigation", "target_user": user.get("email"), "target_host": host.get("hostname")}]
        }
