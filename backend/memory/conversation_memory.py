from typing import List, Dict, Any

class ConversationMemory:
    """Manages chat conversation history and session context for SecureOps-AI."""
    
    def __init__(self):
        self.messages: List[Dict[str, Any]] = []
        self.metadata: Dict[str, Any] = {
            "session_start": "2026-07-25T17:35:00Z",
            "active_incident_id": None,
            "hitl_pending_action": None
        }

    def add_message(self, role: str, content: str, sender: str = "Assistant", tool_calls: List[Dict[str, Any]] = None):
        msg = {
            "role": role,
            "content": content,
            "sender": sender,
            "tool_calls": tool_calls or []
        }
        self.messages.append(msg)

    def get_history(self) -> List[Dict[str, Any]]:
        return self.messages

    def clear(self):
        self.messages = []
        self.metadata["active_incident_id"] = None
        self.metadata["hitl_pending_action"] = None
