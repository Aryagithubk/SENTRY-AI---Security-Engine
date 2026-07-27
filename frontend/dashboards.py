import streamlit as st
from backend.services.api_client import SOCApiClient

client = SOCApiClient()

def render_role_dashboard():
    """Render role-tailored dashboard based on authenticated user's RBAC role."""
    user = st.session_state.get("user", {})
    role = user.get("role", "L1")
    role_display = user.get("role_display", "L1 SOC Analyst")

    st.markdown(
        f'''<section class="dashboard-hero"><div><span>SECURITY POSTURE / {role.upper()}</span>
        <h1>{role_display}</h1><p>{user.get('name')} · {user.get('department', 'Security Operations')}</p></div>
        <div class="hero-status"><i></i> LIVE TELEMETRY</div></section>''',
        unsafe_allow_html=True,
    )

    alerts = client.get_alerts()
    incidents = client.get_incidents()
    endpoints = client.get_endpoints()
    users = client.get_users()

    if role == "L1":
        _render_l1_dashboard(alerts, endpoints)
    elif role == "L2":
        _render_l2_dashboard(alerts, incidents, endpoints, users)
    elif role == "MANAGER":
        _render_manager_dashboard(alerts, incidents, endpoints)
    elif role == "CISO":
        _render_ciso_dashboard(alerts, incidents)
    elif role == "ADMIN":
        _render_admin_dashboard()
    else:
        _render_l1_dashboard(alerts, endpoints)

def _render_l1_dashboard(alerts, endpoints):
    st.markdown("### SIEM alert queue & triage")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Assigned Open Alerts", len(alerts))
    with col2:
        st.metric("Critical Alerts", sum(1 for a in alerts if a.get("severity") == "CRITICAL"))
    with col3:
        st.metric("Endpoints Monitored", len(endpoints))

    st.markdown("#### Active queue")
    for a in alerts[:5]:
        st.markdown(f"- **[{a.get('severity')}] {a.get('alert_id')}**: `{a.get('title')}` (User: `{a.get('user_email')}` | Host: `{a.get('hostname')}`)")

def _render_l2_dashboard(alerts, incidents, endpoints, users):
    st.markdown("### Threat hunting & correlation")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Active Campaigns", "2 Correlated")
    with col2:
        st.metric("High-Risk Users", sum(1 for u in users if u.get("risk_score", 0) > 70))
    with col3:
        st.metric("Compromised Endpoints", sum(1 for ep in endpoints if ep.get("health_status") == "COMPROMISED"))

    st.markdown("#### High-risk entities")
    for u in users:
        if u.get("risk_score", 0) > 70:
            st.warning(f"👤 **{u.get('name')}** (`{u.get('email')}`) | Risk Score: **{u.get('risk_score')}/100** | Status: `{u.get('account_status')}`")

def _render_manager_dashboard(alerts, incidents, endpoints):
    st.markdown("### Incident response command")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Active Incident Tickets", len(incidents))
    with col2:
        st.metric("Pending Escalations", "1 HITL Required")
    with col3:
        st.metric("Host Containment Rules", "1 Active Rule")

    st.markdown("#### Escalation queue")
    for inc in incidents:
        st.markdown(f"🚨 **Incident Ticket {inc.get('incident_id')}**: `{inc.get('title')}` | Severity: **`{inc.get('severity')}`** | Affected Host: `{inc.get('affected_host')}`")

def _render_ciso_dashboard(alerts, incidents):
    st.markdown("### Enterprise security posture")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Overall Security Posture", "ELEVATED RISK", delta="Requires Response", delta_color="inverse")
    with col2:
        st.metric("Critical Threat Campaigns", "1 Active (APT29)")
    with col3:
        st.metric("Mean Time to Contain (MTTC)", "14.2 Minutes")

    st.markdown("#### Executive threat brief")
    st.info("📊 **Campaign Threat Brief**: Active multi-stage LockBit Ransomware & Cobalt Strike C2 campaign detected targeting Sales and Finance endpoints (`WS-FINANCE-04`). Host network isolation initiated.")

def _render_admin_dashboard():
    st.markdown("### System administration & role governance")
    st.markdown("User Role Configuration & Permissions Matrix:")
    st.json({
        "analyst_l1": "L1 SOC Analyst (View Alerts, Users, Endpoints)",
        "analyst_l2": "L2 SOC Analyst & Threat Hunter (Threat Hunting, Correlation, Reports)",
        "manager": "SOC Manager / Incident Commander (Incident Creation, Escalation, HITL Approvals)",
        "ciso": "CISO / Security Executive (Executive Summaries, Risk Posture)",
        "admin": "Security Administrator (System Config, Audit Logs)"
    })
