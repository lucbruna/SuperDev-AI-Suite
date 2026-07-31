"""Tests for the authorization subsystem (authorization/)."""

from __future__ import annotations

import pytest

from integration.authorization.access_policy import AccessPolicy
from integration.authorization.permission_engine import PermissionEngine
from integration.authorization.role_mapping import RoleMapper
from integration.authorization.scope_manager import ScopeManager
from integration.authorization.validation import PermissionValidator


class TestRoleMapper:
    def test_roles_and_permissions(self) -> None:
        roles = RoleMapper()
        roles.define_role("admin", ["*"])
        roles.define_role("viewer", ["connections:list", "api:read"])
        roles.assign("alice", "admin")
        roles.assign("bob", "viewer")
        assert roles.roles_for("alice") == ["admin"]
        assert roles.has_permission("alice", "anything") is True
        assert roles.has_permission("bob", "connections:list") is True
        assert roles.has_permission("bob", "connections:delete") is False

    def test_unassign(self) -> None:
        roles = RoleMapper()
        roles.define_role("viewer", ["api:read"])
        roles.assign("bob", "viewer")
        assert roles.unassign("bob", "viewer") is True
        assert roles.unassign("bob", "viewer") is False
        assert roles.unassign("missing-user", "viewer") is False

    def test_snapshot(self) -> None:
        roles = RoleMapper()
        roles.define_role("viewer", ["read"])
        roles.assign("bob", "viewer")
        snapshot = roles.snapshot()
        assert snapshot["users"] == 1
        assert snapshot["roles"] == 1


class TestScopeManager:
    def test_exact_and_wildcard(self) -> None:
        scopes = ScopeManager()
        assert scopes.check(["connections:connect"], "connections:connect") is True
        assert scopes.check(["connections:*"], "connections:connect") is True
        assert scopes.check(["api:read"], "connections:connect") is False
        assert scopes.check([], "anything") is False

    def test_check_any(self) -> None:
        scopes = ScopeManager()
        assert scopes.check_any(["api:read"], ["api:write", "api:read"]) is True
        assert scopes.check_any(["x"], ["api:write", "api:read"]) is False

    def test_require(self) -> None:
        scopes = ScopeManager()
        scopes.require(["connections:*"], "connections:delete")
        with pytest.raises(PermissionError):
            scopes.require(["api:read"], "connections:delete")

    def test_register(self) -> None:
        scopes = ScopeManager()
        scopes.register("connections:connect", "Connect external systems")
        assert "connections:connect" in scopes.list()


class TestAccessPolicy:
    def test_allow_and_deny(self) -> None:
        policy = AccessPolicy()
        policy.allow("read", "orders")
        assert policy.evaluate("read", "orders") is True
        assert policy.evaluate("read", "invoices") is False

    def test_deny_wins(self) -> None:
        policy = AccessPolicy()
        policy.allow("*", "orders")
        policy.deny("delete", "orders")
        assert policy.evaluate("delete", "orders") is False
        assert policy.evaluate("read", "orders") is True

    def test_conditions(self) -> None:
        policy = AccessPolicy()
        policy.allow("read", "orders", conditions={"region": "br"})
        assert policy.evaluate("read", "orders", {"region": "br"}) is True
        assert policy.evaluate("read", "orders", {"region": "us"}) is False

    def test_check_raises(self) -> None:
        policy = AccessPolicy()
        policy.allow("read", "orders")
        policy.check("read", "orders")
        with pytest.raises(PermissionError):
            policy.check("write", "orders")


class TestPermissionValidator:
    def test_validate(self) -> None:
        validator = PermissionValidator()
        validator.roles.define_role("admin", ["*"])
        validator.roles.assign("alice", "admin")
        validator.scopes.register("connections:connect")
        assert validator.check_permission("alice", "anything") is True
        assert validator.validate("alice", "connections:connect",
                                  granted_scopes=["connections:*"]) is True
        assert validator.validate("alice", "connections:connect",
                                  granted_scopes=["api:read"]) is False

    def test_enforce(self) -> None:
        validator = PermissionValidator()
        with pytest.raises(PermissionError):
            validator.enforce_permission("bob", "connections:delete")

    def test_snapshot(self) -> None:
        validator = PermissionValidator()
        validator.roles.define_role("viewer", ["read"])
        validator.roles.assign("bob", "viewer")
        snapshot = validator.snapshot()
        assert snapshot["users"] == 1
        assert snapshot["roles"] == 1


class TestPermissionEngine:
    def test_define_assign_enforce(self) -> None:
        engine = PermissionEngine()
        engine.define_role("admin", ["*"])
        engine.assign("alice", "admin")
        engine.enforce("alice", "connections:delete")
        assert engine.check("alice", "anything") is True

    def test_enforce_fails(self) -> None:
        engine = PermissionEngine()
        engine.define_role("viewer", ["connections:list"])
        engine.assign("bob", "viewer")
        with pytest.raises(PermissionError):
            engine.enforce("bob", "connections:delete")
        with pytest.raises(PermissionError):
            engine.enforce("bob", "connections:list", granted_scopes=["api:read"])

    def test_policy_integration(self) -> None:
        engine = PermissionEngine()
        engine.policies.allow("read", "orders")
        assert engine.evaluate_policy("read", "orders") is True
        assert engine.evaluate_policy("write", "orders") is False

    def test_stats(self) -> None:
        engine = PermissionEngine()
        engine.define_role("viewer", ["read"])
        engine.assign("bob", "viewer")
        engine.scopes.register("api:read")
        assert engine.stats()["users"] == 1
        assert engine.stats()["roles"] == 1
        assert engine.stats()["scopes"] == 1
