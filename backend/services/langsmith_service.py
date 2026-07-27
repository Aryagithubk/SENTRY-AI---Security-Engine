"""Opt-in LangSmith configuration for SecureOps LangGraph runs."""

import os
from typing import Any, Dict


class LangSmithService:
    """Normalizes LangSmith settings and builds safe LangGraph run configs."""

    @staticmethod
    def enabled() -> bool:
        tracing = os.getenv("LANGSMITH_TRACING", os.getenv("LANGCHAIN_TRACING_V2", "false")).lower()
        return tracing in {"1", "true", "yes"} and bool(os.getenv("LANGSMITH_API_KEY") or os.getenv("LANGCHAIN_API_KEY"))

    @classmethod
    def configure(cls) -> bool:
        """Configure current LangSmith environment names from legacy aliases."""
        api_key = os.getenv("LANGSMITH_API_KEY") or os.getenv("LANGCHAIN_API_KEY")
        endpoint = os.getenv("LANGSMITH_ENDPOINT") or os.getenv("LANGCHAIN_ENDPOINT")
        project = os.getenv("LANGSMITH_PROJECT") or os.getenv("LANGCHAIN_PROJECT") or "SecureOps-AI"
        if api_key:
            os.environ["LANGSMITH_API_KEY"] = api_key
            os.environ["LANGCHAIN_API_KEY"] = api_key
        if endpoint:
            os.environ["LANGSMITH_ENDPOINT"] = endpoint
            os.environ["LANGCHAIN_ENDPOINT"] = endpoint
        os.environ["LANGSMITH_PROJECT"] = project
        os.environ["LANGCHAIN_PROJECT"] = project
        if cls.enabled():
            os.environ["LANGSMITH_TRACING"] = "true"
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
            return True
        return False

    @classmethod
    def run_config(cls, role: str, provider: str) -> Dict[str, Any]:
        """LangGraph configuration propagated to LangSmith as a parent run."""
        if not cls.configure():
            return {}
        return {
            "run_name": "SecureOps Investigation",
            "tags": ["secureops", "langgraph", f"role:{role.lower()}", f"provider:{(provider or 'default').lower()}"],
            "metadata": {"application": "SecureOps-AI", "role": role},
        }
