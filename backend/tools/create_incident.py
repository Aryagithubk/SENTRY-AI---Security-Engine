from typing import List, Dict, Any
from backend.services.api_client import SOCApiClient

client = SOCApiClient()

def create_incident(title: str, severity: str, affected_user: str, affected_host: str, summary: str, related_alerts: List[str]) -> Dict[str, Any]:
    """
    Create a new security incident record in the Incident Management System.
    """
    return client.create_incident(
        title=title,
        severity=severity,
        affected_user=affected_user,
        affected_host=affected_host,
        summary=summary,
        related_alerts=related_alerts
    )
