import re
from typing import Dict, Any, List
from backend.tools.report_generator import generate_report
from backend.services.api_client import SOCApiClient
from backend.services.llm import get_llm
from backend.utils.logger import log_stage
from langchain_core.messages import SystemMessage, HumanMessage

client = SOCApiClient()

class ReportingAgent:
    """
    Specialized agent for executive investigation reports and summaries.
    Uses LLM reasoning (Ollama / Gemini / OpenAI) to dynamically synthesize threat conclusions & remedies.
    """

    def __init__(self, provider: str = None):
        self.provider = provider

    def execute(self, query: str) -> Dict[str, Any]:
        log_stage("Reporting Agent", f"Executing dynamic executive reporting pipeline for query: '{query}'")
        
        # 1. Dynamic Incident ID Extraction
        inc_match = re.search(r"\bINC-[A-Za-z0-9-]+\b", query, re.I)
        target_inc = None
        if inc_match:
            inc_id = inc_match.group(0).upper()
            found_incs = client.get_incidents(inc_id)
            if found_incs:
                target_inc = found_incs[0]
            else:
                return {
                    "agent": "Reporting Agent",
                    "response": f"ℹ️ **Unable to Generate Report: Incident Ticket Not Found**\n\nNo active incident ticket matching `{inc_id}` was found in the Incident Management System.\n\nPlease verify the incident ID and try again.",
                    "data": {"found": False, "target_incident": inc_id},
                    "tool_calls": [{"tool": "get_incidents", "query": inc_id, "found": 0}]
                }

        # 2. Dynamic Email Extraction
        email_match = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", query)
        target_user_email = email_match.group(0) if email_match else (target_inc.get("affected_user") if target_inc else None)

        if email_match and not target_inc:
            found_users = client.get_users(target_user_email)
            if not found_users:
                return {
                    "agent": "Reporting Agent",
                    "response": f"ℹ️ **Unable to Generate Report: User Account Not Found**\n\nNo user account or security telemetry was found for `{target_user_email}` in the enterprise identity database.\n\nPlease verify the user email address and try again.",
                    "data": {"found": False, "target_user": target_user_email},
                    "tool_calls": [{"tool": "get_users", "query": target_user_email, "found": 0}]
                }

        # 3. Dynamic Host or IP Extraction
        ip_match = re.search(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", query)
        host_match = re.search(r"\b(?:WS|LAPTOP|SRV|HOST|DEV|PROD|PC|MAC|WIN)-[A-Za-z0-9-]+\b", query, re.I)
        target_host = host_match.group(0) if host_match else (ip_match.group(0) if ip_match else (target_inc.get("affected_host") if target_inc else None))

        if (host_match or ip_match) and not target_inc and not email_match:
            found_eps = client.get_endpoints(target_host)
            if not found_eps:
                return {
                    "agent": "Reporting Agent",
                    "response": f"ℹ️ **Unable to Generate Report: Host Device Not Found**\n\nNo device records or telemetry were found for host `{target_host.upper()}` in the enterprise endpoint directory.\n\nPlease verify the device hostname or IP address and try again.",
                    "data": {"found": False, "target_host": target_host},
                    "tool_calls": [{"tool": "get_endpoints", "query": target_host, "found": 0}]
                }

        # Fetch telemetry records dynamically
        users = client.get_users(target_user_email) if target_user_email else []
        endpoints = client.get_endpoints(target_host) if target_host else []

        user = users[0] if users else (client.get_users()[0] if client.get_users() else {})
        ep = endpoints[0] if endpoints else (client.get_endpoints()[0] if client.get_endpoints() else {})

        alerts = client.get_alerts(query=user.get("email") or ep.get("hostname") or query)

        ip_indicator = ep.get("ip_address") or "185.220.101.5"
        for a in alerts:
            if a.get("source_ip") and a.get("source_ip") != "N/A":
                ip_indicator = a.get("source_ip")
                break

        threat_intel = client.lookup_ip_or_hash(ip_indicator) or {}

        if not target_inc:
            incidents = client.get_incidents()
            target_inc = incidents[0] if incidents else {}

        # Use LLM to synthesize dynamic AI Root Cause Analysis & Containment Playbook
        ai_summary = f"Automated threat hunting & correlation report for account {user.get('email', 'N/A')} and host {ep.get('hostname', 'N/A')}."
        
        try:
            llm = get_llm(self.provider)
            prompt = f"""You are the Lead SOC Reporting AI. Analyze the following correlated security telemetry and generate a brief 2-sentence executive root cause summary for user '{user.get('name')}' ({user.get('email')}) on endpoint '{ep.get('hostname')}'.
Telemetry:
- User Risk Score: {user.get('risk_score')}/100, Status: {user.get('account_status')}
- Endpoint Health: {ep.get('health_status')}, OS: {ep.get('os')}
- Threat Intel IP: {threat_intel.get('indicator')}, Actor: {threat_intel.get('threat_actor')}
- Alerts Count: {len(alerts)}
Provide ONLY the 2-sentence summary."""
            
            response = llm.invoke([HumanMessage(content=prompt)])
            if response and response.content and len(response.content) > 20 and "Mock" not in str(type(llm)):
                ai_summary = response.content.strip()
                log_stage("LLM Synthesis", "Successfully generated dynamic AI threat summary via LLM")
        except Exception as e:
            log_stage("LLM Synthesis Warning", f"Using base telemetry summary ({e})")

        report_md = generate_report(
            incident_id=target_inc.get("incident_id", "INC-2026-001"),
            title=f"Executive Threat Investigation: {user.get('name', 'Enterprise Target')}",
            severity=target_inc.get("severity", "HIGH"),
            summary=ai_summary,
            alerts=alerts,
            user=user,
            endpoint=ep,
            threat_intel=threat_intel
        )

        return {
            "agent": "Reporting Agent",
            "response": report_md,
            "data": {"report": report_md},
            "tool_calls": [{"tool": "generate_report", "target_user": user.get("email"), "target_host": ep.get("hostname")}]
        }
