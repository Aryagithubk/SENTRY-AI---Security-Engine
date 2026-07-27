from typing import Optional, Dict, Any, List
from backend.services.api_client import SOCApiClient

client = SOCApiClient()

def search_alert(query: Optional[str] = None, severity: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Search SIEM security alerts filtered by search query keyword or severity level.
    """
    return client.get_alerts(query=query, severity=severity)
