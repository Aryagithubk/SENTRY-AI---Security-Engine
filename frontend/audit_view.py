"""Compliance audit presentation."""

import streamlit as st

from backend.services.audit_service import AuditService


def render_audit_view():
    """Render the existing audit records in the shared security surface system."""
    user = st.session_state.get("user", {})
    role = user.get("role", "L1")
    st.markdown("## Compliance audit trail")
    st.caption("Immutable record of logins, queries, agent tools, and human approvals.")

    if role not in ["ADMIN", "MANAGER", "L2", "CISO"]:
        st.warning("Restricted view: full audit-log inspection requires L2 Analyst, Manager, CISO, or Administrator access.")

    logs = AuditService.get_audit_logs(limit=100)
    if not logs:
        st.info("No compliance audit records have been logged yet.")
        return

    filter_user = st.text_input("Filter by user ID or email", placeholder="e.g. analyst_l1")
    filtered_logs = [event for event in logs if not filter_user or filter_user.lower() in event.get("user_id", "").lower()]
    st.caption(f"Showing {len(filtered_logs)} audit events")

    for event in filtered_logs:
        success = event.get("result") == "SUCCESS"
        result_class = "result-success" if success else "result-failure"
        st.markdown(
            f"""
            <article class="audit-event">
                <div class="audit-event-head">
                    <span class="audit-event-meta">{event.get('timestamp')} · USER: {event.get('user_id')} ({event.get('user_role')})</span>
                    <span class="result-badge {result_class}">{event.get('result')}</span>
                </div>
                <div class="audit-event-title">{event.get('action')} · <code>{event.get('resource') or 'No resource'}</code></div>
                <div class="audit-event-detail">{event.get('details') or 'No additional detail recorded.'}</div>
            </article>
            """,
            unsafe_allow_html=True,
        )
