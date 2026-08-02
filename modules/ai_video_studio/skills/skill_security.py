"""Skill security — allowlist/denylist enforcement for skill execution."""
from __future__ import annotations
import hashlib
from typing import Any


class SkillBlockedError(PermissionError):
    """Raised when a blocked skill is requested."""


class SkillSecurity:
    """Controls which skills may run and optional entrypoint hash pinning."""

    def __init__(self) -> None:
        self._allowlist: set[str] | None = None  # None = allow all
        self._denylist: set[str] = set()
        self._pinned: dict[str, str] = {}  # skill_id -> sha256 of callable source

    def allow_only(self, *skill_ids: str) -> None:
        self._allowlist = set(skill_ids)

    def allow_all(self) -> None:
        self._allowlist = None

    def block(self, *skill_ids: str) -> None:
        self._denylist.update(skill_ids)

    def unblock(self, *skill_ids: str) -> None:
        for skill_id in skill_ids:
            self._denylist.discard(skill_id)

    def pin(self, skill_id: str, entrypoint) -> None:
        """Pin the sha256 of a callable's source so tampering is detectable."""
        try:
            import inspect

            self._pinned[skill_id] = hashlib.sha256(
                inspect.getsource(entrypoint).encode("utf-8")
            ).hexdigest()
        except (OSError, TypeError):
            self._pinned[skill_id] = ""

    def check(self, skill_id: str, entrypoint=None) -> None:
        """Raise SkillBlockedError when the skill is not allowed to run."""
        if self._allowlist is not None and skill_id not in self._allowlist:
            raise SkillBlockedError(f"skill '{skill_id}' is not on the allowlist")
        if skill_id in self._denylist:
            raise SkillBlockedError(f"skill '{skill_id}' is blocked")
        pinned = self._pinned.get(skill_id)
        if pinned and entrypoint is not None:
            import inspect

            try:
                actual = hashlib.sha256(
                    inspect.getsource(entrypoint).encode("utf-8")
                ).hexdigest()
                if actual != pinned:
                    raise SkillBlockedError(
                        f"skill '{skill_id}' source does not match its pinned hash"
                    )
            except (OSError, TypeError):
                raise SkillBlockedError(f"cannot verify pinned skill '{skill_id}'") from None

    def snapshot(self) -> dict[str, Any]:
        return {
            "allowlist": sorted(self._allowlist) if self._allowlist is not None else "*",
            "denylist": sorted(self._denylist),
            "pinned": sorted(self._pinned),
        }


_security: SkillSecurity | None = None


def get_skill_security() -> SkillSecurity:
    global _security
    if _security is None:
        _security = SkillSecurity()
    return _security
