import datetime
from typing import Dict, Any, List

def format_alert_summary(alert: Dict[str, Any]) -> str:
    """Format a single security alert dict into Markdown."""
    return f"""### 🚨 Alert {alert.get('alert_id')} - {alert.get('title')}
- **Severity**: `{alert.get('severity')}`
- **Source**: {alert.get('source')}
- **Timestamp**: `{alert.get('timestamp')}`
- **User Email**: `{alert.get('user_email')}`
- **Host / IP**: `{alert.get('hostname', 'N/A')}` / `{alert.get('source_ip', 'N/A')}`
- **TTP**: `{alert.get('mitre_ttp')}`
- **Description**: {alert.get('description')}
- **Status**: `{alert.get('status')}`
"""

def format_user_summary(user: Dict[str, Any]) -> str:
    """Format user record into Markdown."""
    return f"""### 👤 User Profile: {user.get('name')} (`{user.get('email')}`)
- **Department**: {user.get('department')}
- **Role**: {user.get('role')}
- **Risk Score**: `{user.get('risk_score')}/100`
- **Account Status**: `{user.get('account_status')}`
- **MFA Enabled**: `{user.get('mfa_enabled')}`
- **Assigned Host**: `{user.get('assigned_device')}`
- **Last Active**: `{user.get('last_active')}`
"""

def format_endpoint_summary(ep: Dict[str, Any]) -> str:
    """Format host endpoint dict into Markdown."""
    malware_text = "None"
    if ep.get("malware_detected") and ep.get("detected_malware"):
        malware_text = "\n".join([
            f"  - Threat: `{m.get('threat_name')}` | Path: `{m.get('file_path')}` | Action: `{m.get('action_taken')}`"
            for m in ep.get("detected_malware", [])
        ])

    return f"""### 💻 Endpoint: `{ep.get('hostname')}` (`{ep.get('ip_address')}`)
- **OS**: {ep.get('os')}
- **Assigned User**: `{ep.get('assigned_user')}`
- **Health Status**: `{ep.get('health_status')}`
- **EDR Version**: {ep.get('edr_version')} (Agent `{ep.get('agent_status')}`)
- **Malware Detected**: `{ep.get('malware_detected')}`
{malware_text}
"""

def calculate_composite_risk(alerts: List[Dict[str, Any]], user: Dict[str, Any], endpoint: Dict[str, Any]) -> int:
    """Calculate overall risk score from multi-source observations."""
    base = user.get("risk_score", 30)
    alert_points = 0
    for a in alerts:
        sev = a.get("severity", "").upper()
        if sev == "CRITICAL":
            alert_points += 25
        elif sev == "HIGH":
            alert_points += 15
        elif sev == "MEDIUM":
            alert_points += 5
    
    ep_points = 0
    if endpoint.get("health_status") == "COMPROMISED":
        ep_points = 30
    elif endpoint.get("health_status") == "WARNING":
        ep_points = 15

    total = min(100, base + alert_points + ep_points)
    return total
