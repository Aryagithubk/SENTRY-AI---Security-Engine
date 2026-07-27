from typing import Dict, Any, List
from backend.tools.search_alert import search_alert
from backend.utils.helpers import format_alert_summary

class AlertAgent:
    """Specialized agent for searching, analyzing, and triaging SIEM security alerts."""

    def execute(self, query: str) -> Dict[str, Any]:
        # The repository resolves severity and entity constraints from the
        # current SQLite values, including minor spelling errors.
        alerts = search_alert(query=query)
        
        if not alerts:
            return {
                "agent": "Alert Agent",
                "response": f"🔍 No security alerts matching query `{query}` were found in the SIEM database.",
                "data": [],
                "tool_calls": [{"tool": "search_alert", "query": query, "results_count": 0}]
            }

        summary_parts = [f"Found **{len(alerts)}** matching security alert(s):\n"]
        for a in alerts:
            summary_parts.append(format_alert_summary(a))

        return {
            "agent": "Alert Agent",
            "response": "\n".join(summary_parts),
            "data": alerts,
            "tool_calls": [{"tool": "search_alert", "query": query, "results_count": len(alerts)}]
        }
