import os
from typing import Any, List, Dict, Optional
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage
from backend.config import (
    LLM_PROVIDER, OLLAMA_MODEL, OLLAMA_BASE_URL,
    GEMINI_MODEL, OPENAI_MODEL, GOOGLE_API_KEY, OPENAI_API_KEY
)

class MockLLMEngine(BaseChatModel):
    """
    Offline Mock LLM Engine designed for high-accuracy agent simulation
    when no live API key or local Ollama server is running.
    """
    def _generate(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, **kwargs: Any) -> Any:
        from langchain_core.outputs import ChatResult, ChatGeneration
        
        last_msg = messages[-1].content if messages else ""
        system_prompt = ""
        for m in messages:
            if isinstance(m, SystemMessage):
                system_prompt = m.content

        # Clean query string to prevent false positive matching on 'User Query:' prefix
        clean_msg = last_msg.replace("User Query:", "").strip()
        content = "SecureOps-AI Assistant processing your request..."
        
        # Check supervisor routing using NLP Algorithmic Intent Classifier
        if "Supervisor" in system_prompt or "router" in system_prompt.lower():
            from backend.utils.intent_classifier import AlgorithmicIntentClassifier
            agent, score, reason = AlgorithmicIntentClassifier.classify(clean_msg)
            content = f'{{"agent": "{agent}", "reason": "{reason}"}}'

        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=content))])

    @property
    def _llm_type(self) -> str:
        return "mock-llm-engine"


def get_llm(provider: Optional[str] = None):
    """
    Factory function to retrieve LLM based on user selection or environment variable.
    Supported options: 'mock', 'ollama' (Llama 3.2), 'gemini', 'openai'
    """
    selected = (provider or LLM_PROVIDER).lower()

    if selected == "ollama" or selected == "llama3.2":
        try:
            # First try official langchain_ollama package
            from langchain_ollama import ChatOllama
            return ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL)
        except Exception as e1:
            try:
                # Direct module fallback
                from langchain_community.chat_models.ollama import ChatOllama
                return ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL)
            except Exception as e2:
                print(f"[LLM Factory] Could not initialize ChatOllama ({e1} | {e2}). Falling back to Mock Engine.")
                return MockLLMEngine()

    elif selected == "gemini":
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            api_key = GOOGLE_API_KEY or os.getenv("GOOGLE_API_KEY")
            if not api_key:
                print("[LLM Factory] GOOGLE_API_KEY missing. Falling back to Mock Engine.")
                return MockLLMEngine()
            return ChatGoogleGenerativeAI(model=GEMINI_MODEL, google_api_key=api_key)
        except Exception as e:
            print(f"[LLM Factory] Could not initialize Gemini LLM ({e}). Falling back to Mock Engine.")
            return MockLLMEngine()

    elif selected == "openai":
        try:
            from langchain_community.chat_models import ChatOpenAI
            api_key = OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
            if not api_key:
                print("[LLM Factory] OPENAI_API_KEY missing. Falling back to Mock Engine.")
                return MockLLMEngine()
            return ChatOpenAI(model=OPENAI_MODEL, openai_api_key=api_key)
        except Exception as e:
            print(f"[LLM Factory] Could not initialize OpenAI LLM ({e}). Falling back to Mock Engine.")
            return MockLLMEngine()

    # Default fallback
    return MockLLMEngine()
