import re
from typing import Tuple

def validate_ip_address(ip: str) -> bool:
    """Validate IPv4 address format."""
    pattern = r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
    return bool(re.match(pattern, ip.strip()))

def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return bool(re.match(pattern, email.strip()))

def sanitize_input(text: str) -> str:
    """Basic string sanitization to prevent malicious injection."""
    if not text:
        return ""
    return text.strip()
