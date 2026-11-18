"""Timeline-based audio/video synchronization diagnostics.

This checks edit-decision-list timing metadata, not acoustic lip-sync or speech
content. A waveform/forced-alignment model would be needed for those claims.
"""
from __future__ import annotations

from typing import Any


def analyze_av_sync(
    video_clips: list[dict[str, Any]],
    narration_clips: list[dict[str, Any]],
    *,
    fps: int,
    tolerance_frames: int = 2,
    gap_warning_seconds: float = 0.35,
) -> dict[str, Any]:
    if fps < 1:
        raise ValueError("fps must be a positive integer")
    if tolerance_frames < 0:
        raise ValueError("tolerance_frames cannot be negative")
    if gap_warning_seconds < 0:
        raise ValueError("gap_warning_seconds cannot be negative")

    def bounds(clip: dict[str, Any]) -> tuple[int, int]:
        start = int(clip.get("start_frame", round(float(clip.get("start_seconds", clip.get("start", 0))) * fps)))
        end = int(clip.get("end_frame", round(float(clip.get("end_seconds", clip.get("end", 0))) * fps)))
        return start, end

    video = [clip for clip in video_clips if isinstance(clip, dict)]
    narration = [clip for clip in narration_clips if isinstance(clip, dict)]
    warnings: list[dict[str, Any]] = []
    comparisons: list[dict[str, Any]] = []
    if not video:
        raise ValueError("video timeline has no scene clips")

    video_end = max((bounds(clip)[1] for clip in video), default=0)
    previous_end: int | None = None
    for index, clip in enumerate(narration):
        start, end = bounds(clip)
        if end <= start:
            warnings.append({"code": "invalid_narration_range", "severity": "critical", "clip_index": index})
            continue
        if start >= video_end or end > video_end + tolerance_frames:
            warnings.append({"code": "narration_outside_video", "severity": "critical", "clip_index": index,
                             "start_frame": start, "end_frame": end, "video_end_frame": video_end})
        if previous_end is not None:
            gap = start - previous_end
            if gap > round(gap_warning_seconds * fps):
                warnings.append({"code": "narration_gap", "severity": "warning", "start_frame": previous_end,
                                 "end_frame": start, "duration_seconds": round(gap / fps, 3)})
            elif gap < -tolerance_frames:
                warnings.append({"code": "narration_overlap", "severity": "warning", "clip_index": index,
                                 "overlap_frames": -gap})
        previous_end = max(previous_end or end, end)

    if len(narration) == len(video) and narration:
        for index, (scene, voice) in enumerate(zip(video, narration, strict=True)):
            scene_start, scene_end = bounds(scene)
            voice_start, voice_end = bounds(voice)
            start_delta = voice_start - scene_start
            end_delta = voice_end - scene_end
            item = {
                "scene_index": int(scene.get("scene_index", index)),
                "start_delta_frames": start_delta,
                "end_delta_frames": end_delta,
                "start_delta_ms": round(start_delta * 1000 / fps, 1),
                "end_delta_ms": round(end_delta * 1000 / fps, 1),
                "aligned": abs(start_delta) <= tolerance_frames and abs(end_delta) <= tolerance_frames,
            }
            comparisons.append(item)
            if not item["aligned"]:
                warnings.append({"code": "scene_narration_timing_mismatch", "severity": "warning", **item})
    elif narration:
        warnings.append({
            "code": "per_scene_comparison_unavailable",
            "severity": "info",
            "video_scene_count": len(video),
            "narration_clip_count": len(narration),
        })

    critical = any(item["severity"] == "critical" for item in warnings)
    status = "blocked" if critical else ("needs_review" if warnings else "passed")
    return {
        "status": status,
        "fps": fps,
        "tolerance_frames": tolerance_frames,
        "video_duration_frames": video_end,
        "video_duration_seconds": round(video_end / fps, 3),
        "video_scene_count": len(video),
        "narration_clip_count": len(narration),
        "scene_comparisons": comparisons,
        "warnings": warnings,
        "export_blocked": critical,
        "analysis_method": "timeline_frame_metadata",
        "limitations": [
            "Não analisa conteúdo acústico nem detecta início real da fala.",
            "Não verifica sincronização labial; compara apenas os intervalos da timeline.",
        ],
    }
