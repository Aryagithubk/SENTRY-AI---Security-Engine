import json
from typing import List, Dict, Any, Optional
from backend.config import (
    ALERTS_FILE, USERS_FILE, ENDPOINTS_FILE,
    INCIDENTS_FILE, LOGIN_HISTORY_FILE, THREAT_INTEL_FILE
)

class SOCApiClient:
    """Mock REST API client for querying SOC systems & JSON databases."""

    @staticmethod
    def _read_json(filepath) -> List[Dict[str, Any]]:
        if not filepath.exists():
            return []
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def _write_json(filepath, data: List[Dict[str, Any]]) -> None:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def get_alerts(self, query: Optional[str] = None, severity: Optional[str] = None) -> List[Dict[str, Any]]:
        alerts = self._read_json(ALERTS_FILE)
        
        # Filter severity if specified
        filtered = alerts
        if severity:
            filtered = [a for a in alerts if a.get("severity", "").upper() == severity.upper()]

        if not query:
            return filtered

        # Comprehensive stop-words set
        stop_words = {
            "show", "find", "me", "all", "list", "alerts", "alert", "security", "related", 
            "events", "for", "in", "the", "last", "hours", "24", "siem", "check", "search", 
            "get", "to", "of", "on", "at", "by", "from", "with", "is", "an", "a", "or", "and",
            "severity", "high", "critical", "medium", "low"
        }
        
        # Clean query tokens
        import re
        q_tokens = [
            w.lower() for w in re.findall(r"\b\w+\b", query) 
            if w.lower() not in stop_words and len(w) > 2
        ]

        if not q_tokens:
            # Query only contained stop words & severity (e.g., "Show me all critical security alerts")
            return filtered

        results = []
        for alert in filtered:
            # Combine all text fields for comprehensive matching
            searchable_text = f"{alert.get('alert_id')} {alert.get('title')} {alert.get('description')} {alert.get('source')} {alert.get('mitre_ttp')} {alert.get('user_email')} {alert.get('hostname')} {alert.get('source_ip')} {alert.get('severity')}".lower()
            
            # Check for exact word boundary match for any token
            if any(re.search(r"\b" + re.escape(token) + r"\b", searchable_text) for token in q_tokens):
                results.append(alert)

        return results

    def get_users(self, query: Optional[str] = None) -> List[Dict[str, Any]]:
        users = self._read_json(USERS_FILE)
        if not query:
            return users
        q = query.lower().strip()

        # 1. Check for exact email address match first
        import re
        email_match = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", q)
        if email_match:
            exact_email = email_match.group(0)
            exact_users = [u for u in users if u.get("email", "").lower() == exact_email]
            return exact_users # Returns exact match if present, else empty list []

        # 2. Name, User ID, or Partial Email Search
        matched = []
        for u in users:
            email = u.get("email", "").lower()
            name = u.get("name", "").lower()
            uid = u.get("user_id", "").lower()
            dept = u.get("department", "").lower()

            if (email and (email in q or q in email)) or (name and (name in q or q in name)) or (uid and (uid in q or q in uid)) or (dept and (dept in q or q in dept)):
                matched.append(u)

        return matched

    def get_endpoints(self, query: Optional[str] = None) -> List[Dict[str, Any]]:
        endpoints = self._read_json(ENDPOINTS_FILE)
        if not query:
            return endpoints
        q = query.lower().strip()

        # 1. Check for exact hostname or IP match
        import re
        host_match = re.search(r"\b(?:WS|LAPTOP|SRV|HOST|DEV|PROD|PC|MAC|WIN)-[A-Za-z0-9-]+\b", q, re.I)
        ip_match = re.search(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", q)

        if host_match:
            target_h = host_match.group(0).lower()
            exact_hosts = [ep for ep in endpoints if ep.get("hostname", "").lower() == target_h]
            return exact_hosts

        if ip_match:
            target_ip = ip_match.group(0)
            exact_ips = [ep for ep in endpoints if ep.get("ip_address", "") == target_ip]
            return exact_ips

        # 2. Assigned User Search
        email_match = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", q)
        if email_match:
            target_em = email_match.group(0)
            return [ep for ep in endpoints if ep.get("assigned_user", "").lower() == target_em]

        matched = []
        for ep in endpoints:
            host = ep.get("hostname", "").lower()
            epid = ep.get("endpoint_id", "").lower()

            if (host and host in q) or (epid and epid in q):
                matched.append(ep)

        return matched

    def get_login_history(self, user_email: Optional[str] = None) -> List[Dict[str, Any]]:
        logins = self._read_json(LOGIN_HISTORY_FILE)
        if not user_email:
            return logins
        return [l for l in logins if user_email.lower() in l.get("user_email", "").lower()]

    def lookup_ip_or_hash(self, indicator: str) -> Optional[Dict[str, Any]]:
        threats = self._read_json(THREAT_INTEL_FILE)
        ind_clean = indicator.strip().lower()
        for t in threats:
            if t.get("indicator", "").lower() == ind_clean:
                return t
        return None

    def get_incidents(self, incident_id: Optional[str] = None) -> List[Dict[str, Any]]:
        incidents = self._read_json(INCIDENTS_FILE)
        if not incident_id:
            return incidents
        return [i for i in incidents if i.get("incident_id", "").upper() == incident_id.upper()]

    def create_incident(self, title: str, severity: str, affected_user: str, affected_host: str, summary: str, related_alerts: List[str]) -> Dict[str, Any]:
        incidents = self._read_json(INCIDENTS_FILE)
        new_id = f"INC-2026-{len(incidents) + 1:03d}"
        import datetime
        now_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        new_inc = {
            "incident_id": new_id,
            "created_at": now_str,
            "title": title,
            "severity": severity.upper(),
            "status": "OPEN",
            "assigned_analyst": "SOC AI Assistant (Assigned)",
            "affected_user": affected_user,
            "affected_host": affected_host,
            "related_alerts": related_alerts,
            "summary": summary,
            "recommended_actions": [
                "Isolate affected workstation host",
                "Revoke compromise user tokens",
                "Perform full threat hunting scan"
            ]
        }
        incidents.append(new_inc)
        self._write_json(INCIDENTS_FILE, incidents)
        return new_inc
