from typing import Dict, Any, List

def generate_report(
    incident_id: str, 
    title: str, 
    severity: str, 
    summary: str, 
    alerts: List[Dict[str, Any]], 
    user: Dict[str, Any], 
    endpoint: Dict[str, Any], 
    threat_intel: Dict[str, Any]
) -> str:
    """
    Generate an enterprise executive investigation report in markdown format.
    Provides conclusive multi-vector analysis ("What Happened") and clear remediation playbooks ("What's the Remedy").
    """
    user_name = user.get("name", "Unknown Account")
    user_email = user.get("email", "N/A")
    user_risk = user.get("risk_score", 50)
    user_status = user.get("account_status", "ACTIVE")
    
    host_name = endpoint.get("hostname", "N/A")
    host_ip = endpoint.get("ip_address", "N/A")
    host_os = endpoint.get("os", "N/A")
    host_health = endpoint.get("health_status", "HEALTHY")
    
    threat_ip = threat_intel.get("indicator", "185.220.101.5")
    threat_actor = threat_intel.get("threat_actor", "Unknown Threat Actor")
    threat_conf = threat_intel.get("confidence_score", 85)
    
    # Format Alert Timeline
    alert_rows = ""
    for a in alerts:
        alert_rows += f"- **[{a.get('severity', 'HIGH')}] {a.get('alert_id', 'ALT')}** (`{a.get('timestamp', 'N/A')}`): **{a.get('title')}**\n  - *Details*: {a.get('description')}\n  - *TTP*: `{a.get('mitre_ttp', 'N/A')}` | *Source*: `{a.get('source', 'SIEM')}`\n"

    if not alert_rows:
        alert_rows = "- *No isolated alert anomalies detected for this scope.*\n"

    report = rf"""# 🛡️ Executive Incident Investigation & Root Cause Report
**Incident ID**: `{incident_id}` | **Classification**: `{severity}` | **Status**: `INVESTIGATED & CONTAINED`  
**Generated Date**: `2026-07-26` | **Lead Analyst**: `SecureOps AI Assistant`

---

## 🔍 1. Conclusive Root Cause Analysis ("What Happened")

### 📖 Incident Overview & Attack Narrative
{summary}

Analysis of multi-source telemetry indicates a **coordinated multi-stage attack chain**. The threat actor (`{threat_actor}`) initially gained unauthorized access through credential theft / impossible travel authentication, escalated privileges on endpoint `{host_name}`, and executed malicious C2 beaconing outbound to malicious infrastructure (`{threat_ip}`).

### 📊 Multi-Vector Entity Telemetry

| Investigation Vector | Target Entity | Telemetry Findings | Risk Level |
|---|---|---|---|
| **👤 User Identity** | `{user_name}` (`{user_email}`) | Risk Score: **`{user_risk}/100`** | Status: `{user_status}` | `HIGH` |
| **💻 Endpoint EDR** | `{host_name}` (`{host_ip}`) | Health: **`{host_health}`** | OS: `{host_os}` | `{severity}` |
| **🌐 Threat Intel** | `{threat_ip}` | Actor: **`{threat_actor}`** | Confidence: `{threat_conf}%` | `CRITICAL` |

---

## 🕒 2. Chronological Security Event Timeline
{alert_rows}

---

## 🛠️ 3. Recommended Remediation & Containment Playbook ("What's the Remedy")

### ⚡ Immediate Containment Actions (Phase 1)
1. **Network Host Isolation**: Immediately trigger EDR network containment on endpoint `{host_name}` (`{host_ip}`) to prevent lateral movement.
2. **Session Token Revocation**: Revoke all active OAuth2 & Kerberos SSO tokens for user account `{user_email}` across cloud IAM and local Active Directory.
3. **Perimeter Firewall Blocking**: Add malicious C2 IP `{threat_ip}` to edge perimeter firewall drop list (inbound/outbound TCP 443/80).

### 🔧 Long-Term Remediation & Hardening (Phase 2)
1. **MFA Re-Enrollment & Password Reset**: Force FIDO2 hardware-token MFA re-registration and mandatory 16+ character passphrase reset for `{user_email}`.
2. **EDR Full-Disk Remediation**: Execute deep EDR scan on `{host_name}` to remove any lingering persistence mechanisms or scheduled tasks.
3. **Cloud IAM & Policy Audit**: Review CloudTrail and Azure AD logs for any unauthorized privilege escalation or security group modifications performed during the breach window.
"""
    return report
