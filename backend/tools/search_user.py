from typing import Optional, Dict, Any, List
from backend.services.api_client import SOCApiClient

client = SOCApiClient()

def search_user(query: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Search user identity directory by user email, name, or department.
    """
    return client.get_users(query=query)

def get_user_logins(user_email: str) -> List[Dict[str, Any]]:
    """
    Retrieve login history logs for a given user email.
    """
    return client.get_login_history(user_email=user_email)
