"""Chat and safe execution-summary presentation components."""

import time

import streamlit as st


def stream_words(text: str):
    """Small, readable streaming effect for a newly generated response."""
    words = text.split(" ")
    for index, word in enumerate(words):
        yield word + (" " if index < len(words) - 1 else "")
        time.sleep(0.012)


def render_chat_messages():
    """Render persisted messages and safe agent execution summaries."""
    if "messages" in st.session_state and st.session_state["messages"]:
        first_message = st.session_state["messages"][0].get("content", "")
        if "Welcome to SecureOps AI" in first_message or "SecureOps AI Assistant" in first_message:
            st.session_state["messages"] = []

    if not st.session_state.get("messages"):
        st.session_state["messages"] = [{
            "role": "assistant",
            "content": (
                "**Welcome to SENTRY AI.** I can help investigate SIEM alerts, identity activity, "
                "endpoint health, incidents, and executive reporting.\n\n"
                "Ask a security question or select a runbook from the command sidebar to begin."
            ),
        }]

    for message in st.session_state["messages"]:
        avatar = "🛡️" if message["role"] == "assistant" else "👤"
        with st.chat_message(message["role"], avatar=avatar):
            trace = message.get("trace") or []
            if trace:
                with st.expander("Agent execution summary", expanded=False):
                    for step in trace:
                        stage = step.get("stage_title") or f"Stage: {step.get('step', 'Execution')}"
                        agent = step.get("agent") or step.get("decision", "Agent")
                        st.markdown(f"##### {stage}")
                        st.markdown(f"**Active agent:** `{agent}`")
                        if step.get("reason"):
                            st.caption(f"Selection summary: {step['reason']}")
                        if step.get("decision"):
                            st.caption(f"Delegated to: {step['decision']}")
                        if step.get("tool_calls"):
                            st.caption("Telemetry tools used")
                            for tool_call in step["tool_calls"]:
                                st.markdown(f"- `{tool_call.get('tool', 'Tool')}`")

                badge_markup = "".join(
                    f'<span class="trace-badge">{step.get("agent") or step.get("decision", "Agent")}</span>'
                    for step in trace
                )
                st.markdown(badge_markup, unsafe_allow_html=True)

            if message["role"] == "assistant" and message.get("stream_flag"):
                message["stream_flag"] = False
                st.write_stream(stream_words(message["content"]))
            else:
                st.markdown(message["content"])


def render_hitl_dialog():
    """Render a clear approval boundary for sensitive security operations."""
    hitl_state = st.session_state.get("hitl_state")
    if not hitl_state:
        return

    action = hitl_state.get("action_details", {})
    st.markdown(
        f"""
        <section class="hitl-panel" role="alert">
            <div class="hitl-eyebrow">HUMAN APPROVAL REQUIRED</div>
            <h3>Review proposed security action</h3>
            <p><b>{hitl_state.get('target_agent', 'Security agent')}</b> requests analyst approval before a sensitive action is performed.</p>
            <div class="hitl-meta">
                <div><span>ACTION</span><b>{action.get('action', 'Security action')}</b></div>
                <div><span>AFFECTED HOST</span><b>{action.get('target_host', 'N/A')}</b></div>
                <div><span>AFFECTED USER</span><b>{action.get('target_user', 'N/A')}</b></div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )
    approve, reject = st.columns(2)
    with approve:
        if st.button("Approve action", type="primary", use_container_width=True):
            st.session_state["hitl_approved"] = True
            st.session_state["hitl_query"] = action.get("query", "")
            st.session_state["hitl_state"] = None
            st.rerun()
    with reject:
        if st.button("Reject action", use_container_width=True):
            st.session_state["hitl_approved"] = False
            st.session_state.pop("hitl_query", None)
            st.session_state["hitl_state"] = None
            st.session_state.setdefault("messages", []).append({
                "role": "assistant",
                "content": "**Operation rejected.** The proposed security action was not performed.",
            })
            st.rerun()
