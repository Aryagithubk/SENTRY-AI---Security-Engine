import re
from datetime import datetime, timezone
from difflib import SequenceMatcher, get_close_matches
from typing import Any, Dict, List, Optional

from backend.services.db_service import DatabaseService


class SOCApiClient:
    """SQLite-backed repository for SOC telemetry and incident records."""

    @staticmethod
    def _normalise(text: Any) -> List[str]:
        return re.findall(r"[a-z0-9@._:-]+", str(text or "").lower())

    @staticmethod
    def _record_text(record: Dict[str, Any]) -> str:
        return " ".join(str(value) for value in record.values() if value is not None).lower()

    @classmethod
    def _semantic_matches(cls, records: List[Dict[str, Any]], query: Optional[str]) -> List[Dict[str, Any]]:
        if not query:
            return records
        tokens = cls._normalise(query)
        # Product words are not evidence constraints. The remaining terms are
        # scored against live database values with typo tolerance.
        ignored = {"show", "find", "list", "get", "check", "search", "security", "alert", "alerts", "severity", "sevrity", "critical", "high", "medium", "low", "all", "the", "for", "with", "and", "of", "a", "an"}
        terms = [token for token in tokens if token not in ignored and len(token) > 2]
        if not terms:
            return records
        scored = []
        for record in records:
            text = cls._record_text(record)
            words = cls._normalise(text)
            score = 0.0
            for term in terms:
                if term in text:
                    score += 1.0
                else:
                    score += max((SequenceMatcher(None, term, word).ratio() for word in words), default=0) * 0.45
            if score >= 0.65:
                scored.append((score, record))
        return [record for _, record in sorted(scored, key=lambda item: item[0], reverse=True)]

    def get_alerts(self, query: Optional[str] = None, severity: Optional[str] = None) -> List[Dict[str, Any]]:
        alerts = DatabaseService.get_records("alerts")
        available_severities = sorted({str(alert.get("severity", "")).upper() for alert in alerts if alert.get("severity")})
        requested_severity = (severity or "").upper()
        if not requested_severity and query:
            candidates = self._normalise(query)
            # Compare every user token directly with values currently stored
            # in the database. This handles both `critical` and `sevrity`.
            severity_candidates = [
                (SequenceMatcher(None, token.upper(), value).ratio(), value)
                for token in candidates
                for value in available_severities
            ]
            if severity_candidates:
                score, value = max(severity_candidates)
                if score >= 0.72:
                    requested_severity = value
        if requested_severity:
            normalised = get_close_matches(requested_severity, available_severities, n=1, cutoff=0.55)
            if normalised:
                alerts = [alert for alert in alerts if str(alert.get("severity", "")).upper() == normalised[0]]
        return self._semantic_matches(alerts, query)

    def get_users(self, query: Optional[str] = None) -> List[Dict[str, Any]]:
        return self._semantic_matches(DatabaseService.get_records("identity_users"), query)

    def get_endpoints(self, query: Optional[str] = None) -> List[Dict[str, Any]]:
        return self._semantic_matches(DatabaseService.get_records("endpoints"), query)

    def get_login_history(self, user_email: Optional[str] = None) -> List[Dict[str, Any]]:
        records = DatabaseService.get_records("login_history")
        return [record for record in records if not user_email or record.get("user_email", "").lower() == user_email.lower()]

    def lookup_ip_or_hash(self, indicator: str) -> Optional[Dict[str, Any]]:
        matches = self._semantic_matches(DatabaseService.get_records("threat_intelligence"), indicator)
        return next((record for record in matches if str(record.get("indicator", "")).lower() == indicator.lower()), None)

    def get_incidents(self, incident_id: Optional[str] = None) -> List[Dict[str, Any]]:
        incidents = DatabaseService.get_records("incidents")
        return [incident for incident in incidents if not incident_id or incident.get("incident_id", "").upper() == incident_id.upper()]

    def create_incident(self, title: str, severity: str, affected_user: str, affected_host: str, summary: str, related_alerts: List[str]) -> Dict[str, Any]:
        existing = self.get_incidents()
        sequence = max((int(match.group(1)) for incident in existing for match in [re.search(r"(\d+)$", incident.get("incident_id", ""))] if match), default=0) + 1
        incident_id = f"INC-{datetime.now(timezone.utc).year}-{sequence:03d}"
        incident = {
            "incident_id": incident_id,
            "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "title": title,
            "severity": severity.upper(),
            "status": "OPEN",
            "assigned_analyst": "SOC AI Assistant",
            "affected_user": affected_user,
            "affected_host": affected_host,
            "related_alerts": related_alerts,
            "summary": summary,
            "recommended_actions": ["Validate evidence", "Obtain required approval", "Document containment decision"],
        }
        DatabaseService.upsert_record("incidents", incident_id, incident)
        return incident
