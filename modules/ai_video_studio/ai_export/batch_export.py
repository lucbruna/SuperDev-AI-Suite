"""Batch export — render one frame set to several targets in sequence."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from modules.ai_video_studio.ai_export.export_engine import export_engine

ProgressFn = Callable[[int, int, str], None]  # (done, total, target_name)


_CONTAINER_EXT = {
    "mp4": "mp4",
    "matroska": "mkv",
    "avi": "avi",
    "webm": "webm",
    "mov": "mov",
    "gif": "gif",
    "image2": "png",
}


def _default_ext(preset: str | None, profile: str | None) -> str:
    """Pick a file extension from a preset or profile name."""
    from modules.ai_video_studio.ai_export.export_presets import PRESETS
    from modules.ai_video_studio.ai_export.export_profiles import PROFILES

    if preset and preset in PRESETS:
        prof = PRESETS[preset].profile
        if prof in PROFILES:
            return _CONTAINER_EXT.get(PROFILES[prof].container, "mp4")
    if profile and profile in PROFILES:
        return _CONTAINER_EXT.get(PROFILES[profile].container, "mp4")
    if preset:
        # fallback: try the raw name as a container/codec hint
        for key, ext in _CONTAINER_EXT.items():
            if key in preset or preset in key:
                return ext
    return "mp4"


@dataclass
class BatchExportResult:
    """Aggregate result of a batch export run."""

    total: int = 0
    ok: int = 0
    failed: int = 0
    results: list[dict[str, Any]] = field(default_factory=list)
    errors: dict[str, str] = field(default_factory=dict)
    elapsed_s: float = 0.0

    def report(self) -> str:
        lines = [
            f"Batch export: {self.ok}/{self.total} ok, {self.failed} failed "
            f"({self.elapsed_s:.1f}s)",
        ]
        for name, err in self.errors.items():
            lines.append(f"  [x] {name}: {err}")
        return "\n".join(lines)


def batch_export(
    frames: list[Any],
    targets: list[dict[str, Any]],
    output_dir: str | Path,
    *,
    progress: ProgressFn | None = None,
) -> BatchExportResult:
    """Export ``frames`` to every target in ``targets``.

    Each target is a dict: ``{"name", "preset"|"profile", "fps"?, "resolution"?,
    "ext"?}``. Files land at ``<output_dir>/<name>.<ext>`` (ext defaults
    to the profile container).
    """
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    started = time.time()
    result = BatchExportResult(total=len(targets))

    for i, target in enumerate(targets):
        name = target.get("name", f"export_{i + 1}")
        try:
            preset = target.get("preset")
            profile = target.get("profile")
            ext = target.get("ext") or _default_ext(preset, profile)
            path = out_dir / f"{name}.{ext}"
            res = export_engine.export_frames(
                frames,
                preset=preset,
                profile=profile,
                fps=target.get("fps"),
                resolution=target.get("resolution"),
                output_path=path,
            )
            result.ok += 1
            result.results.append(res)
        except Exception as e:  # noqa: BLE001
            result.failed += 1
            result.errors[name] = str(e)
        if progress:
            progress(i + 1, len(targets), name)

    result.elapsed_s = round(time.time() - started, 3)
    return result
