from __future__ import annotations

from typing import Any
from uuid import uuid4


class VideoSummarizer:
    def __init__(self) -> None:
        self._summaries: dict[str, dict[str, Any]] = {}

    async def generate_summary(self, video_data: bytes | str) -> dict[str, Any]:
        summary_id = str(uuid4())
        summary = {
            "summary_id": summary_id,
            "title": "Production Floor Surveillance - Shift A",
            "duration_sec": 180.0,
            "total_frames": 5400,
            "key_frames": await self.extract_key_frames(video_data),
            "timeline": await self.generate_timeline(video_data),
            "text": await self.get_summary_text(video_data),
            "statistics": {
                "total_activities": 6,
                "total_events": 3,
                "unique_actors": 4,
                "avg_activity_duration_sec": 7.8,
                "busiest_zone": "assembly_line",
                "peak_activity_time_sec": 37.3,
            },
            "highlights": [
                "Safety violation detected at 00:01:15",
                "Production anomaly on conveyor belt at 00:00:42",
                "Equipment malfunction alert on robot arm at 00:01:08",
            ],
            "generated_at": "2026-07-28T15:00:00Z",
        }
        self._summaries[summary_id] = summary
        return summary

    async def extract_key_frames(self, video_data: bytes | str, max_frames: int = 5) -> list[dict[str, Any]]:
        key_frames = [
            {"frame_index": 0, "timestamp_sec": 0.0, "description": "Scene start", "significance": 0.8},
            {"frame_index": 456, "timestamp_sec": 15.2, "description": "Safety violation event", "significance": 0.95},
            {"frame_index": 1281, "timestamp_sec": 42.7, "description": "Production anomaly detected", "significance": 0.88},
            {"frame_index": 2049, "timestamp_sec": 68.3, "description": "Equipment malfunction", "significance": 0.97},
            {"frame_index": 3615, "timestamp_sec": 120.5, "description": "Unauthorized access event", "significance": 0.91},
        ]
        return key_frames[:max_frames]

    async def generate_timeline(self, video_data: bytes | str) -> list[dict[str, Any]]:
        return [
            {"time_sec": 0.0, "label": "Start", "type": "milestone", "description": "Recording started"},
            {"time_sec": 5.0, "label": "Patrol", "type": "activity", "description": "Worker patrols floor"},
            {"time_sec": 8.0, "label": "Machine Operation", "type": "activity", "description": "CNC operation begins"},
            {"time_sec": 15.2, "label": "Safety Violation", "type": "event", "description": "Worker enters restricted zone"},
            {"time_sec": 20.7, "label": "Quality Check", "type": "activity", "description": "Inspection at quality station"},
            {"time_sec": 27.3, "label": "Forklift Transport", "type": "activity", "description": "Pallet transported to storage"},
            {"time_sec": 37.3, "label": "Robot Assembly", "type": "activity", "description": "Robotic assembly active"},
            {"time_sec": 42.7, "label": "Conveyor Anomaly", "type": "event", "description": "Speed drop detected"},
            {"time_sec": 68.3, "label": "Robot Overheat", "type": "event", "description": "Joint temperature critical"},
            {"time_sec": 85.0, "label": "Quality Defect", "type": "event", "description": "Solder crack found"},
            {"time_sec": 120.5, "label": "Unauthorized Access", "type": "event", "description": "Intruder in secure area"},
            {"time_sec": 155.0, "label": "Maintenance Alert", "type": "event", "description": "Vibration threshold exceeded"},
            {"time_sec": 180.0, "label": "End", "type": "milestone", "description": "Recording ended"},
        ]

    async def create_clip(self, video_data: bytes | str, start_sec: float, end_sec: float) -> dict[str, Any]:
        clip_id = str(uuid4())
        return {
            "clip_id": clip_id,
            "start_sec": start_sec,
            "end_sec": end_sec,
            "duration_sec": round(end_sec - start_sec, 1),
            "frame_count": int((end_sec - start_sec) * 30),
            "source_video_id": id(video_data),
            "clip_url": f"clips/{clip_id}.mp4",
            "thumbnail_url": f"thumbnails/{clip_id}.jpg",
            "events_in_clip": [
                e for e in [
                    {"time": 15.2, "type": "safety_violation"},
                    {"time": 42.7, "type": "production_anomaly"},
                ]
                if start_sec <= e["time"] <= end_sec
            ],
        }

    async def get_summary_text(self, video_data: bytes | str) -> str:
        return (
            "This 3-minute surveillance video of Production Floor A captures a full shift cycle "
            "with six distinct worker activities and three critical events. The shift begins with "
            "routine patrol and machine operation. At 15 seconds, a safety violation occurs when "
            "a worker enters a restricted zone without proper safety gear. Production continues "
            "with quality inspection and forklift transport until a conveyor belt anomaly at 42 "
            "seconds requires speed adjustment. The most critical incident happens at 68 seconds "
            "when a robotic arm joint overheats, triggering an emergency stop. Later, a quality "
            "defect is identified on a circuit board at 85 seconds, followed by an unauthorized "
            "access attempt at 120 seconds. The video concludes with a maintenance alert at 155 "
            "seconds, indicating normal equipment degradation."
        )
