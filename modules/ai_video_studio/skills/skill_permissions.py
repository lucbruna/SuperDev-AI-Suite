"""Skill permissions — resource-level permissions enforced before execution."""
from __future__ import annotations
from typing import Any


class PermissionDeniedError(PermissionError):
    """Raised when a skill requests a resource it is not allowed to use."""


class SkillPermissions:
    """Tracks the resources (features/domains) a skill is allowed to touch."""

    def __init__(self) -> None:
        # skill_id -> set of allowed resources
        self._grants: dict[str, set[str]] = {}

    def grant(self, skill_id: str, *resources: str) -> None:
        self._grants.setdefault(skill_id, set()).update(resources)

    def revoke(self, skill_id: str, *resources: str) -> None:
        grants = self._grants.get(skill_id)
        if grants:
            for resource in resources:
                grants.discard(resource)

    def allowed(self, skill_id: str, resource: str) -> bool:
        grants = self._grants.get(skill_id)
        return bool(grants and resource in grants)

    def require(self, skill_id: str, resource: str) -> None:
        if not self.allowed(skill_id, resource):
            raise PermissionDeniedError(
                f"skill '{skill_id}' is not allowed to use '{resource}'"
            )

    def require_all(self, skill_id: str, resources: list[str] | None) -> None:
        for resource in resources or ():
            self.require(skill_id, resource)

    def snapshot(self) -> dict[str, Any]:
        return {skill_id: sorted(res) for skill_id, res in sorted(self._grants.items())}


_permissions: SkillPermissions | None = None


def get_skill_permissions() -> SkillPermissions:
    global _permissions
    if _permissions is None:
        _permissions = SkillPermissions()
    return _permissions
