"""Avatar registry — registers avatar engines, profiles and subsystems."""
from __future__ import annotations

from typing import Any, Callable

from modules.ai_video_studio.ai_avatar_engine.avatar_profiles import AvatarProfile


class AvatarRegistry:
    """Central registry for profiles and named subsystems/components.

    ``register``/``get`` follow the studio's ``Registry`` pattern; profiles
    are indexed by id so library and engine lookups stay O(1).
    """

    def __init__(self) -> None:
        self._components: dict[str, Callable[..., Any]] = {}
        self._profiles: dict[str, AvatarProfile] = {}
        self._meta: dict[str, dict[str, Any]] = {}

    # ── components ────────────────────────────────────────────────
    def register(self, name: str, factory: Callable[..., Any], **meta: Any) -> None:
        self._components[name] = factory
        self._meta.setdefault(name, {}).update(meta)

    def get(self, name: str) -> Callable[..., Any]:
        if name not in self._components:
            raise KeyError(f"unknown avatar component '{name}'")
        return self._components[name]

    def names(self) -> list[str]:
        return sorted(self._components)

    # ── profiles ──────────────────────────────────────────────────
    def add_profile(self, profile: AvatarProfile) -> bool:
        if profile.id in self._profiles:
            return False
        self._profiles[profile.id] = profile
        return True

    def get_profile(self, profile_id: str) -> AvatarProfile:
        if profile_id not in self._profiles:
            raise KeyError(f"unknown avatar profile '{profile_id}'")
        return self._profiles[profile_id]

    def remove_profile(self, profile_id: str) -> bool:
        """Remove a profile by id; returns True when it existed."""
        return self._profiles.pop(profile_id, None) is not None

    def list_profiles(self, *, style: str | None = None, dimension: str | None = None,
                      gender: str | None = None) -> list[AvatarProfile]:
        candidates = list(self._profiles.values())
        if style:
            candidates = [p for p in candidates if p.style == style]
        if dimension:
            candidates = [p for p in candidates if p.dimension == dimension]
        if gender:
            candidates = [p for p in candidates if p.gender == gender]
        return candidates

    def profile_count(self) -> int:
        return len(self._profiles)


_avatar_registry: AvatarRegistry | None = None


def get_avatar_registry() -> AvatarRegistry:
    """Return the shared avatar registry singleton."""
    global _avatar_registry
    if _avatar_registry is None:
        _avatar_registry = AvatarRegistry()
    return _avatar_registry
