import re
from typing import Any, Dict

from langchain_core.messages import HumanMessage

from backend.services.api_client import SOCApiClient
from backend.services.correlation_service import ThreatCorrelationService
from backend.services.llm import get_llm
from backend.tools.report_generator import generate_report
from backend.utils.logger import log_stage


class ReportingAgent:
    """Creates a report only from evidence resolved from the request scope."""

    def __init__(self, provider: str = None):
        self.provider = provider
        self.client = SOCApiClient()

    def execute(self, query: str) -> Dict[str, Any]:
        incident_match = re.search(r"\bINC-[A-Za-z0-9-]+\b", query, re.IGNORECASE)
        incident = None
        report_scope = query
        if incident_match:
            incident_id = incident_match.group(0).upper()
            incidents = self.client.get_incidents(incident_id)
            if not incidents:
                return {"agent": "Reporting Agent", "response": f"ℹ️ **Incident Ticket Not Found**\n\nNo incident matches `{incident_id}`.", "data": {"found": False, "target_incident": incident_id}, "tool_calls": [{"tool": "get_incidents", "query": incident_id, "found": 0}]}
            incident = incidents[0]
            report_scope = f"{query} {incident.get('affected_user', '')} {incident.get('affected_host', '')}"

        correlation = ThreatCorrelationService.correlate_investigation(query=report_scope, incident_id=(incident or {}).get("incident_id"))
        if correlation.get("no_evidence"):
            return {"agent": "Reporting Agent", "response": "ℹ️ **Insufficient Evidence for Report**\n\nNo telemetry matched the requested report scope. Verify the incident ID or target entity.", "data": correlation, "tool_calls": [{"tool": "correlate_investigation", "results_count": 0}]}

        user = correlation.get("target_user") or {}
        endpoint = correlation.get("target_host") or {}
        threat_intel = correlation.get("threat_intel") or {}
        alerts = correlation["matched_alerts"]
        summary = self._summarize(correlation, user, endpoint, threat_intel)
        report = generate_report(
            incident_id=(incident or {}).get("incident_id", "N/A"),
            title=(incident or {}).get("title", f"Investigation report: {endpoint.get('hostname', user.get('email', 'environment scope'))}"),
            severity=(incident or {}).get("severity", correlation["risk_level"]),
            summary=summary,
            alerts=alerts,
            user=user,
            endpoint=endpoint,
            threat_intel=threat_intel,
        )
        tool_calls = [
            {"tool": "correlate_investigation", "alerts_correlated": len(alerts)},
            {"tool": "generate_report", "incident_id": (incident or {}).get("incident_id")},
        ]
        return {"agent": "Reporting Agent", "response": report, "data": {"report": report, "correlation": correlation}, "tool_calls": tool_calls}

    def _summarize(self, correlation: Dict[str, Any], user: Dict[str, Any], endpoint: Dict[str, Any], threat_intel: Dict[str, Any]) -> str:
        fallback = (
            f"The report is based on {len(correlation['matched_alerts'])} correlated alert(s) for "
            f"user `{user.get('email', 'N/A')}` and endpoint `{endpoint.get('hostname', 'N/A')}`. "
            f"The evidence-derived assessment is `{correlation['risk_level']}` risk ({correlation['composite_risk']}/100)."
        )
        try:
            llm = get_llm(self.provider)
            prompt = (
                "Write a two-sentence executive summary using only this evidence. Do not claim containment, attribution, or compromise unless explicitly present. "
                f"Alerts: {len(correlation['matched_alerts'])}; risk: {correlation['risk_level']} ({correlation['composite_risk']}/100); "
                f"user: {user.get('email')}; endpoint: {endpoint.get('hostname')}; threat intel: {threat_intel.get('indicator')} / {threat_intel.get('threat_actor')}."
            )
            response = llm.invoke([HumanMessage(content=prompt)])
            if response and response.content and "MockLLMEngine" not in type(llm).__name__:
                return response.content.strip()
        except Exception as error:
            log_stage("Reporting Agent", f"LLM summary unavailable; using evidence summary ({error})", level="warning")
        return fallback
