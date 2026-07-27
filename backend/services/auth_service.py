from typing import Optional, Dict, Any
from backend.services.db_service import DatabaseService

class AuthService:
    """Service layer verifying user credentials, role selection, and session context via SQLite database."""

    @classmethod
    def authenticate(cls, username_or_email: str, password: str, selected_role_code: str = "L1") -> Optional[Dict[str, Any]]:
        """
        Verify credentials against SQLite database.
        Checks username/email, password, and matching selected role.
        """
        if not username_or_email or not password:
            return None

        user = DatabaseService.verify_user_login(
            username_or_email=username_or_email,
            password=password,
            selected_role_code=selected_role_code
        )
        return user
