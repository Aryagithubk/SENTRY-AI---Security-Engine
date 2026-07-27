import streamlit as st
from backend.services.api_client import SOCApiClient
from backend.services.audit_service import AuditService

client = SOCApiClient()

def render_sidebar():
    """Render sidebar control panel, user profile badge, navigation menu, LLM provider selector, live DB stats, and presets."""
    user = st.session_state.get("user", {})
    user_name = user.get("name", "Alex Mercer")
    user_role = user.get("role", "L1")
    role_display = user.get("role_display", "L1 SOC Analyst")

    with st.sidebar:
        st.markdown("## 🛡️ SENTRY Control Panel")
        st.markdown("---")

        # Authenticated User Badge
        st.markdown(
            f"""
            <div style="background: rgba(168, 85, 247, 0.12); border: 1px solid rgba(168, 85, 247, 0.4); border-radius: 12px; padding: 0.75rem; margin-bottom: 1rem;">
                <div style="font-weight: 700; color: #F8FAFC;">👤 {user_name}</div>
                <div style="font-size: 0.8rem; color: #06B6D4; font-weight: 600;">{role_display}</div>
                <div style="font-size: 0.75rem; color: #94A3B8; margin-top: 2px;">{user.get('email')}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Navigation Selector
        st.markdown("### 🧭 Console Navigation")
        nav_choice = st.radio(
            "Go to View",
            options=["💬 Copilot Chat", "🕵️ Investigation Workspace", "📊 Role Dashboard", "📜 Compliance Audit Logs"],
            index=0,
            label_visibility="collapsed"
        )
        st.session_state["nav_choice"] = nav_choice

        st.markdown("---")

        # LLM Engine Selector
        st.markdown("### ⚙️ LLM Provider")
        provider_option = st.selectbox(
            "Select Active Model Engine",
            options=["Ollama (Llama 3.2)", "Mock Engine (Offline)", "Google Gemini", "OpenAI"],
            index=0,
            help="Switch dynamically between local Llama 3.2 (Ollama), offline mock mode, or cloud APIs."
        )

        provider_map = {
            "Ollama (Llama 3.2)": "ollama",
            "Mock Engine (Offline)": "mock",
            "Google Gemini": "gemini",
            "OpenAI": "openai"
        }
        st.session_state["llm_provider"] = provider_map[provider_option]

        st.markdown("---")

        # Real Live Telemetry Stats
        alerts = client.get_alerts()
        incidents = client.get_incidents()
        endpoints = client.get_endpoints()

        crit_alerts = sum(1 for a in alerts if a.get("severity") == "CRITICAL")
        high_alerts = sum(1 for a in alerts if a.get("severity") == "HIGH")

        st.markdown("### 📊 Live Telemetry Stats")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total SIEM Alerts", len(alerts))
            st.metric("Open Incidents", len(incidents))
        with col2:
            st.metric("Critical / High", f"{crit_alerts} / {high_alerts}")
            st.metric("Monitored Endpoints", len(endpoints))

        st.markdown("---")

        # Preset Security Triggers
        st.markdown("### ⚡ Quick Threat Scenarios")
        st.caption("Click any preset query to trigger automated multi-agent triage:")

        scenarios = [
            ("🚨 Ransomware Detection", "Inspect endpoint status for WS-FINANCE-04"),
            ("🌐 Impossible Travel Audit", "Check login history for johndoe@securetech.com"),
            ("🕸️ Cross-Domain Hunting", "Correlate malware and suspicious network activity for WS-FINANCE-04"),
            ("⚠️ Escalate Incident (HITL)", "Create security incident ticket for host WS-FINANCE-04"),
            ("📄 Executive CISO Report", "Generate executive report for incident INC-2026-001")
        ]

        for label, query_text in scenarios:
            if st.button(label, use_container_width=True):
                st.session_state["nav_choice"] = "💬 Copilot Chat"
                st.session_state["preset_query"] = query_text

        st.markdown("---")

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("✨ Reset Session", use_container_width=True):
                st.session_state.pop("messages", None)
                st.session_state.pop("hitl_state", None)
                st.rerun()
        with col_btn2:
            if st.button("🚪 Log Out", type="secondary", use_container_width=True):
                AuditService.log_event(
                    user_id=user.get("username", "user"),
                    user_role=user.get("role", "L1"),
                    action="LOGOUT",
                    result="SUCCESS"
                )
                st.session_state.clear()
                st.rerun()
