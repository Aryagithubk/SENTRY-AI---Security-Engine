import time
import streamlit as st

def stream_words(text: str):
    """Word streaming generator for smooth typewriter animation."""
    words = text.split(" ")
    for i, word in enumerate(words):
        yield word + (" " if i < len(words) - 1 else "")
        time.sleep(0.012)

def render_chat_messages():
    """Render chat conversation history with glowing message borders and typewriter streaming."""
    # Reset old session messages if legacy 'SecureOps AI' welcome exists in session state
    if "messages" in st.session_state and st.session_state["messages"]:
        first_msg = st.session_state["messages"][0].get("content", "")
        if "Welcome to SecureOps AI" in first_msg or "SecureOps AI Assistant" in first_msg:
            st.session_state["messages"] = []

    if "messages" not in st.session_state or not st.session_state["messages"]:
        st.session_state["messages"] = [
            {
                "role": "assistant",
                "content": "👋 **Hello! I am SENTRY** (*Security Engine for Next-generation Triage, Recommendations & Yield*), your AI Security Operations Assistant.\n\nI am here to help you with multi-agent SIEM threat hunting, user identity audits, endpoint health diagnostics, and executive CISO reporting.\n\n*Type a query below or select a quick threat scenario from the sidebar to begin!*"
            }
        ]

    for idx, msg in enumerate(st.session_state["messages"]):
        avatar_icon = "🛡️" if msg["role"] == "assistant" else "👤"
        
        with st.chat_message(msg["role"], avatar=avatar_icon):
            # Display structured stage execution timeline if present
            if "trace" in msg and msg["trace"]:
                with st.expander("🔍 **View Multi-Agent Stage Execution Log**", expanded=False):
                    for step in msg["trace"]:
                        stage_title = step.get("stage_title") or f"Stage: {step.get('step', 'Execution')}"
                        agent_name = step.get("agent") or step.get("decision", "Agent")
                        
                        st.markdown(f"##### {stage_title}")
                        st.markdown(f"- **Active Agent**: `{agent_name}`")
                        if "reason" in step:
                            st.markdown(f"- **Routing Rationale**: *{step['reason']}*")
                        if "decision" in step:
                            st.markdown(f"- **Target Delegate**: `{step['decision']}`")
                        if "tool_calls" in step and step["tool_calls"]:
                            st.markdown("- **Invoked Tools & Telemetry Queries**:")
                            for tc in step["tool_calls"]:
                                st.markdown(f"  - 🛠️ Tool: `{tc.get('tool')}` | Parameters: `{tc}`")
                        st.markdown("---")

                # Header badge summary
                trace_html = ""
                for step in msg["trace"]:
                    agent_name = step.get("agent") or step.get("decision", "Agent")
                    trace_html += f'<span class="trace-badge">🤖 {agent_name}</span>'
                st.markdown(trace_html, unsafe_allow_html=True)
                st.markdown("")

            # Typewriter Streaming Animation for newly added assistant response
            if msg["role"] == "assistant" and msg.get("stream_flag"):
                msg["stream_flag"] = False  # Only stream once
                st.write_stream(stream_words(msg["content"]))
            else:
                st.markdown(msg["content"])

def render_hitl_dialog():
    """Render Human-in-the-Loop authorization dialog."""
    hitl_state = st.session_state.get("hitl_state")
    if hitl_state:
        st.markdown(
            f"""
            <div style="background: rgba(239, 68, 68, 0.12); border: 1px solid rgba(239, 68, 68, 0.5); border-radius: 14px; padding: 1.25rem; margin: 1rem 0; box-shadow: 0 0 20px rgba(239, 68, 68, 0.2);">
                <div style="color: #F87171; font-weight: 800; font-size: 1.1rem; margin-bottom: 0.5rem;">⚠️ Human-in-the-Loop Authorization Required</div>
                <p style="margin-bottom: 0.5rem;">The <b>{hitl_state.get('target_agent')}</b> is requesting analyst authorization for a sensitive security action:</p>
                <ul style="margin-bottom: 0.5rem;">
                    <li><b>Action</b>: Create / Escalate Security Incident Ticket</li>
                    <li><b>Target Device</b>: <code>WS-FINANCE-04</code></li>
                    <li><b>Target User</b>: <code>sarah.c@securetech.com</code></li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Authorize Action", type="primary", use_container_width=True):
                st.session_state["hitl_approved"] = True
                st.session_state["hitl_state"] = None
                st.rerun()
        with col2:
            if st.button("❌ Abort Action", use_container_width=True):
                st.session_state["hitl_approved"] = False
                st.session_state["hitl_state"] = None
                st.session_state["messages"].append({
                    "role": "assistant",
                    "content": "🚫 **Operation Aborted**: Incident creation cancelled by analyst."
                })
                st.rerun()
