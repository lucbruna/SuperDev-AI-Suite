"""Tests for the RBAC module (backend.auth.rbac)."""
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import UTC, datetime, timedelta

from backend.auth.rbac import (
    Action,
    PermissionChecker,
    Resource,
    RoleName,
    _DEFAULT_ROLE_PERMISSIONS,
    assign_role,
    ensure_system_roles,
    get_user_permissions,
    require_permission,
)


class TestRoleName:
    def test_role_names_are_strings(self):
        for role in RoleName:
            assert isinstance(role.value, str)

    def test_all_expected_roles_exist(self):
        expected = {"super_admin", "admin", "manager", "developer", "viewer", "guest"}
        actual = {r.value for r in RoleName}
        assert actual == expected


class TestResource:
    def test_resource_values(self):
        expected = {
            "users", "projects", "workflows", "agents", "plugins",
            "providers", "knowledge", "organizations", "audit",
            "notifications", "settings",
        }
        actual = {r.value for r in Resource}
        assert actual == expected


class TestAction:
    def test_action_values(self):
        expected = {"create", "read", "update", "delete", "execute", "manage", "admin"}
        actual = {a.value for a in Action}
        assert actual == expected


class TestDefaultPermissions:
    def test_super_admin_has_all_permissions(self):
        perms = _DEFAULT_ROLE_PERMISSIONS[RoleName.SUPER_ADMIN]
        for resource in Resource:
            for action in Action:
                assert (resource.value, action.value) in perms

    def test_viewer_has_only_read(self):
        perms = _DEFAULT_ROLE_PERMISSIONS[RoleName.VIEWER]
        for res, act in perms:
            assert act == Action.READ.value

    def test_guest_has_limited_permissions(self):
        perms = _DEFAULT_ROLE_PERMISSIONS[RoleName.GUEST]
        assert len(perms) <= 5  # Very limited
        resources = {r for r, _ in perms}
        assert resources.issubset({"projects", "workflows", "knowledge"})

    def test_all_roles_have_permission_sets(self):
        for role in RoleName:
            assert role in _DEFAULT_ROLE_PERMISSIONS
            assert isinstance(_DEFAULT_ROLE_PERMISSIONS[role], set)


class TestPermissionChecker:
    def test_init_with_enums(self):
        checker = PermissionChecker(Resource.USERS, Action.READ)
        assert checker.resource == "users"
        assert checker.action == "read"

    def test_init_with_strings(self):
        checker = PermissionChecker("projects", "create")
        assert checker.resource == "projects"
        assert checker.action == "create"

    @pytest.mark.asyncio
    async def test_check_returns_false_for_nonexistent_user(self):
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        checker = PermissionChecker(Resource.USERS, Action.READ)
        result = await checker.check(mock_session, "nonexistent-id")
        assert result is False

    @pytest.mark.asyncio
    async def test_check_returns_true_for_superuser(self):
        mock_user = MagicMock()
        mock_user.is_superuser = True

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_session.execute.return_value = mock_result

        checker = PermissionChecker(Resource.USERS, Action.DELETE)
        result = await checker.check(mock_session, "user-123")
        assert result is True


class TestRequirePermission:
    def test_returns_callable(self):
        dep = require_permission(Resource.PROJECTS, Action.CREATE)
        assert callable(dep)

    def test_returns_callable_with_strings(self):
        dep = require_permission("users", "read")
        assert callable(dep)


class TestEnsureSystemRoles:
    @pytest.mark.asyncio
    async def test_creates_roles(self):
        mock_session = AsyncMock()
        # First call returns None (role doesn't exist)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        await ensure_system_roles(mock_session)
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_skips_existing_roles(self):
        mock_session = AsyncMock()
        # Return existing role for all queries
        mock_role = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_role
        mock_session.execute.return_value = mock_result

        await ensure_system_roles(mock_session)
        mock_session.add.assert_not_called()
        mock_session.commit.assert_called_once()


class TestAssignRole:
    @pytest.mark.asyncio
    async def test_raises_on_missing_role(self):
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        with pytest.raises(ValueError, match="does not exist"):
            await assign_role(mock_session, "user-123", "nonexistent_role")

    @pytest.mark.asyncio
    async def test_skips_duplicate_assignment(self):
        mock_role = MagicMock()
        mock_role.id = "role-123"
        mock_existing_ur = MagicMock()

        mock_session = AsyncMock()
        # First call: role found, second call: existing assignment found
        mock_result1 = MagicMock()
        mock_result1.scalar_one_or_none.return_value = mock_role
        mock_result2 = MagicMock()
        mock_result2.scalar_one_or_none.return_value = mock_existing_ur

        mock_session.execute.side_effect = [mock_result1, mock_result2]

        result = await assign_role(mock_session, "user-123", "admin")
        assert result == mock_existing_ur
        mock_session.add.assert_not_called()
