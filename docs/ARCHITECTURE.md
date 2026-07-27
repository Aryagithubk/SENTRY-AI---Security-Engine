# 📐 SENTRY AI Architecture & System Design

SENTRY (**Security Engine for Next-generation Triage, Recommendations & Yield**) is built as an enterprise-grade multi-agent Security Operations Center (SOC) Copilot.

---

## 🏗️ Architectural Overview

```mermaid
graph TD
    User([User Analyst]) --> Login[Authentication & RBAC Service]
    Login --> UI[Streamlit UI - SENTRY Console]
    
    subgraph "LangGraph Workflow & State"
        UI --> Graph[SecureOpsGraph]
        Graph --> State[TypedDict State]
        State --> Supervisor[Supervisor Orchestrator Agent]
    end
    
    subgraph "Specialized Worker Agents"
        Supervisor --> Conv[Conversational Agent]
        Supervisor --> Alert[Alert Analysis Agent]
        Supervisor --> Ident[Identity Agent]
        Supervisor --> Endp[Endpoint Agent]
        Supervisor --> Inc[Incident Agent - HITL & RBAC]
        Supervisor --> Rep[Reporting Agent]
        Supervisor --> Corr[Threat Correlation Agent]
    end
    
    subgraph "Data & Audit Layer"
        WorkerAgents --> MockAPI[Mock Security APIs / JSON Data]
        WorkerAgents --> AuditService[Enterprise Audit Logger]
        Graph --> LangSmith[LangSmith Observability]
    end
```

---

## 🔒 Role-Based Access Control (RBAC) Permissions Matrix

| Action / Capability | L1 Analyst | L2 Threat Hunter | SOC Manager | CISO Executive | Admin |
|---|:---:|:---:|:---:|:---:|:---:|
| View SIEM Alerts & Logs | ✅ | ✅ | ✅ | ✅ | ✅ |
| Inspect User Identity & Logins | ✅ | ✅ | ✅ | ❌ | ✅ |
| Inspect Host Endpoint Telemetry | ✅ | ✅ | ✅ | ❌ | ✅ |
| Threat Hunting & Correlation | ❌ | ✅ | ✅ | ❌ | ❌ |
| Analyst Handoffs | ❌ | ✅ | ✅ | ❌ | ❌ |
| Incident Ticket Creation / Escalation | ❌ | ❌ | ✅ | ❌ | ❌ |
| Host EDR Network Isolation | ❌ | ❌ | ✅ | ❌ | ❌ |
| View Executive Summaries | ✅ | ✅ | ✅ | ✅ | ✅ |
| View System Compliance Audit Logs | ❌ | ✅ | ✅ | ✅ | ✅ |
