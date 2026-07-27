import re
from collections import Counter
from typing import Any, Dict, List, Optional

from backend.services.api_client import SOCApiClient


client = SOCApiClient()


class ThreatCorrelationService:
    """Evidence-driven correlation over the configured SOC telemetry sources."""

    SEVERITY_WEIGHTS = {"CRITICAL": 30, "HIGH": 18, "MEDIUM": 8, "LOW": 3}

    @staticmethod
    def _entities(query: str) -> Dict[str, Optional[str]]:
        email = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", query)
        host = re.search(r"\b(?:WS|LAPTOP|SRV|HOST|DEV|PROD|PC|MAC|WIN)-[A-Za-z0-9-]+\b", query, re.I)
        ip = re.search(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", query)
        return {
            "email": email.group(0) if email else None,
            "host": host.group(0) if host else None,
            "ip": ip.group(0) if ip else None,
        }

    @classmethod
    def correlate_investigation(
        cls,
        query: str = "",
        target_user: Optional[str] = None,
        target_host: Optional[str] = None,
        incident_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Resolve the requested scope and correlate only matching evidence.

        A global threat-hunt (no entity in the query) uses all current alerts.
        An explicit but unknown user or host returns no evidence instead of
        silently substituting a demo identity or endpoint.
        """
        entities = cls._entities(query)
        requested_user = target_user or entities["email"]
        requested_host = target_host or entities["host"] or entities["ip"]

        user_matches = client.get_users(requested_user) if requested_user else []
        host_matches = client.get_endpoints(requested_host) if requested_host else []
        user = user_matches[0] if user_matches else None
        host = host_matches[0] if host_matches else None

        # Resolve the other entity from the requested evidence, never from a
        # fixed first record in mock data.
        if user is None and host and host.get("assigned_user"):
            users = client.get_users(host["assigned_user"])
            user = users[0] if users else None
        if host is None and user:
            hosts = client.get_endpoints(user.get("email"))
            host = hosts[0] if hosts else None

        explicit_scope_missing = (requested_user and user is None) or (requested_host and host is None)
        all_alerts = client.get_alerts()
        if explicit_scope_missing:
            matched_alerts: List[Dict[str, Any]] = []
        elif user or host:
            matched_alerts = [
                alert for alert in all_alerts
                if (user and alert.get("user_email", "").lower() == user.get("email", "").lower())
                or (host and alert.get("hostname", "").lower() == host.get("hostname", "").lower())
            ]
        else:
            # A hunt with no entity is intentionally an environment-wide scope.
            matched_alerts = all_alerts

        if not matched_alerts:
            return {
                "no_evidence": True,
                "scope": {"requested_user": requested_user, "requested_host": requested_host},
                "target_user": user,
                "target_host": host,
                "matched_alerts": [],
                "timeline": [],
                "attack_chain": [],
                "explainability": {"reasons": ["No matching telemetry was found for the requested scope."], "recommended_next_step": "Verify the target identifier or broaden the investigation scope."},
            }

        indicators = []
        for alert in matched_alerts:
            indicator = alert.get("source_ip")
            if indicator and indicator != "N/A":
                intel = client.lookup_ip_or_hash(indicator)
                if intel:
                    indicators.append(intel)
        threat_intel = max(indicators, key=lambda item: item.get("confidence_score", 0), default=None)

        severity_score = sum(cls.SEVERITY_WEIGHTS.get(alert.get("severity", "").upper(), 3) for alert in matched_alerts)
        user_risk = int(user.get("risk_score", 0)) if user else 0
        host_penalty = 20 if host and host.get("health_status", "").upper() == "COMPROMISED" else 0
        composite_risk = min(100, round(severity_score + (user_risk * 0.25) + host_penalty))
        risk_level = "CRITICAL" if composite_risk >= 85 else "HIGH" if composite_risk >= 60 else "MEDIUM" if composite_risk >= 30 else "LOW"
        confidence_pct = min(98, 55 + (len(matched_alerts) * 7) + (15 if user else 0) + (15 if host else 0) + (10 if threat_intel else 0))

        timeline = sorted(({
            "timestamp": alert.get("timestamp"), "event": alert.get("title"), "severity": alert.get("severity"),
            "description": alert.get("description"), "ttp": alert.get("mitre_ttp"), "source": alert.get("source"),
        } for alert in matched_alerts), key=lambda event: event.get("timestamp") or "")

        attack_chain = []
        if user:
            attack_chain.append({"id": "identity", "type": "IDENTITY", "title": f"Identity: {user.get('email')}", "description": f"Risk score: {user.get('risk_score', 'N/A')}/100", "status": user.get("account_status", "OBSERVED")})
        if host:
            attack_chain.append({"id": "endpoint", "type": "ENDPOINT", "title": f"Endpoint: {host.get('hostname')}", "description": f"Health: {host.get('health_status', 'UNKNOWN')}", "status": host.get("health_status", "OBSERVED")})
        if threat_intel:
            attack_chain.append({"id": "indicator", "type": "THREAT_INTEL", "title": f"Indicator: {threat_intel.get('indicator')}", "description": f"Attribution: {threat_intel.get('threat_actor', 'Unknown')}", "status": "MATCHED"})
        for index, alert in enumerate(matched_alerts, start=1):
            attack_chain.append({"id": f"alert-{index}", "type": "ALERT", "title": alert.get("title", "Security alert"), "description": alert.get("description", ""), "status": alert.get("severity", "OBSERVED")})

        sources = Counter(alert.get("source", "Unknown") for alert in matched_alerts)
        recommendations = []
        if host and host.get("health_status", "").upper() == "COMPROMISED":
            recommendations.append(f"Review containment options for `{host.get('hostname')}` with an authorized analyst.")
        if user and user.get("risk_score", 0) >= 70:
            recommendations.append(f"Review active sessions and authentication activity for `{user.get('email')}`.")
        if threat_intel:
            recommendations.append(f"Validate network activity involving `{threat_intel.get('indicator')}` before blocking or escalating.")
        if not recommendations:
            recommendations.append("Continue triage by validating the correlated alerts and their timestamps.")

        reasons = [f"{len(matched_alerts)} matching alert(s) were correlated across {len(sources)} telemetry source(s)."]
        if user:
            reasons.append(f"Identity evidence belongs to `{user.get('email')}` with risk score `{user.get('risk_score', 'N/A')}/100`.")
        if host:
            reasons.append(f"Endpoint evidence belongs to `{host.get('hostname')}` with health `{host.get('health_status', 'UNKNOWN')}`.")
        if threat_intel:
            reasons.append(f"Threat intelligence matched `{threat_intel.get('indicator')}` to `{threat_intel.get('threat_actor', 'Unknown')}`.")

        return {
            "scope": {"requested_user": requested_user, "requested_host": requested_host, "incident_id": incident_id},
            "target_user": user,
            "target_host": host,
            "threat_intel": threat_intel,
            "matched_alerts": matched_alerts,
            "composite_risk": composite_risk,
            "confidence_pct": confidence_pct,
            "risk_level": risk_level,
            "attack_chain": attack_chain,
            "timeline": timeline,
            "explainability": {"title": f"Evidence-based risk assessment: {risk_level} ({composite_risk}/100)", "confidence_score": f"{confidence_pct}%", "reasons": reasons, "recommended_next_step": " ".join(recommendations)},
        }
