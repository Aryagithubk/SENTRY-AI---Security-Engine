from typing import Dict, Any, Optional

class HumanInTheLoopController:
    """Manages confirmation state for critical security actions."""

    def __init__(self):
        self.pending_action: Optional[Dict[str, Any]] = None

    def request_approval(self, action_type: str, details: Dict[str, Any]) -> Dict[str, Any]:
        self.pending_action = {
            "action_type": action_type,
            "details": details,
            "status": "PENDING"
        }
        return self.pending_action

    def approve(self) -> Dict[str, Any]:
        if not self.pending_action:
            return {"status": "NO_PENDING_ACTION"}
        self.pending_action["status"] = "APPROVED"
        action = self.pending_action
        self.pending_action = None
        return action

    def reject(self) -> Dict[str, Any]:
        if not self.pending_action:
            return {"status": "NO_PENDING_ACTION"}
        self.pending_action["status"] = "REJECTED"
        action = self.pending_action
        self.pending_action = None
        return action
