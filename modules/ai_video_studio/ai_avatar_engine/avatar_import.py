"""Avatar import — load serialized avatars back into the engine."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from modules.ai_video_studio.ai_avatar_engine.avatar_profiles import AvatarProfile, profile_from_dict


class AvatarImport:
    """Loads profiles (and profile lists) from JSON files or dicts."""

    def import_profile(self, data: dict[str, Any]) -> AvatarProfile:
        """Build a validated profile from a dict (raises on invalid fields)."""
        return profile_from_dict(data)

    def import_profile_file(self, path: str | Path) -> AvatarProfile:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        return self.import_profile(payload)

    def import_profiles(self, data: list[dict[str, Any]]) -> list[AvatarProfile]:
        return [self.import_profile(d) for d in data]

    def import_profiles_file(self, path: str | Path) -> list[AvatarProfile]:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        items = payload.get("profiles", payload) if isinstance(payload, dict) else payload
        return self.import_profiles(items)


_avatar_import: AvatarImport | None = None


def get_avatar_import() -> AvatarImport:
    global _avatar_import
    if _avatar_import is None:
        _avatar_import = AvatarImport()
    return _avatar_import
