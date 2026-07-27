from typing import Optional, Dict, Any
from backend.services.api_client import SOCApiClient

client = SOCApiClient()

def lookup_ip(indicator: str) -> Optional[Dict[str, Any]]:
    """
    Perform Threat Intelligence lookup for an IP address or SHA256 file hash.
    """
    return client.lookup_ip_or_hash(indicator=indicator)
