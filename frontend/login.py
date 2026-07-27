"""Authentication view for the SENTRY security operations console."""

import streamlit as st

from backend.services.audit_service import AuditService
from backend.services.auth_service import AuthService
from backend.services.db_service import DatabaseService

ROLE_MAP = {
    "L1 SOC Analyst": "L1",
    "L2 SOC Analyst & Threat Hunter": "L2",
    "SOC Manager / Incident Commander": "MANAGER",
    "CISO / Security Executive": "CISO",
    "Security Administrator": "ADMIN",
}


def render_login_page():
    """Render the role-aware enterprise login without changing auth semantics."""
    st.markdown(
        """
        <section class="login-brand">
            <div class="login-emblem" aria-hidden="true">
                <svg viewBox="0 0 24 24" fill="none" width="42" height="42" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2L3 7V12C3 17.55 7.16 22.74 12 24C16.84 22.74 21 17.55 21 12V7L12 2Z" fill="url(#login-shield-grad)" stroke="#74bcff" stroke-width="1.5"/>
                    <path d="M12 6L17 9V12C17 15.5 14.8 18.8 12 19.8C9.2 18.8 7 15.5 7 12V9L12 6Z" stroke="#d5e9ff" stroke-width="1.5"/>
                    <defs><linearGradient id="login-shield-grad" x1="3" y1="2" x2="21" y2="24"><stop stop-color="#4ca8ff"/><stop offset="1" stop-color="#8b7cff"/></linearGradient></defs>
                </svg>
            </div>
            <h1>SENTRY AI</h1>
            <p>Security Engine for Next-generation Triage, Recommendations &amp; Yield</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    left, center, right = st.columns([1, 2, 1])
    with center:
        st.markdown(
            '<section class="login-panel"><h3>Enterprise portal login</h3>'
            '<p class="login-caption">Authenticate with your approved SOC credentials and assigned role.</p></section>',
            unsafe_allow_html=True,
        )
        with st.form("login_form"):
            username_input = st.text_input("Username or Corporate Email", placeholder="e.g. analyst_l1 or alex.m@securetech.com")
            password_input = st.text_input("Password", type="password", placeholder="Enter your password")
            selected_role_label = st.selectbox(
                "Logging In As (Role Selection)",
                options=list(ROLE_MAP.keys()),
                index=0,
                help="Select your assigned organisational role. SENTRY verifies credentials and role assignment against the SQLite database.",
            )
            submit_login = st.form_submit_button("Authenticate and enter SENTRY", use_container_width=True)

            if submit_login:
                user = AuthService.authenticate(
                    username_or_email=username_input,
                    password=password_input,
                    selected_role_code=ROLE_MAP[selected_role_label],
                )
                if user:
                    session_id = DatabaseService.create_app_session(user)
                    st.session_state["authenticated"] = True
                    st.session_state["user"] = user
                    st.session_state["app_session_id"] = session_id
                    st.query_params["session"] = session_id
                    AuditService.log_event(
                        user_id=user["username"], user_role=user["role"], action="LOGIN", result="SUCCESS",
                        details=f"User authenticated successfully via SQLite database as {user['role_display']}",
                    )
                    st.rerun()
                else:
                    st.error("Authentication failed. Check your username, password, and selected role.")

        st.markdown(
            '<p class="login-notice"><b>Security notice.</b> Access is restricted to authorised SOC personnel. '
            'Authentication is verified through the SQLite security database and recorded for compliance.</p>',
            unsafe_allow_html=True,
        )
