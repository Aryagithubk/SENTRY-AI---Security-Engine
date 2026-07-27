from typing import Dict, Any, Tuple
from backend.agents.supervisor import SupervisorAgent

class RouterWorkflow:
    """Routes execution from Supervisor Agent to target worker agents."""

    def __init__(self, provider: str = None):
        self.supervisor = SupervisorAgent(provider=provider)

    def route_query(self, query: str) -> Tuple[str, str]:
        return self.supervisor.route(query)
