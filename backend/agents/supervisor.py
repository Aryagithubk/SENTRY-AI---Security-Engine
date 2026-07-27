from typing import Dict, Any, Literal, Tuple, Optional
from pydantic import BaseModel
from backend.prompts.supervisor_prompt import SUPERVISOR_PROMPT
from backend.services.llm import get_llm
from backend.utils.intent_classifier import AlgorithmicIntentClassifier
from backend.utils.logger import log_stage
from langchain_core.messages import SystemMessage, HumanMessage


class RoutingDecision(BaseModel):
    """Validated structured response returned by the supervisor LLM."""

    agent: Literal[
        "Conversational Agent", "Alert Agent", "Identity Agent", "Endpoint Agent",
        "Incident Agent", "Reporting Agent", "Threat Correlation Agent",
    ]
    reason: str = "Routed based on query intent"

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

        # Guardrails are deterministic.  All other requests are delegated to
        # the selected LLM so the supervisor can make an actual routing choice.
        alg_agent, alg_score, alg_reason = AlgorithmicIntentClassifier.classify(query)
        is_guardrail = alg_reason.startswith("Matched conversational") or alg_reason.startswith("Matched profanity")
        if is_guardrail:
            log_stage("Supervisor Fast-Path", f"User: {(auth_context or {}).get('username')} ({user_role}) | Query: '{query}' -> Routed to: '{alg_agent}' ({alg_reason})")
            return alg_agent, alg_reason

        # Offline mode has no reasoning model.  Its deterministic router is a
        # clearly labelled fallback, not the normal orchestration path.
        if self.provider == "mock":
            log_stage("Supervisor Offline Routing", f"Query: '{query}' -> Routed to: '{alg_agent}' ({alg_reason})")
            return alg_agent, alg_reason

        # LLM supervisor decision with deterministic fallback on provider or
        # structured-output failure.
        try:
            llm = get_llm(self.provider)
            prompt_content = f"{SUPERVISOR_PROMPT}\nUser Role: {user_role}"
            messages = [
                SystemMessage(content=prompt_content),
                HumanMessage(content=f"User Query: {query}")
            ]
            response = llm.invoke(messages)
            content = response.content.strip()

            # This validates an LLM response; it is not application storage.
            # Telemetry and incidents are read from SQLite via SOCApiClient.
            decision = RoutingDecision.model_validate_json(content)
            agent = decision.agent
            reason = decision.reason
            log_stage("Supervisor LLM Routing", f"User Role: {user_role} | Query: '{query}' -> Routed to: '{agent}' ({reason})")
            return agent, reason
        except Exception:
            log_stage("Supervisor Routing (Fallback)", f"Query: '{query}' -> Routed to: '{alg_agent}' (Score: {alg_score:.2f})")
            return alg_agent, alg_reason
