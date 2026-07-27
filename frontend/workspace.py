"""Investigation workspace presentation."""

import streamlit as st

from backend.services.investigation_workspace import InvestigationWorkspaceService


def render_investigation_workspace():
    """Present persisted investigation data with shared UI components."""
    user = st.session_state.get("user", {})
    role_display = user.get("role_display", "L1 SOC Analyst")
    workspace = InvestigationWorkspaceService.get_or_create_workspace(
        assigned_user=user.get("email", "alex.m@securetech.com"), assigned_role=role_display
    )

    st.markdown("## Active SOC investigation")
    st.caption(
        f"Investigation `{workspace['investigation_id']}` · Assigned to {workspace['assigned_analyst']} ({workspace['analyst_role']})"
    )
    metrics = st.columns(4)
    with metrics[0]:
        st.metric("Assessed risk", workspace["risk_level"], delta=f"{workspace['composite_risk_score']}/100")
    with metrics[1]:
        st.metric("AI confidence", f"{workspace['confidence_pct']}%", delta="Multi-source correlated")
    with metrics[2]:
        st.metric("Correlated alerts", len(workspace["matched_alerts"]))
    with metrics[3]:
        st.metric("Target host health", workspace["target_host"].get("health_status", "N/A"), delta=workspace["target_host"].get("hostname", "Environment scope"))

    attack_tab, timeline_tab, explain_tab, handoff_tab, ask_tab = st.tabs(
        ["Attack chain", "Threat timeline", "Evidence summary", "Analyst handoff", "Ask investigation"]
    )
    with attack_tab:
        st.markdown("### Correlated attack chain")
        st.caption("Evidence across threat intelligence, identity, endpoint, and firewall sources.")
        for index, node in enumerate(workspace["attack_chain"], start=1):
            st.markdown(
                f"""
                <article class="attack-chain-node">
                    <div class="attack-chain-head">
                        <span class="attack-chain-title">{node.get('icon', '•')} Step {index}: {node['title']}</span>
                        <span class="severity-badge">{node['status']}</span>
                    </div>
                    <p>{node['description']}</p>
                </article>
                """,
                unsafe_allow_html=True,
            )
            if index < len(workspace["attack_chain"]):
                st.markdown('<div class="chain-connector" aria-hidden="true">↓</div>', unsafe_allow_html=True)

    with timeline_tab:
        st.markdown("### Chronological threat events")
        for event in workspace["timeline"]:
            is_critical = event.get("severity") == "CRITICAL"
            st.markdown(
                f"""
                <article class="timeline-event {'critical' if is_critical else ''}">
                    <div class="timeline-meta">{event.get('timestamp')} · {event.get('severity')} · {event.get('source')}</div>
                    <div class="timeline-title">{event.get('event')}</div>
                    <div class="audit-event-detail">{event.get('description')} (TTP: <code>{event.get('ttp')}</code>)</div>
                </article>
                """,
                unsafe_allow_html=True,
            )

    with explain_tab:
        explanation = workspace["explainability"]
        st.markdown("### Evidence-based recommendation")
        st.markdown(f"#### {explanation['title']}")
        st.metric("AI confidence", explanation["confidence_score"])
        st.markdown("**Evidence considered**")
        for reason in explanation["reasons"]:
            st.markdown(f"- {reason}")
        st.info(f"Recommended next step: {explanation['recommended_next_step']}")

    with handoff_tab:
        st.markdown("### Analyst-to-analyst handoff")
        st.caption("Generate a structured transfer brief from the current evidence.")
        with st.form("handoff_form"):
            target_analyst = st.selectbox(
                "Transfer investigation to",
                options=["david.m@securetech.com (L2 Threat Hunter)", "sarah.c@securetech.com (SOC Manager / Incident Commander)"],
            )
            notes = st.text_area("Analyst notes", placeholder="Summarise evidence, containment status, and the recommended next step.")
            submit_handoff = st.form_submit_button("Generate handoff brief and transfer", use_container_width=True)
            if submit_handoff:
                destination_role = "L2 Threat Hunter" if "L2" in target_analyst else "SOC Manager"
                handoff = InvestigationWorkspaceService.generate_analyst_handoff(
                    investigation_id=workspace["investigation_id"], from_user=user.get("email", "analyst"),
                    from_role=role_display, to_user=target_analyst.split(" ")[0], to_role=destination_role,
                    handoff_notes=notes,
                )
                st.success("Investigation transferred successfully.")
                st.markdown(handoff)

    with ask_tab:
        st.markdown("### Ask the investigation")
        st.caption("Query the collected evidence without rerunning external search tools.")
        question = st.text_input("Question", placeholder="Why is this incident high risk? Show the event timeline.")
        if question:
            st.markdown(InvestigationWorkspaceService.ask_investigation(workspace["investigation_id"], question))
