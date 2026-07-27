import json
from typing import Dict, Any, Tuple, Optional
from backend.prompts.supervisor_prompt import SUPERVISOR_PROMPT
from backend.services.llm import get_llm
from backend.utils.intent_classifier import AlgorithmicIntentClassifier
from backend.utils.logger import log_stage
from langchain_core.messages import SystemMessage, HumanMessage

class SupervisorAgent:
    """
    Supervisor Routing Orchestrator for SENTRY AI.
    Analyzes user intent, checks authorization permissions, and routes requests to specialized worker agents.
    """

    def __init__(self, provider: str = None):
        self.provider = provider

    def route(self, query: str, auth_context: Optional[Dict[str, Any]] = None) -> Tuple[str, str]:
        """
        Analyze query and determine appropriate agent.
        Returns: (agent_name, rationale)
        """
        user_role = (auth_context or {}).get("role", "L1")

        # 1. Deterministic Fast-Path Check using Algorithmic Intent Classifier
        alg_agent, alg_score, alg_reason = AlgorithmicIntentClassifier.classify(query)
        if alg_score >= 0.80:
            log_stage("Supervisor Fast-Path", f"User: {(auth_context or {}).get('username')} ({user_role}) | Query: '{query}' -> Routed to: '{alg_agent}' ({alg_reason})")
            return alg_agent, alg_reason

        # 2. LLM Orchestrator Reasoning Fallback
        try:
            llm = get_llm(self.provider)
            prompt_content = f"{SUPERVISOR_PROMPT}\nUser Role: {user_role}"
            messages = [
                SystemMessage(content=prompt_content),
                HumanMessage(content=f"User Query: {query}")
            ]
            response = llm.invoke(messages)
            content = response.content.strip()

            # Parse JSON decision
            data = json.loads(content)
            agent = data.get("agent", "Conversational Agent")
            reason = data.get("reason", "Routed based on query intent")
            log_stage("Supervisor LLM Routing", f"User Role: {user_role} | Query: '{query}' -> Routed to: '{agent}' ({reason})")
            return agent, reason
        except Exception:
            log_stage("Supervisor Routing (Fallback)", f"Query: '{query}' -> Routed to: '{alg_agent}' (Score: {alg_score:.2f})")
            return alg_agent, alg_reason
