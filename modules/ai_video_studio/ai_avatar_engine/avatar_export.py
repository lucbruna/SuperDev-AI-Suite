"""Avatar export — serialize avatars and results to files."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from modules.ai_video_studio.ai_avatar_engine.avatar_profiles import AvatarProfile


class AvatarExport:
    """Exports profiles and generation results as JSON/portable artifacts."""

    def export_profile(self, profile: AvatarProfile, output_path: str | Path) -> Path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(profile.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
        return out

    def export_results(self, results: list[dict[str, Any]], output_path: str | Path) -> Path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps({"count": len(results), "results": results}, indent=2,
                                  ensure_ascii=False), encoding="utf-8")
        return out

    def to_json(self, data: dict[str, Any]) -> str:
        return json.dumps(data, indent=2, ensure_ascii=False, default=str)


_avatar_export: AvatarExport | None = None


def get_avatar_export() -> AvatarExport:
    global _avatar_export
    if _avatar_export is None:
        _avatar_export = AvatarExport()
    return _avatar_export
