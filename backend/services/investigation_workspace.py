from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from uuid import uuid4
from backend.services.correlation_service import ThreatCorrelationService

class InvestigationWorkspaceService:
    """
    Service managing SOC Copilot Investigation Workspaces, Analyst Handoffs, 
    and direct 'Ask the Investigation' Q&A.
    """

    _active_workspaces: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def get_or_create_workspace(
        cls, 
        investigation_id: Optional[str] = None,
        assigned_user: str = "Unassigned",
        assigned_role: str = "L1 SOC Analyst",
        target_user: Optional[str] = None,
        target_host: Optional[str] = None
    ) -> Dict[str, Any]:
        """Retrieve existing workspace or synthesize a new active investigation workspace."""
        investigation_id = investigation_id or f"INV-{uuid4().hex[:8].upper()}"
        if investigation_id in cls._active_workspaces:
            return cls._active_workspaces[investigation_id]

        correlation_data = ThreatCorrelationService.correlate_investigation(
            target_user=target_user, 
            target_host=target_host,
            incident_id=investigation_id
        )

        user = correlation_data.get("target_user") or {}
        host = correlation_data.get("target_host") or {}
        workspace = {
            "investigation_id": investigation_id,
            "title": f"Evidence-based investigation: {user.get('name', 'environment scope')} / {host.get('hostname', 'environment scope')}",
            "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "status": "ACTIVE_INVESTIGATION",
            "assigned_analyst": assigned_user,
            "analyst_role": assigned_role,
            "risk_level": correlation_data.get("risk_level", "UNKNOWN"),
            "composite_risk_score": correlation_data.get("composite_risk", 0),
            "confidence_pct": correlation_data.get("confidence_pct", 0),
            "target_user": user,
            "target_host": host,
            "threat_intel": correlation_data.get("threat_intel") or {},
            "matched_alerts": correlation_data["matched_alerts"],
            "attack_chain": correlation_data["attack_chain"],
            "timeline": correlation_data["timeline"],
            "explainability": correlation_data.get("explainability", {"title": "No evidence", "confidence_score": "0%", "reasons": ["No matching telemetry was found."], "recommended_next_step": "Provide a valid investigation scope."}),
            "handoff_history": []
        }

        cls._active_workspaces[investigation_id] = workspace
        return workspace

    @classmethod
    def generate_analyst_handoff(
        cls, 
        investigation_id: str, 
        from_user: str, 
        from_role: str, 
        to_user: str, 
        to_role: str,
        handoff_notes: str = ""
    ) -> str:
        """Generate concise automated analyst handoff summary when transferring investigation."""
        ws = cls.get_or_create_workspace(investigation_id)
        ws["assigned_analyst"] = to_user
        ws["analyst_role"] = to_role

        handoff_md = f"""# 🤝 Investigation Handoff Brief
**Investigation ID**: `{investigation_id}` | **Status**: `TRANSFERRED TO {to_role.upper()}`  
**Transferred From**: `{from_user}` ({from_role}) → **To**: `{to_user}` ({to_role})  
**Handover Timestamp**: `{datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}`

---

### 📋 1. Investigation Executive Context
- **Campaign Title**: {ws['title']}
- **Assessed Risk Level**: **`{ws['risk_level']}`** (Composite Score: `{ws['composite_risk_score']}/100` | Confidence: `{ws['confidence_pct']}%`)
- **Target User Account**: `{ws['target_user'].get('email')}` (Department: `{ws['target_user'].get('department')}`)
- **Target Endpoint Device**: `{ws['target_host'].get('hostname')}` (`{ws['target_host'].get('ip_address')}`)

---

### 🔍 2. Key Findings & Correlated Evidence Summary
- **SIEM Alerts Correlated**: `{len(ws['matched_alerts'])} active alerts` (Brute force, Impossible Travel, PowerShell Payload Execution, C2 Beaconing, Ransomware Encryption).
- **Threat Actor Attribution**: `{ws['threat_intel'].get('threat_actor')}` (C2 Infrastructure: `{ws['threat_intel'].get('indicator')}`).
- **Endpoint Status**: `{ws['target_host'].get('health_status')}`.

---

### 📝 3. Outgoing Analyst Notes & Recommended Next Steps
**Notes from {from_user}**: *"{handoff_notes or 'Transferred for advanced L2 correlation, host containment authorization, and incident escalation.'}"*

**Recommended Actions for {to_user}**:
1. Review full attack chain graph in SENTRY Investigation Workspace.
2. Confirm EDR host isolation authorization for `{ws['target_host'].get('hostname')}`.
3. Trigger CISO Executive Summary report generation.
"""
        ws["handoff_history"].append({
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "from": f"{from_user} ({from_role})",
            "to": f"{to_user} ({to_role})",
            "notes": handoff_notes
        })
        return handoff_md

    @classmethod
    def ask_investigation(cls, investigation_id: str, question: str) -> str:
        """Answer analyst questions directly against active investigation context."""
        ws = cls.get_or_create_workspace(investigation_id)
        q = question.lower()

        if "why" in q or "risk" in q:
            exp = ws["explainability"]
            reasons_text = "\n".join([f"- {r}" for r in exp["reasons"]])
            return f"### 📊 Investigation Risk Analysis ({ws['risk_level']} - {ws['composite_risk_score']}/100)\n\n**Confidence Rating**: `{ws['confidence_pct']}%`\n\n**Key Evidence Factors**:\n{reasons_text}\n\n**Recommendation**: {exp['recommended_next_step']}"

        if "user" in q or "john" in q or "who" in q:
            u = ws["target_user"]
            return f"### 👤 Target User Context\n- **Name**: `{u.get('name')}`\n- **Email**: `{u.get('email')}`\n- **Department**: `{u.get('department')}`\n- **Risk Score**: `{u.get('risk_score')}/100`\n- **Status**: `{u.get('account_status')}`"

        if "host" in q or "device" in q or "endpoint" in q:
            h = ws["target_host"]
            return f"### 💻 Target Endpoint Context\n- **Hostname**: `{h.get('hostname')}`\n- **IP Address**: `{h.get('ip_address')}`\n- **OS**: `{h.get('os')}`\n- **Health Status**: `{h.get('health_status')}`"

        if "timeline" in q or "when" in q or "event" in q:
            timeline_rows = ""
            for t in ws["timeline"]:
                timeline_rows += f"- `{t.get('timestamp')}` | **[{t.get('severity')}] {t.get('event')}** (`{t.get('ttp')}`)\n"
            return f"### 🕒 Investigation Event Timeline\n{timeline_rows}"

        return f"### 🔍 Investigation Context Answer (`{investigation_id}`)\n\nRegarding your query: *'{question}'*\n\nTarget User `{ws['target_user'].get('email')}` and Endpoint `{ws['target_host'].get('hostname')}` show correlated evidence of a **{ws['risk_level']} Risk Cyber Campaign** with composite risk score `{ws['composite_risk_score']}/100`. {len(ws['matched_alerts'])} SIEM alerts were correlated."
