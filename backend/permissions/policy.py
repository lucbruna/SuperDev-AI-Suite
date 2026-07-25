from __future__ import annotations

from typing import Any


class PolicyEngine:
    def check(
        self,
        user_permissions: list[str],
        required_permissions: list[str],
        context: dict[str, Any] | None = None,
    ) -> bool:
        if not required_permissions:
            return True
        return all(p in user_permissions for p in required_permissions)

    def check_any(
        self,
        user_permissions: list[str],
        required_permissions: list[str],
        context: dict[str, Any] | None = None,
    ) -> bool:
        if not required_permissions:
            return True
        return any(p in user_permissions for p in required_permissions)

    def evaluate_policy(
        self,
        policy_rules: list[dict[str, Any]],
        user: dict[str, Any],
        resource: dict[str, Any],
        action: str,
    ) -> bool:
        for rule in policy_rules:
            if self._match_rule(rule, user, resource, action):
                effect = rule.get("effect", "deny")
                return effect == "allow"
        return False

    def _match_rule(
        self,
        rule: dict[str, Any],
        user: dict[str, Any],
        resource: dict[str, Any],
        action: str,
    ) -> bool:
        conditions = rule.get("conditions", {})

        if "roles" in conditions:
            user_role = user.get("role", "")
            if user_role not in conditions["roles"]:
                return False

        if "actions" in conditions:
            if action not in conditions["actions"]:
                return False

        if "resource_types" in conditions:
            resource_type = resource.get("type", "")
            if resource_type not in conditions["resource_types"]:
                return False

        return True

    def evaluate_abac(
        self,
        user: dict[str, Any],
        resource: dict[str, Any],
        action: str,
        context: dict[str, Any],
    ) -> bool:
        resource.get("type", "")
        resource_owner = resource.get("owner_id")
        user_id = user.get("id")
        org_membership = context.get("org_membership", [])

        is_owner = resource_owner is not None and str(resource_owner) == str(user_id)
        is_org_member = resource.get("organization_id") and str(resource.get("organization_id")) in [
            str(m) for m in org_membership
        ]

        if action.endswith(":admin") or action.endswith(":delete"):
            return is_owner or is_org_member

        if action.endswith(":write"):
            return is_owner or is_org_member

        if action.endswith(":read"):
            return True

        return False