from __future__ import annotations

from typing import Any
from uuid import uuid4


class FrameAnalyzer:
    def __init__(self) -> None:
        self._cache: dict[int, list[dict[str, Any]]] = {}
        self._analysis_count = 0

    async def extract_frames(self, video_data: bytes | str, count: int = 10, interval: int | None = None) -> list[dict[str, Any]]:
        self._analysis_count += 1
        frames = []
        for i in range(count):
            timestamp_sec = i * (interval or 2)
            frames.append({
                "frame_index": i,
                "timestamp_sec": timestamp_sec,
                "timestamp_str": f"00:{timestamp_sec // 60:02d}:{timestamp_sec % 60:02d}",
                "width": 1920,
                "height": 1080,
                "analysis": await self.analyze_frame(video_data, i),
            })
        return frames

    async def analyze_frame(self, video_data: bytes | str, frame_index: int = 0) -> dict[str, Any]:
        self._analysis_count += 1
        return {
            "frame_index": frame_index,
            "frame_id": str(uuid4()),
            "sharpness": round(0.75 + (frame_index % 10) * 0.02, 3),
            "brightness": round(0.6 + (frame_index % 5) * 0.05, 3),
            "contrast": round(0.55 + (frame_index % 8) * 0.03, 3),
            "motion_score": round(0.1 + (frame_index % 6) * 0.08, 3),
            "has_motion": (frame_index % 3) == 0,
            "objects_count": (frame_index % 5) + 3,
            "mean_color": "#4682B4",
            "histogram_peak": 142,
            "scene_cut": frame_index == 0,
        }

    async def detect_changes(self, video_data: bytes | str, frame_indices: list[int] | None = None) -> list[dict[str, Any]]:
        if frame_indices is None:
            frame_indices = [0, 1, 2, 3, 4]
        changes = []
        for i in range(1, len(frame_indices)):
            changes.append({
                "from_frame": frame_indices[i - 1],
                "to_frame": frame_indices[i],
                "change_score": round(0.05 + i * 0.03, 3),
                "has_significant_change": i > 2,
                "change_type": "motion" if i % 2 == 0 else "lighting" if i % 3 == 0 else "object_appearance",
                "affected_regions": ["center", "top_right"] if i > 1 else ["center"],
            })
        return changes

    async def get_frame_metadata(self, video_data: bytes | str, frame_index: int = 0) -> dict[str, Any]:
        return {
            "frame_index": frame_index,
            "codec": "h264",
            "pixel_format": "yuv420p",
            "color_range": "limited",
            "aspect_ratio": "16:9",
            "bitrate_kbps": 8000,
            "key_frame": frame_index == 0,
            "pts": frame_index * 1001,
            "dts": frame_index * 1001,
            "duration_sec": 0.033,
            "gop_position": frame_index % 30,
        }

    async def compare_frames(self, video_data: bytes | str, frame_a: int, frame_b: int) -> dict[str, Any]:
        diff_score = abs(frame_a - frame_b) * 0.05
        return {
            "frame_a": frame_a,
            "frame_b": frame_b,
            "difference_score": round(min(diff_score, 1.0), 3),
            "mse": round(diff_score * 255, 2),
            "psnr": round(45.0 - diff_score * 10, 2),
            "ssim": round(1.0 - diff_score * 2, 3),
            "histogram_correlation": round(1.0 - diff_score, 3),
            "identical": frame_a == frame_b,
            "structural_changes": [
                {"region": "top_left", "change": diff_score * 0.5},
                {"region": "bottom_right", "change": diff_score * 0.8},
            ] if diff_score > 0.1 else [],
        }

    def clear_cache(self) -> None:
        self._cache.clear()
