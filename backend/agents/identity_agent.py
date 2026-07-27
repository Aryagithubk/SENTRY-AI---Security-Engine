import re
from typing import Dict, Any, List
from backend.tools.search_user import search_user, get_user_logins
from backend.utils.helpers import format_user_summary

class IdentityAgent:
    """
    Specialized agent for user identity investigations, IAM logs, and authentication checks.
    Politely informs the user if a target email address is not found in the database.
    """

    def execute(self, query: str) -> Dict[str, Any]:
        # Dynamically extract any valid email address from query
        email_match = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", query)
        target_query = email_match.group(0) if email_match else query.strip()

        users = search_user(query=target_query)
        
        if not users:
            # Polite response when user account is not found in database
            target_name = email_match.group(0) if email_match else query.strip()
            return {
                "agent": "Identity Agent",
                "response": f"ℹ️ **User Identity Not Found**\n\nNo active account records or authentication telemetry were found for `{target_name}` in the enterprise identity directory.\n\nPlease verify the user email address or account ID and try again.",
                "data": {"found": False, "target": target_name},
                "tool_calls": [{"tool": "search_user", "query": target_query, "found": 0}]
            }

        selected_user = users[0]
        email = selected_user.get("email", "")
        logins = get_user_logins(user_email=email) if email else []

        summary_parts = [f"Retrieved identity context for **{selected_user.get('name', 'User')}**:\n"]
        summary_parts.append(format_user_summary(selected_user))
        
        if logins:
            summary_parts.append("\n#### 🔐 Authentication Activity History:")
            for l in logins:
                status_icon = "✅" if l.get("status") == "SUCCESS" else "❌"
                summary_parts.append(
                    f"- {status_icon} `{l.get('timestamp')}` | Location: **{l.get('location')}** (`{l.get('ip_address')}`) | Method: `{l.get('auth_type')}` | Reason: *{l.get('failure_reason')}*"
                )

        return {
            "agent": "Identity Agent",
            "response": "\n".join(summary_parts),
            "data": {"user": selected_user, "logins": logins},
            "tool_calls": [
                {"tool": "search_user", "query": target_query, "found": len(users)},
                {"tool": "get_user_logins", "user_email": email, "logins_count": len(logins)}
            ]
        }
