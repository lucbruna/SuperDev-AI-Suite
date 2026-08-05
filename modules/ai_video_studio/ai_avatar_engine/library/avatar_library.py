"""Avatar library — aggregates all domain-specific avatar catalogs."""
from __future__ import annotations


from modules.ai_video_studio.ai_avatar_engine.avatar_profiles import AvatarProfile

_DOMAIN_MODULES = (
    "business_avatars", "education_avatars", "medical_avatars", "legal_avatars",
    "agriculture_avatars", "engineering_avatars", "finance_avatars", "tourism_avatars",
    "ecommerce_avatars", "influencer_avatars", "presenter_avatars", "child_avatars",
    "elderly_avatars", "fantasy_avatars", "sci_fi_avatars",
)


class AvatarLibrary:
    """Aggregates every domain avatar catalog into one queryable library."""

    def all(self) -> list[AvatarProfile]:
        profiles: list[AvatarProfile] = []
        for module_name in _DOMAIN_MODULES:
            module = __import__(f"{__name__.rsplit('.', 1)[0]}.{module_name}",
                                fromlist=["avatars"])
            profiles.extend(module.avatars())
        return profiles

    def list(self, *, style: str | None = None, dimension: str | None = None,
             gender: str | None = None, tag: str | None = None) -> list[AvatarProfile]:
        candidates = self.all()
        if style:
            candidates = [a for a in candidates if a.style == style]
        if dimension:
            candidates = [a for a in candidates if a.dimension == dimension]
        if gender:
            candidates = [a for a in candidates if a.gender == gender]
        if tag:
            candidates = [a for a in candidates if tag in a.tags]
        return candidates

    def get(self, profile_id: str) -> AvatarProfile:
        for profile in self.all():
            if profile.id == profile_id:
                return profile
        raise KeyError(f"unknown avatar profile '{profile_id}'")

    def count(self) -> int:
        return len(self.all())


_avatar_library: AvatarLibrary | None = None


def get_avatar_library() -> AvatarLibrary:
    """Return the shared avatar library singleton."""
    global _avatar_library
    if _avatar_library is None:
        _avatar_library = AvatarLibrary()
    return _avatar_library
