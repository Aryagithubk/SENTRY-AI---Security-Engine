import streamlit as st
from backend.services.auth_service import AuthService
from backend.services.audit_service import AuditService

ROLE_MAP = {
    "L1 SOC Analyst": "L1",
    "L2 SOC Analyst & Threat Hunter": "L2",
    "SOC Manager / Incident Commander": "MANAGER",
    "CISO / Security Executive": "CISO",
    "Security Administrator": "ADMIN"
}

def render_login_page():
    """Render enterprise login page requiring username/email, password, and role selection."""
    st.markdown(
        """
        <div style="text-align: center; padding: 2rem 0 1rem 0;">
            <div style="display: inline-flex; align-items: center; justify-content: center; width: 75px; height: 75px; background: radial-gradient(circle, rgba(168, 85, 247, 0.4) 0%, rgba(6, 182, 212, 0.2) 100%); border: 2px solid #A855F7; border-radius: 50%; box-shadow: 0 0 30px rgba(168, 85, 247, 0.5); margin-bottom: 1rem;">
                <svg viewBox="0 0 24 24" fill="none" width="42" height="42" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2L3 7V12C3 17.55 7.16 22.74 12 24C16.84 22.74 21 17.55 21 12V7L12 2Z" fill="url(#login-shield-grad)" stroke="#A855F7" stroke-width="1.5"/>
                    <path d="M12 6L17 9V12C17 15.5 14.8 18.8 12 19.8C9.2 18.8 7 15.5 7 12V9L12 6Z" stroke="#06B6D4" stroke-width="1.5"/>
                    <defs>
                        <linearGradient id="login-shield-grad" x1="3" y1="2" x2="21" y2="24" gradientUnits="userSpaceOnUse">
                            <stop offset="0%" stop-color="#A855F7"/>
                            <stop offset="100%" stop-color="#06B6D4"/>
                        </linearGradient>
                    </defs>
                </svg>
            </div>
            <h1 style="background: linear-gradient(135deg, #06B6D4 0%, #A855F7 50%, #EC4899 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; font-size: 2.5rem; margin: 0;">SENTRY AI</h1>
            <p style="color: #06B6D4; font-weight: 600; letter-spacing: 0.5px; margin-top: 0.25rem;">Security Engine for Next-generation Triage, Recommendations & Yield</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 🔐 Enterprise Portal Login")
        st.caption("Enter your credentials, select your organizational role, and authenticate against the SQLite database:")

        with st.form("login_form"):
            username_input = st.text_input("Username or Corporate Email", placeholder="e.g. analyst_l1 or alex.m@securetech.com")
            password_input = st.text_input("Password", type="password", placeholder="••••••••")
            
            selected_role_label = st.selectbox(
                "Logging In As (Role Selection)",
                options=list(ROLE_MAP.keys()),
                index=0,
                help="Select your assigned organizational role. SENTRY verifies credentials and role assignment against the SQLite database."
            )
            
            submit_login = st.form_submit_button("Authenticate & Log In to SENTRY", use_container_width=True)

            if submit_login:
                role_code = ROLE_MAP[selected_role_label]
                user = AuthService.authenticate(
                    username_or_email=username_input,
                    password=password_input,
                    selected_role_code=role_code
                )
                
                if user:
                    st.session_state["authenticated"] = True
                    st.session_state["user"] = user
                    AuditService.log_event(
                        user_id=user["username"],
                        user_role=user["role"],
                        action="LOGIN",
                        result="SUCCESS",
                        details=f"User authenticated successfully via SQLite database as {user['role_display']}"
                    )
                    st.rerun()
                else:
                    st.error("❌ Authentication Failed: Invalid Username/Email, Password, or Role Selection. Please check the reference table below.")

        st.markdown("---")
        st.caption("🔒 **Enterprise Security Notice**: Access to SENTRY is restricted to authorized SOC personnel. All login attempts are authenticated against the SQLite security database and logged for compliance auditing.")
