import time
import streamlit as st
from frontend.styles import MAIN_CSS
from frontend.login import render_login_page
from frontend.sidebar import render_sidebar
from frontend.chat import render_chat_messages, render_hitl_dialog
from frontend.workspace import render_investigation_workspace
from frontend.dashboards import render_role_dashboard
from frontend.audit_view import render_audit_view
from backend.workflows.graph import SecureOpsGraph
from backend.services.audit_service import AuditService

def init_app():
    """Initialize page configuration and CSS theme."""
    st.set_page_config(
        page_title="SENTRY — Security Engine for Next-generation Triage, Recommendations & Yield",
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.markdown(MAIN_CSS, unsafe_allow_html=True)

def render_header():
    """Render top header with rotating glowing security shield, SENTRY identity, and Back to Login button."""
    user = st.session_state.get("user", {})
    
    col_hdr1, col_hdr2 = st.columns([4, 1])
    with col_hdr1:
        st.markdown(
            f"""
            <div class="soc-header">
                <div class="shield-container">
                    <svg class="rotating-shield" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 2L3 7V12C3 17.55 7.16 22.74 12 24C16.84 22.74 21 17.55 21 12V7L12 2Z" fill="url(#shield-grad)" stroke="#A855F7" stroke-width="1.5"/>
                        <path d="M12 6L17 9V12C17 15.5 14.8 18.8 12 19.8C9.2 18.8 7 15.5 7 12V9L12 6Z" stroke="#06B6D4" stroke-width="1.5" stroke-linejoin="round"/>
                        <defs>
                            <linearGradient id="shield-grad" x1="3" y1="2" x2="21" y2="24" gradientUnits="userSpaceOnUse">
                                <stop offset="0%" stop-color="#A855F7" stop-opacity="0.6"/>
                                <stop offset="50%" stop-color="#06B6D4" stop-opacity="0.4"/>
                                <stop offset="100%" stop-color="#EC4899" stop-opacity="0.6"/>
                            </linearGradient>
                        </defs>
                    </svg>
                </div>
                <div>
                    <div class="soc-title-text">SENTRY AI</div>
                    <div style="color: #06B6D4; font-size: 0.8rem; font-weight: 600; margin-top: -4px;">
                        Role: <span style="color: #A855F7;">{user.get('role_display', 'L1 Analyst')}</span> ({user.get('email', '')})
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col_hdr2:
        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
        if st.button("⬅️ Back to Login", type="secondary", use_container_width=True):
            AuditService.log_event(
                user_id=user.get("username", "user"),
                user_role=user.get("role", "L1"),
                action="NAVIGATE_BACK_TO_LOGIN",
                result="SUCCESS"
            )
            st.session_state["authenticated"] = False
            st.session_state.pop("user", None)
            st.rerun()

    st.markdown(
        """
        <div class="soc-tagline">
            ⚡ SENTRY — Security Engine for Next-generation Triage, Recommendations & Yield
        </div>
        """,
        unsafe_allow_html=True
    )

def run_main_ui():
    init_app()

    # Check Authentication Guard
    if not st.session_state.get("authenticated"):
        render_login_page()
        return

    render_sidebar()
    render_header()

    nav_choice = st.session_state.get("nav_choice", "💬 Copilot Chat")

    if nav_choice == "🕵️ Investigation Workspace":
        render_investigation_workspace()
        return
    elif nav_choice == "📊 Role Dashboard":
        render_role_dashboard()
        return
    elif nav_choice == "📜 Compliance Audit Logs":
        render_audit_view()
        return

    # Render Copilot Chat (Default View)
    render_chat_messages()
    render_hitl_dialog()

    user = st.session_state.get("user", {})
    user_auth = {
        "username": user.get("username", "analyst_l1"),
        "name": user.get("name", "Alex Mercer"),
        "email": user.get("email", "alex.m@securetech.com"),
        "role": user.get("role", "L1"),
        "role_display": user.get("role_display", "L1 SOC Analyst")
    }

    # Check for preset query or text input
    user_input = None
    if "preset_query" in st.session_state and st.session_state["preset_query"]:
        user_input = st.session_state.pop("preset_query")
    else:
        user_input = st.chat_input("Ask SENTRY AI a security query, user email, host IP, or command...")

    # Process pending HITL approval execution
    if st.session_state.get("hitl_approved"):
        st.session_state["hitl_approved"] = False
        provider = st.session_state.get("llm_provider", "ollama")
        graph = SecureOpsGraph(provider=provider)
        
        with st.status("🧠 **SENTRY AI Thinking...** Executing authorized security action...", expanded=True) as status:
            status.write("⚙️ Initializing authorized incident ticket parameters...")
            time.sleep(0.3)
            approved_query = st.session_state.pop("hitl_query", "create security incident")
            res = graph.process_query(approved_query, auth_context=user_auth, hitl_approved=True)
            status.write("✅ Incident creation confirmed in Incident Management System.")
            time.sleep(0.3)
            status.update(label="✅ **Execution Completed**", state="complete", expanded=False)

        st.session_state["messages"].append({
            "role": "assistant",
            "content": res.get("response", ""),
            "trace": res.get("execution_trace", [])
        })
        st.rerun()

    if user_input:
        # Append User Message
        st.session_state["messages"].append({"role": "user", "content": user_input})
        
        # Log user query in compliance audit log
        AuditService.log_event(
            user_id=user_auth["username"],
            user_role=user_auth["role"],
            action="QUERY_EXECUTION",
            resource=user_input[:50],
            result="SUCCESS"
        )

        provider = st.session_state.get("llm_provider", "ollama")
        graph = SecureOpsGraph(provider=provider)

        # AI Thinking & Reasoning Status Expander
        with st.status("🧠 **SENTRY AI Thinking & Reasoning...**", expanded=True) as status:
            status.write(f"🔍 **Stage 1**: Supervisor Agent evaluating query intent for role `{user_auth['role']}`...")
            time.sleep(0.35)
            status.write("🛠️ **Stage 2**: Invoking specialized worker agents & querying SIEM/EDR telemetry...")
            
            result = graph.process_query(user_input, auth_context=user_auth)
            time.sleep(0.35)

            if result.get("status") == "HITL_REQUIRED":
                status.write("⚠️ **Stage 3**: Action requires Human-in-the-Loop analyst authorization.")
                status.update(label="⚠️ **Analyst Authorization Required**", state="complete", expanded=False)
            else:
                status.write("📊 **Stage 4**: Synthesizing multi-source root cause analysis & compliance audit entry...")
                time.sleep(0.35)
                status.update(label="✅ **Multi-Agent Threat Synthesis Completed**", state="complete", expanded=False)

        # Append Assistant Response
        st.session_state["messages"].append({
            "role": "assistant",
            "content": result.get("response", ""),
            "trace": result.get("execution_trace", []),
            "stream_flag": True
        })
        
        if result.get("status") == "HITL_REQUIRED":
            result["action_details"] = {**(result.get("action_details") or {}), "query": user_input}
            st.session_state["hitl_state"] = result

        st.rerun()
