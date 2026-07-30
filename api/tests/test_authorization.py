from __future__ import annotations

import sys
from typing import Any

import pytest  # type: ignore[import-untyped]

sys.path.insert(0, "SuperDev")

from api.authz import Authorizer, RBACEngine, ABACEngine  # noqa: E402
from api.authz.policy import Policy, PolicyBuilder, PolicyEngine  # noqa: E402
from api.authz.scope_registry import ScopeRegistry  # noqa: E402
from api.authz.tenant_manager import TenantManager  # noqa: E402


class TestAuthorizer:
    def test_initialization(self) -> None:
        authz = Authorizer()
        assert authz is not None


class TestRBACEngine:
    def test_add_role(self) -> None:
        rbac = RBACEngine()
        rbac.add_role("admin")
        assert rbac.has_role("admin")

    def test_add_permission_to_role(self) -> None:
        rbac = RBACEngine()
        rbac.add_role("admin")
        rbac.add_permission("admin", "create:user")
        assert rbac.has_permission("admin", "create:user")

    def test_role_hierarchy(self) -> None:
        rbac = RBACEngine()
        rbac.add_role("admin", parents=["editor"])
        rbac.add_role("editor")
        rbac.add_permission("editor", "edit:post")
        assert rbac.has_permission("admin", "edit:post")

    def test_no_permission(self) -> None:
        rbac = RBACEngine()
        rbac.add_role("viewer")
        assert not rbac.has_permission("viewer", "delete:post")

    def test_add_role_with_nonexistent_parent(self) -> None:
        rbac = RBACEngine()
        rbac.add_role("user")
        rbac.add_role("admin", parents=["user", "nonexistent"])
        # Should silently skip missing parent
        assert rbac.has_role("admin")


class TestABACEngine:
    def test_evaluate_true(self) -> None:
        abac = ABACEngine()
        rule = lambda user, resource, context: user.get("role") == "admin"  # noqa: E731
        abac.add_rule("delete:post", rule)
        result = abac.evaluate("delete:post", {"role": "admin"}, {}, {})
        assert result is True

    def test_evaluate_false(self) -> None:
        abac = ABACEngine()
        rule = lambda user, resource, context: user.get("role") == "admin"  # noqa: E731
        abac.add_rule("delete:post", rule)
        result = abac.evaluate("delete:post", {"role": "viewer"}, {}, {})
        assert result is False

    def test_missing_rule(self) -> None:
        abac = ABACEngine()
        result = abac.evaluate("nonexistent", {}, {}, {})
        assert result is False


class TestPolicyEngine:
    def test_evaluate_allow(self) -> None:
        policy = Policy(id="p1", effect="Allow", actions=["read:*"], resources=["*"])
        engine = PolicyEngine()
        engine.add(policy)
        result = engine.evaluate("read:user", "user:123")
        assert result is True

    def test_evaluate_deny(self) -> None:
        deny = Policy(id="p2", effect="Deny", actions=["delete:*"], resources=["*"])
        allow = Policy(id="p3", effect="Allow", actions=["*"], resources=["*"])
        engine = PolicyEngine()
        engine.add(deny)
        engine.add(allow)
        result = engine.evaluate("delete:user", "user:123")
        assert result is False

    def test_no_match(self) -> None:
        engine = PolicyEngine()
        result = engine.evaluate("read:user", "user:123")
        assert result is False


class TestScopeRegistry:
    def test_register_and_check(self) -> None:
        registry = ScopeRegistry()
        registry.register("read:users")
        assert registry.has("read:users")

    def test_scope_hierarchy(self) -> None:
        registry = ScopeRegistry()
        registry.register("read:users:email")
        assert registry.has("read:users")
        assert registry.has("read:users:email")

    def test_no_scope(self) -> None:
        registry = ScopeRegistry()
        assert not registry.has("write:admin")


class TestTenantManager:
    def test_create_tenant(self) -> None:
        mgr = TenantManager()
        tenant = mgr.create_tenant("acme")
        assert tenant.name == "acme"
        assert tenant.tenant_id is not None

    def test_get_tenant(self) -> None:
        mgr = TenantManager()
        created = mgr.create_tenant("acme")
        retrieved = mgr.get_tenant(created.tenant_id)
        assert retrieved is not None
        assert retrieved.name == "acme"

    def test_isolation(self) -> None:
        mgr = TenantManager()
        t1 = mgr.create_tenant("acme")
        t2 = mgr.create_tenant("globex")
        mgr.add_user(t1.tenant_id, "user1")
        users_t1 = mgr.get_users(t1.tenant_id)
        users_t2 = mgr.get_users(t2.tenant_id)
        assert "user1" in users_t1
        assert "user1" not in users_t2
