from datetime import datetime, timezone
from typing import Any, Dict, List


def generate_report(incident_id: str, title: str, severity: str, summary: str, alerts: List[Dict[str, Any]], user: Dict[str, Any], endpoint: Dict[str, Any], threat_intel: Dict[str, Any]) -> str:
    """Render a report from supplied evidence without adding demo facts."""
    alert_rows = "\n".join(
        f"- **[{alert.get('severity', 'UNKNOWN')}] {alert.get('alert_id', 'N/A')}** (`{alert.get('timestamp', 'N/A')}`): {alert.get('title', 'Security alert')}\n  - Details: {alert.get('description', 'N/A')}\n  - TTP: `{alert.get('mitre_ttp', 'N/A')}` | Source: `{alert.get('source', 'N/A')}`"
        for alert in alerts
    ) or "- No alert evidence matched this report scope."
    recommendations = ["Validate the listed evidence before taking containment action."]
    if endpoint.get("health_status", "").upper() == "COMPROMISED":
        recommendations.append(f"Request authorized containment review for `{endpoint.get('hostname')}`.")
    if user.get("risk_score", 0) >= 70:
        recommendations.append(f"Review authentication sessions for `{user.get('email')}`.")
    if threat_intel.get("indicator"):
        recommendations.append(f"Validate network activity involving `{threat_intel.get('indicator')}`.")
    return f"""# Executive Investigation Report
**Title**: {title}
**Incident ID**: `{incident_id}` | **Assessment**: `{severity}`
**Generated**: `{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}`

## Evidence-Based Summary
{summary}

## Entities in Scope
- **User**: `{user.get('name', 'N/A')}` (`{user.get('email', 'N/A')}`)
- **Endpoint**: `{endpoint.get('hostname', 'N/A')}` (`{endpoint.get('ip_address', 'N/A')}`), health: `{endpoint.get('health_status', 'N/A')}`
- **Threat intelligence**: `{threat_intel.get('indicator', 'No matching indicator')}` - `{threat_intel.get('threat_actor', 'N/A')}`

## Correlated Timeline
{alert_rows}

## Recommended Next Steps
{chr(10).join(f'{index}. {recommendation}' for index, recommendation in enumerate(recommendations, start=1))}
"""
