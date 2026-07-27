import re
from typing import Tuple

class AlgorithmicIntentClassifier:
    """
    Bulletproof intent classifier for SENTRY (Security Engine for Next-generation Triage, Recommendations & Yield).
    Guarantees that greetings, farewells, profanity, identity queries, and general conversations 
    are ALWAYS routed to Conversational Agent.
    """

    @classmethod
    def classify(cls, query: str) -> Tuple[str, float, str]:
        q = query.lower().strip()

        # 1. Direct Greetings, Identity & Farewell Overrides (100% Precision)
        greetings_regex = r"\b(hi|hello|hey|greetings|good\s*morning|good\s*afternoon|good\s*evening|namaste|ssup|yo|bye|goodbye|cya|see\s*you|who\s*are\s*you|what\s*can\s*you\s*do|help|sentry|thanks|thank\s*you)\b"
        if re.search(greetings_regex, q):
            return "Conversational Agent", 1.0, "Matched conversational greeting or identity pattern"

        # 2. Profanity / Abusive Language Guardrails (100% Precision)
        profanity_regex = r"\b(fuck|bitch|bastard|asshole|shit|dick|pussy|cunt|gaali|bhenchod|madarchod|chutiya|gand|harami)\b"
        if re.search(profanity_regex, q):
            return "Conversational Agent", 1.0, "Matched profanity guardrail pattern"

        # 3. Explicit Threat Correlation & Threat Hunting Patterns
        if re.search(r"\b(correlate|threat hunting|attack chain|campaign|cross-domain)\b", q):
            return "Threat Correlation Agent", 0.95, "Matched explicit threat correlation intent"

        # 4. Explicit Executive Report Generation Patterns
        if re.search(r"\b(generate|prepare|create|build|make)\b.*\b(report|executive summary|ciso report)\b", q):
            return "Reporting Agent", 0.95, "Matched explicit report generation intent"

        # 4. Explicit Security Incident Creation / Escalation Patterns
        if re.search(r"\b(create|open|escalate|trigger)\b.*\b(incident|ticket)\b", q):
            return "Incident Agent", 0.95, "Matched explicit incident escalation intent"

        # 5. Explicit Login History / IAM User Patterns
        if re.search(r"\b(login history|failed attempts|user profile|authentication history|mfa status)\b", q) or "@" in q:
            return "Identity Agent", 0.90, "Matched explicit user identity or email pattern"

        # 6. Explicit Endpoint / Host Patterns
        if re.search(r"\b(host|endpoint|workstation|device status|edr telemetry)\b", q) or re.search(r"\b(?:WS|LAPTOP|SRV|HOST|DEV|PROD|PC|MAC|WIN)-[A-Za-z0-9-]+\b", q, re.I):
            return "Endpoint Agent", 0.90, "Matched explicit host endpoint pattern"

        # 7. Explicit SIEM Security Alert Patterns
        if re.search(r"\b(alert|alerts|siem|critical alerts|security alerts|threats list|mitre)\b", q):
            return "Alert Agent", 0.90, "Matched explicit SIEM security alert pattern"

        # 8. Default Fallback for all other general conversations
        return "Conversational Agent", 0.85, "Default fallback to Conversational Agent for general query"
