import streamlit as st
from backend.services.investigation_workspace import InvestigationWorkspaceService

def render_investigation_workspace():
    """Render SOC Investigation Workspace, Attack Chain Graph, Timeline, Handoffs, and Q&A."""
    user = st.session_state.get("user", {})
    user_id = user.get("username", "analyst_l1")
    user_role = user.get("role", "L1")
    role_display = user.get("role_display", "L1 SOC Analyst")

    ws = InvestigationWorkspaceService.get_or_create_workspace(
        assigned_user=user.get("email", "alex.m@securetech.com"),
        assigned_role=role_display
    )

    st.markdown("## 🕵️ Active SOC Investigation Workspace")
    st.caption(f"Investigation ID: `{ws['investigation_id']}` | Assigned Analyst: `{ws['assigned_analyst']}` ({ws['analyst_role']})")
    st.markdown("---")

    # Workspace Header Metric Card
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Assessed Risk Level", ws["risk_level"], delta=f"{ws['composite_risk_score']}/100 Risk Score", delta_color="inverse")
    with col2:
        st.metric("AI Confidence Rating", f"{ws['confidence_pct']}%", delta="Multi-Source Correlated")
    with col3:
        st.metric("Correlated Alerts", len(ws["matched_alerts"]))
    with col4:
        st.metric("Target Host Health", ws["target_host"].get("health_status", "N/A"), delta=ws["target_host"].get("hostname", "Environment scope"), delta_color="inverse")

    st.markdown("---")

    # Tabs inside Workspace
    ws_tab1, ws_tab2, ws_tab3, ws_tab4, ws_tab5 = st.tabs([
        "🔗 Attack Chain Graph", 
        "🕒 Threat Timeline", 
        "💡 Explainability ('Why?')", 
        "🤝 Analyst Handoff",
        "❓ Ask Investigation"
    ])

    with ws_tab1:
        st.markdown("### 🕸️ Graphical Attack Chain Sequence")
        st.caption("Visual representation of correlated security events across Threat Intel, Identity, EDR, and Firewall:")
        
        # Render visual attack chain nodes
        for idx, node in enumerate(ws["attack_chain"], start=1):
            st.markdown(
                f"""
                <div style="background: rgba(14, 15, 23, 0.8); border: 1px solid rgba(168, 85, 247, 0.3); border-radius: 12px; padding: 1rem; margin-bottom: 0.75rem; box-shadow: 0 4px 15px rgba(0,0,0,0.4);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 700; color: #06B6D4; font-size: 1.05rem;">{node.get('icon', '🔗')} Step {idx}: {node['title']}</span>
                        <span style="background: rgba(239, 68, 68, 0.2); border: 1px solid #EF4444; color: #F87171; padding: 2px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 700;">{node['status']}</span>
                    </div>
                    <p style="color: #94A3B8; margin-top: 0.4rem; margin-bottom: 0; font-size: 0.9rem;">{node['description']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            if idx < len(ws["attack_chain"]):
                st.markdown("<div style='text-align: center; color: #A855F7; font-size: 1.2rem; font-weight: bold;'>↓</div>", unsafe_allow_html=True)

    with ws_tab2:
        st.markdown("### 🕒 Chronological Threat Event Timeline")
        for t in ws["timeline"]:
            severity_color = "#EF4444" if t.get("severity") == "CRITICAL" else "#F59E0B"
            st.markdown(
                f"""
                <div style="border-left: 3px solid {severity_color}; padding-left: 12px; margin-bottom: 1rem;">
                    <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: #06B6D4;">{t.get('timestamp')} | [{t.get('severity')}] - {t.get('source')}</div>
                    <div style="font-weight: 700; font-size: 1rem; color: #F8FAFC; margin: 2px 0;">{t.get('event')}</div>
                    <div style="color: #94A3B8; font-size: 0.85rem;">{t.get('description')} (TTP: <code>{t.get('ttp')}</code>)</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    with ws_tab3:
        st.markdown("### 💡 AI Recommendation Justification ('Why Am I Seeing This?')")
        exp = ws["explainability"]
        st.markdown(f"#### {exp['title']}")
        st.markdown(f"**AI Confidence Level**: `{exp['confidence_score']}`")
        st.markdown("**Evidence-Based Rationale**:")
        for r in exp["reasons"]:
            st.markdown(f"- 📌 {r}")
        st.markdown("---")
        st.markdown(f"**Recommended Action**: {exp['recommended_next_step']}")

    with ws_tab4:
        st.markdown("### 🤝 Analyst-to-Analyst Investigation Handoff")
        st.caption("Generate a structured handoff brief to transfer this investigation to an L2 Threat Hunter or SOC Manager:")

        with st.form("handoff_form"):
            target_analyst = st.selectbox(
                "Transfer Investigation To",
                options=["david.m@securetech.com (L2 Threat Hunter)", "sarah.c@securetech.com (SOC Manager / Incident Commander)"],
                index=0
            )
            handoff_notes = st.text_area("Analyst Notes / Key Transfer Insights", placeholder="e.g. Correlated ransomware execution on WS-FINANCE-04. Requires host containment authorization and CISO report.")
            submit_handoff = st.form_submit_button("Generate Handoff Brief & Transfer", use_container_width=True)

            if submit_handoff:
                to_user_email = target_analyst.split(" ")[0]
                to_role = "L2 Threat Hunter" if "L2" in target_analyst else "SOC Manager"
                
                handoff_md = InvestigationWorkspaceService.generate_analyst_handoff(
                    investigation_id=ws["investigation_id"],
                    from_user=user.get("email", user_id),
                    from_role=role_display,
                    to_user=to_user_email,
                    to_role=to_role,
                    handoff_notes=handoff_notes
                )
                st.success("✅ Investigation Transferred Successfully!")
                st.markdown(handoff_md)

    with ws_tab5:
        st.markdown("### ❓ 'Ask the Investigation' Q&A")
        st.caption("Ask questions directly against collected evidence and telemetry without re-running external search tools:")

        inv_query = st.text_input("Ask a question about this active investigation...", placeholder="e.g. Why is this incident high risk? or Show me timeline")
        if inv_query:
            answer = InvestigationWorkspaceService.ask_investigation(ws["investigation_id"], inv_query)
            st.markdown(answer)
