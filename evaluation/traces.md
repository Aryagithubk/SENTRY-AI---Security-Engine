# 🔍 Tracing Log Samples

```json
[
  {
    "trace_id": "tr-001",
    "timestamp": "2026-07-25T17:35:10Z",
    "user_query": "Check impossible travel for johndoe@securetech.com",
    "supervisor_routing": {
      "agent": "Identity Agent",
      "reason": "Query requests user authentication logs and impossible travel check"
    },
    "tool_calls": [
      {"tool": "search_user", "query": "johndoe@securetech.com", "found": 1},
      {"tool": "get_user_logins", "user_email": "johndoe@securetech.com", "logins_count": 4}
    ],
    "status": "SUCCESS",
    "latency_ms": 195
  },
  {
    "trace_id": "tr-002",
    "timestamp": "2026-07-25T17:35:45Z",
    "user_query": "Create security incident ticket for host WS-FINANCE-04",
    "supervisor_routing": {
      "agent": "Incident Agent",
      "reason": "Query requests incident creation"
    },
    "hitl_interruption": {
      "requires_approval": true,
      "pending_action": "CREATE_INCIDENT",
      "status": "WAITING_FOR_ANALYST"
    },
    "status": "HITL_REQUIRED",
    "latency_ms": 85
  }
]
```
