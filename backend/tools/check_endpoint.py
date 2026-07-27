from typing import Optional, Dict, Any, List
from backend.services.api_client import SOCApiClient

client = SOCApiClient()

def check_endpoint(query: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Check EDR host device status, health status, and malware detection records.
    """
    return client.get_endpoints(query=query)
