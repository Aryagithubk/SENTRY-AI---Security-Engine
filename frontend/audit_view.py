import streamlit as st
from backend.services.audit_service import AuditService

def render_audit_view():
    """Render Enterprise Compliance Audit Log viewer with filtering options."""
    user = st.session_state.get("user", {})
    role = user.get("role", "L1")

    st.markdown("## 📜 Enterprise Compliance Audit Logs")
    st.caption("Immutable compliance audit log recording all user logins, query executions, agent tool invocations, and HITL authorization decisions:")
    st.markdown("---")

    if role not in ["ADMIN", "MANAGER", "L2", "CISO"]:
        st.warning("🔒 **Restricted View**: Full compliance audit log inspection requires L2 Analyst, Manager, or Admin privileges.")

    logs = AuditService.get_audit_logs(limit=100)

    if not logs:
        st.info("No compliance audit records logged yet.")
        return

    # Filter Bar
    filter_user = st.text_input("Filter by User ID / Email", placeholder="e.g. analyst_l1")
    
    filtered_logs = logs
    if filter_user:
        filtered_logs = [l for l in logs if filter_user.lower() in l.get("user_id", "").lower()]

    st.markdown(f"Displaying **{len(filtered_logs)}** audit events:")

    for event in filtered_logs:
        result_color = "#10B981" if event.get("result") == "SUCCESS" else "#EF4444"
        st.markdown(
            f"""
            <div style="background: rgba(14, 15, 23, 0.7); border: 1px solid rgba(168, 85, 247, 0.2); border-radius: 10px; padding: 0.75rem 1rem; margin-bottom: 0.5rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: #06B6D4;">{event.get('timestamp')} | USER: <b>{event.get('user_id')}</b> ({event.get('user_role')})</span>
                    <span style="color: {result_color}; font-weight: 700; font-size: 0.8rem;">[{event.get('result')}]</span>
                </div>
                <div style="font-weight: 700; color: #F8FAFC; margin-top: 0.25rem;">ACTION: {event.get('action')} | RESOURCE: <code>{event.get('resource')}</code></div>
                <div style="color: #94A3B8; font-size: 0.85rem; margin-top: 0.2rem;">{event.get('details')}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
