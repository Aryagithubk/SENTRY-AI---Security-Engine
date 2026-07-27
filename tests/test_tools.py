import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from backend.tools.search_alert import search_alert
from backend.tools.search_user import search_user, get_user_logins
from backend.tools.check_endpoint import check_endpoint
from backend.tools.lookup_ip import lookup_ip
from backend.tools.create_incident import create_incident

def test_search_alert():
    alerts = search_alert()
    assert len(alerts) > 0
    crit_alerts = search_alert(severity="CRITICAL")
    assert all(a["severity"] == "CRITICAL" for a in crit_alerts)

def test_search_user():
    users = search_user(query="johndoe")
    assert len(users) == 1
    assert users[0]["email"] == "johndoe@securetech.com"

def test_get_user_logins():
    logins = get_user_logins("johndoe@securetech.com")
    assert len(logins) > 0

def test_check_endpoint():
    endpoints = check_endpoint(query="WS-FINANCE-04")
    assert len(endpoints) == 1
    assert endpoints[0]["health_status"] == "COMPROMISED"

def test_lookup_ip():
    res = lookup_ip("185.220.101.5")
    assert res is not None
    assert res["risk_level"] == "CRITICAL"

def test_create_incident():
    inc = create_incident(
        title="Test Incident",
        severity="HIGH",
        affected_user="test@securetech.com",
        affected_host="WS-TEST-01",
        summary="Test incident creation",
        related_alerts=["ALT-1001"]
    )
    assert inc["incident_id"].startswith("INC-2026-")
