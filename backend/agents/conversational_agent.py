import re
from typing import Dict, Any
from backend.services.llm import get_llm
from backend.utils.logger import log_stage
from langchain_core.messages import SystemMessage, HumanMessage

SENTRY_IDENTITY = """I am **SENTRY** (*Security Engine for Next-generation Triage, Recommendations & Yield*), your AI-powered Security Operations Center Assistant.

### 🛡️ How I Can Assist You:
1. **🚨 SIEM Alert Triage**: Search & analyze critical security alerts, MITRE ATT&CK TTPs, and threat severity.
2. **👤 Identity & Access Audits**: Inspect user risk scores, authentication history, impossible travel, and MFA status.
3. **💻 Endpoint Diagnostics**: Monitor workstation health, EDR telemetry, process execution, and host compromise status.
4. **⚠️ Incident Escalation & Containment**: Trigger security ticket creation and host isolation with Human-in-the-Loop authorization.
5. **📄 Executive CISO Reporting**: Generate multi-source root cause analyses ("What Happened") and remediation playbooks ("What's the Remedy").

*How can I help protect your enterprise infrastructure today?*"""

PROFANITY_PATTERNS = [
    r"\b(fuck|bitch|bastard|asshole|shit)\b"
]

GREETING_PATTERNS = [
    r"\b(hi|hello|hey|greetings|good\s*morning|good\s*afternoon|good\s*evening|namaste|ssup|yo)\b"
]

FAREWELL_PATTERNS = [
    r"\b(bye|goodbye|cya|see\s*you|take\s*care|exit|quit|thanks|thank\s*you)\b"
]

IDENTITY_PATTERNS = [
    r"\b(who\s*are\s*you|what\s*is\s*your\s*name|what\s*can\s*you\s*do|help|sentry)\b"
]

class ConversationalAgent:
    """
    Conversational Agent handling greetings, farewells, profanity guardrails, 
    and general inquiries under the SENTRY AI security identity.
    """

    def __init__(self, provider: str = None):
        self.provider = provider

    def execute(self, query: str) -> Dict[str, Any]:
        q_lower = query.lower().strip()
        log_stage("Conversational Agent", f"Processing general query: '{query}'")

        # 1. Check Profanity / Abusive Language Guardrail
        for pattern in PROFANITY_PATTERNS:
            if re.search(pattern, q_lower):
                log_stage("Guardrail Triggered", "Profanity/abusive language detected", level="warning")
                return {
                    "agent": "Conversational Agent (Guardrails)",
                    "response": "⚠️ **Professional Conduct Reminder**\n\nI am **SENTRY** (*Security Engine for Next-generation Triage, Recommendations & Yield*). Please maintain professional language in the Security Operations Console.\n\nLet me know how I can assist you with your threat hunting or security investigation tasks.",
                    "data": {"guardrail": "PROFANITY_TRIGGERED"},
                    "tool_calls": []
                }

        # 2. Check Greetings
        for pattern in GREETING_PATTERNS:
            if re.search(pattern, q_lower):
                return {
                    "agent": "Conversational Agent",
                    "response": f"👋 **Hello!**\n\n{SENTRY_IDENTITY}",
                    "data": {"type": "GREETING"},
                    "tool_calls": []
                }

        # 3. Check Identity / Help Inquiries
        for pattern in IDENTITY_PATTERNS:
            if re.search(pattern, q_lower):
                return {
                    "agent": "Conversational Agent",
                    "response": SENTRY_IDENTITY,
                    "data": {"type": "IDENTITY_HELP"},
                    "tool_calls": []
                }

        # 4. Check Farewells
        for pattern in FAREWELL_PATTERNS:
            if re.search(pattern, q_lower):
                return {
                    "agent": "Conversational Agent",
                    "response": "👋 **Goodbye!** Thank you for using **SENTRY** (*Security Engine for Next-generation Triage, Recommendations & Yield*). Stay vigilant and stay secure!",
                    "data": {"type": "FAREWELL"},
                    "tool_calls": []
                }

        # 5. Out-of-Scope Off-Topic General Conversations
        try:
            llm = get_llm(self.provider)
            system_prompt = """You are SENTRY (Security Engine for Next-generation Triage, Recommendations & Yield), an enterprise AI Security Operations Assistant. 
The user has asked a general or off-topic question. Respond politely in 2-3 sentences as SENTRY, answering their question briefly if appropriate, but gently steering the user back to Security Operations (threat hunting, user audits, endpoint checks, or executive reports)."""
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=query)
            ]
            response = llm.invoke(messages)
            content = response.content.strip()
            
            return {
                "agent": "Conversational Agent",
                "response": content,
                "data": {"type": "GENERAL_OUT_OF_SCOPE"},
                "tool_calls": []
            }
        except Exception:
            return {
                "agent": "Conversational Agent",
                "response": f"I am **SENTRY** (*Security Engine for Next-generation Triage, Recommendations & Yield*).\n\nI am specialized in enterprise cybersecurity operations, threat hunting, user identity audits, and host diagnostics.\n\nPlease ask a security query (e.g. *'Show all critical alerts'*, *'Check login history for johndoe@securetech.com'*, or *'Generate executive report'*).",
                "data": {"type": "OUT_OF_SCOPE_FALLBACK"},
                "tool_calls": []
            }
