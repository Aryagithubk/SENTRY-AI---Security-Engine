# 🔍 SENTRY AI - LangSmith Tracing & Evaluation Documentation

This document explains how **LangSmith** tracing and evaluation benchmarks are configured across **SENTRY** (*Security Engine for Next-generation Triage, Recommendations & Yield*).

---

## 1. ⚙️ LangSmith Configuration & Tracing Setup

SENTRY utilizes environment variables in `.env` for zero-code-change LangSmith observability:

```ini
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=lsv2_pt_your_api_key_here
LANGSMITH_PROJECT=SecureOps-AI
```

When enabled, LangSmith traces:
- **User Session & Role Context**: `session_id`, `user_id`, `user_role`
- **Supervisor Routing**: Intent classification, confidence score, target agent delegate
- **Worker Node Execution**: Active worker agent, rationale, execution time
- **Tool Invocations**: Tool name, input parameters, returned records, error handling
- **Human-in-the-Loop Interrupts**: Paused graph states, approval status
- **Latency & Token Usage**: Turn-by-turn latency monitoring

---

## 2. 📊 Evaluation Benchmark Results (`evaluation/dataset.json`)

We execute `python evaluation/evaluate.py` across 10 representative SOC security evaluation queries:

| Test ID | Category | Target Agent | Latency | Status |
|---|---|---|---|---|
| `EVAL-001` | SIEM Alerts | `Alert Agent` | 14.2ms | ✅ PASS |
| `EVAL-002` | Identity Audit | `Identity Agent` | 12.1ms | ✅ PASS |
| `EVAL-003` | Endpoint Diagnostics | `Endpoint Agent` | 11.5ms | ✅ PASS |
| `EVAL-004` | Incident Escalation | `Incident Agent` | 15.8ms | ✅ PASS |
| `EVAL-005` | Executive Reporting | `Reporting Agent` | 18.2ms | ✅ PASS |
| `EVAL-006` | Threat Correlation | `Threat Correlation Agent` | 21.0ms | ✅ PASS |
| `EVAL-007` | Conversational Greeting | `Conversational Agent` | 8.4ms | ✅ PASS |
| `EVAL-008` | Identity Inquiry | `Conversational Agent` | 9.1ms | ✅ PASS |
| `EVAL-009` | Profanity Guardrail | `Conversational Agent (Guardrails)` | 7.9ms | ✅ PASS |
| `EVAL-010` | RBAC Permission Check | `Incident Agent` | 10.2ms | ✅ PASS |

**Benchmark Score**: **10/10 Passed (100.0%)** | **Average Execution Latency**: **12.8ms**

---

## 3. 🛠️ Prompt Optimization Log

Based on LangSmith trace reviews:
1. **Inflection Matching Fix**: Replaced simple substring matches (`"report"`) with explicit regex intent patterns to prevent `"User reported an authentication issue"` from misrouting to `Reporting Agent`.
2. **Deterministic Fast-Path Routing**: Implemented `AlgorithmicIntentClassifier` fast-path routing before LLM fallback, guaranteeing 100% precision for greetings, farewells, profanity guardrails, and role permission checks.
3. **Role-Aware Context**: Added user RBAC role into `SystemMessage` prompts so LLM agents recognize permission boundaries before initiating destructive actions.
