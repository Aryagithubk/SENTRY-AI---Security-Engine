"""Professional command sidebar for the SENTRY SOC console."""

import streamlit as st

from backend.services.api_client import SOCApiClient
from backend.services.audit_service import AuditService
from backend.services.db_service import DatabaseService

client = SOCApiClient()


def render_sidebar():
    """Render navigation, operator context, telemetry posture, and quick actions."""
    user = st.session_state.get("user", {})
    user_name = user.get("name", "Alex Mercer")
    role_display = user.get("role_display", "L1 SOC Analyst")

    with st.sidebar:
        st.markdown(
            f'''<section class="side-brand">
                <div class="side-eyebrow"><span></span> SECURITY OPERATIONS</div>
                <h2>SENTRY <b>/</b> COMMAND</h2>
                <div class="operator-card"><div class="operator-avatar">{user_name[:1].upper()}</div>
                    <div><strong>{user_name}</strong><small>{role_display}</small><small>{user.get('email', '')}</small></div>
                    <i>ACTIVE</i>
                </div>
            </section>''',
            unsafe_allow_html=True,
        )

        st.markdown('<div class="side-section-label">WORKSPACE</div>', unsafe_allow_html=True)
        nav_choice = st.radio(
            "Workspace navigation",
            options=["Copilot", "Investigation", "Operations Dashboard", "Audit Trail"],
            label_visibility="collapsed",
        )
        st.session_state["nav_choice"] = {
            "Copilot": "💬 Copilot Chat",
            "Investigation": "🕵️ Investigation Workspace",
            "Operations Dashboard": "📊 Role Dashboard",
            "Audit Trail": "📜 Compliance Audit Logs",
        }[nav_choice]

        st.markdown('<div class="side-section-label">INTELLIGENCE ENGINE</div>', unsafe_allow_html=True)
        provider_option = st.selectbox(
            "Active inference engine",
            options=["Ollama / Llama 3.2", "Mock / Offline", "Google Gemini", "OpenAI"],
            label_visibility="collapsed",
        )
        st.session_state["llm_provider"] = {
            "Ollama / Llama 3.2": "ollama", "Mock / Offline": "mock",
            "Google Gemini": "gemini", "OpenAI": "openai",
        }[provider_option]

        alerts, incidents, endpoints = client.get_alerts(), client.get_incidents(), client.get_endpoints()
        critical = sum(1 for item in alerts if item.get("severity") == "CRITICAL")
        high = sum(1 for item in alerts if item.get("severity") == "HIGH")
        st.markdown('<div class="side-section-label">LIVE POSTURE</div>', unsafe_allow_html=True)
        st.markdown(
            f'''<div class="posture-grid">
                <div><b>{len(alerts)}</b><span>ALERTS</span></div><div><b>{critical + high}</b><span>PRIORITY</span></div>
                <div><b>{len(incidents)}</b><span>INCIDENTS</span></div><div><b>{len(endpoints)}</b><span>ENDPOINTS</span></div>
            </div>''',
            unsafe_allow_html=True,
        )

        st.markdown('<div class="side-section-label">RUNBOOKS</div>', unsafe_allow_html=True)
        scenarios = [
            ("Endpoint ransomware triage", "Inspect endpoint status for WS-FINANCE-04"),
            ("Identity anomaly review", "Check login history for johndoe@securetech.com"),
            ("Cross-domain threat hunt", "Correlate malware and suspicious network activity for WS-FINANCE-04"),
            ("Incident escalation", "Create security incident ticket for host WS-FINANCE-04"),
            ("Executive incident brief", "Generate executive report for incident INC-2026-001"),
        ]
        for label, query in scenarios:
            if st.button(label, key=f"runbook_{label}", use_container_width=True):
                st.session_state["nav_choice"] = "💬 Copilot Chat"
                st.session_state["preset_query"] = query

        st.markdown('<div class="side-footer">SENTRY CORE <span>●</span> TELEMETRY SYNCHRONIZED</div>', unsafe_allow_html=True)
        left, right = st.columns(2)
        with left:
            if st.button("Reset", use_container_width=True):
                st.session_state.pop("messages", None)
                st.session_state.pop("hitl_state", None)
                st.rerun()
        with right:
            if st.button("Sign out", use_container_width=True):
                AuditService.log_event(
                    user_id=user.get("username", "user"),
                    user_role=user.get("role", "L1"),
                    action="LOGOUT",
                    result="SUCCESS",
                )
                session_id = st.session_state.get("app_session_id")
                if session_id:
                    DatabaseService.delete_app_session(session_id)
                st.query_params.clear()
                st.session_state.clear()
                st.rerun()
