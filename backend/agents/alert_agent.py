from typing import Dict, Any, List
from backend.tools.search_alert import search_alert
from backend.utils.helpers import format_alert_summary

class AlertAgent:
    """Specialized agent for searching, analyzing, and triaging SIEM security alerts."""

    def execute(self, query: str) -> Dict[str, Any]:
        # Extract potential severity filter or keywords
        severity = None
        for s in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            if s.lower() in query.lower():
                severity = s
                break

        alerts = search_alert(query=query, severity=severity)
        
        if not alerts:
            return {
                "agent": "Alert Agent",
                "response": f"🔍 No security alerts matching query `{query}` were found in the SIEM database.",
                "data": [],
                "tool_calls": [{"tool": "search_alert", "query": query, "severity": severity, "results_count": 0}]
            }

        summary_parts = [f"Found **{len(alerts)}** matching security alert(s):\n"]
        for a in alerts:
            summary_parts.append(format_alert_summary(a))

        return {
            "agent": "Alert Agent",
            "response": "\n".join(summary_parts),
            "data": alerts,
            "tool_calls": [{"tool": "search_alert", "query": query, "severity": severity, "results_count": len(alerts)}]
        }
