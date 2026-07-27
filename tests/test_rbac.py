import pytest
from backend.services.auth_service import AuthService
from backend.services.rbac_service import RBACService
from backend.services.audit_service import AuditService

def test_auth_service_success():
    user = AuthService.authenticate("analyst_l1", "l1pass123")
    assert user is not None
    assert user["role"] == "L1"
    assert user["username"] == "analyst_l1"

def test_auth_service_failure():
    user = AuthService.authenticate("analyst_l1", "wrong_password_xyz")
    assert user is None

def test_rbac_permission_matrix():
    assert RBACService.has_permission("L1", "VIEW_ALERTS") is True
    assert RBACService.has_permission("L1", "CREATE_INCIDENT") is False
    
    assert RBACService.has_permission("MANAGER", "CREATE_INCIDENT") is True
    assert RBACService.has_permission("CISO", "VIEW_EXECUTIVE_SUMMARY") is True

def test_rbac_authorize_action():
    is_auth_l1, _ = RBACService.authorize_action("L1", "create_incident")
    assert is_auth_l1 is False

    is_auth_mgr, _ = RBACService.authorize_action("MANAGER", "create_incident")
    assert is_auth_mgr is True

def test_audit_logging():
    event = AuditService.log_event(
        user_id="test_user",
        user_role="L1",
        action="TEST_ACTION",
        resource="TEST_RESOURCE",
        result="SUCCESS"
    )
    assert event["user_id"] == "test_user"
    assert event["action"] == "TEST_ACTION"
