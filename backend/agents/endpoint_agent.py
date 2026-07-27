import re
from typing import Dict, Any, List
from backend.tools.check_endpoint import check_endpoint
from backend.utils.helpers import format_endpoint_summary

class EndpointAgent:
    """
    Specialized agent for host endpoint diagnostics, EDR agent health, and malware inspection.
    Politely informs the user if a target host or IP is not found in the database.
    """

    def execute(self, query: str) -> Dict[str, Any]:
        # Dynamically extract host or IP pattern from query
        host_match = re.search(r"\b(?:WS|LAPTOP|SRV|HOST|DEV|PROD|PC|MAC|WIN)-[A-Za-z0-9-]+\b", query, re.I)
        ip_match = re.search(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", query)
        
        target_query = host_match.group(0) if host_match else (ip_match.group(0) if ip_match else query.strip())

        endpoints = check_endpoint(query=target_query)
        
        if not endpoints:
            # Polite response when endpoint host is not found in database
            target_name = target_query.upper()
            return {
                "agent": "Endpoint Agent",
                "response": f"ℹ️ **Endpoint Device Not Found**\n\nNo active EDR telemetry or device records were found for host `{target_name}` in the enterprise endpoint directory.\n\nPlease verify the hostname or IP address and try again.",
                "data": {"found": False, "target": target_name},
                "tool_calls": [{"tool": "check_endpoint", "query": target_query, "hosts_found": 0}]
            }

        summary_parts = [f"Retrieved endpoint diagnostics for **{len(endpoints)}** host(s):\n"]
        for ep in endpoints:
            summary_parts.append(format_endpoint_summary(ep))

        return {
            "agent": "Endpoint Agent",
            "response": "\n".join(summary_parts),
            "data": endpoints,
            "tool_calls": [{"tool": "check_endpoint", "query": target_query, "hosts_found": len(endpoints)}]
        }
