"""Avatar metadata — build serializable metadata for generated avatars."""
from __future__ import annotations

import hashlib
import time
from typing import Any

from modules.ai_video_studio.ai_avatar_engine.avatar_profiles import AvatarProfile


class AvatarMetadata:
    """Attaches standard metadata (id, hash, timestamps) to avatar outputs."""

    @staticmethod
    def for_profile(profile: AvatarProfile, *, generated_by: str = "ai_avatar_engine") -> dict[str, Any]:
        return {
            "profile_id": profile.id,
            "profile_name": profile.name,
            "style": profile.style,
            "dimension": profile.dimension,
            "generated_by": generated_by,
            "generated_at": round(time.time(), 3),
        }

    @staticmethod
    def fingerprint(payload: dict[str, Any]) -> str:
        """Stable content hash for cache/dedup keys."""
        raw = str(sorted(payload.items())).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()[:16]

    @staticmethod
    def enrich(result: dict[str, Any], profile: AvatarProfile) -> dict[str, Any]:
        meta = AvatarMetadata.for_profile(profile)
        meta["output_hash"] = AvatarMetadata.fingerprint(result)
        result["metadata"] = meta
        return result


_avatar_metadata: AvatarMetadata | None = None


def get_avatar_metadata() -> AvatarMetadata:
    global _avatar_metadata
    if _avatar_metadata is None:
        _avatar_metadata = AvatarMetadata()
    return _avatar_metadata
