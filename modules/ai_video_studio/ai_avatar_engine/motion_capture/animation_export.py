"""Animation export — serialize motion into JSON animation data."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class AnimationExport:
    """Writes keyframe motion data to JSON files."""

    def export(self, motion: list[dict[str, Any]], output_path: str | Path,
               *, fps: int = 24, name: str = "animation") -> Path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        payload = {"name": name, "fps": fps, "frames": len(motion), "keyframes": motion}
        out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return out

    def to_dict(self, motion: list[dict[str, Any]], *, fps: int = 24) -> dict[str, Any]:
        return {"fps": fps, "frames": len(motion), "keyframes": motion}


_animation_export: AnimationExport | None = None


def get_animation_export() -> AnimationExport:
    global _animation_export
    if _animation_export is None:
        _animation_export = AnimationExport()
    return _animation_export
