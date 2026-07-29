from __future__ import annotations

from typing import Any
from uuid import uuid4


PREDEFINED_ACTIVITIES: list[dict[str, Any]] = [
    {
        "activity_id": "act_001",
        "type": "walking",
        "subtype": "patrolling",
        "description": "Worker patrolling the production floor",
        "confidence": 0.94,
        "start_frame": 0,
        "end_frame": 150,
        "start_time_sec": 0.0,
        "end_time_sec": 5.0,
        "duration_sec": 5.0,
        "actor": "person_01",
        "zone": "production_floor_a",
    },
    {
        "activity_id": "act_002",
        "type": "lifting",
        "subtype": "heavy_lift",
        "description": "Worker lifting a heavy box onto conveyor",
        "confidence": 0.89,
        "start_frame": 160,
        "end_frame": 220,
        "start_time_sec": 5.3,
        "end_time_sec": 7.3,
        "duration_sec": 2.0,
        "actor": "person_02",
        "zone": "loading_zone",
    },
    {
        "activity_id": "act_003",
        "type": "operating",
        "subtype": "machine_operation",
        "description": "Worker operating the CNC machine control panel",
        "confidence": 0.96,
        "start_frame": 240,
        "end_frame": 600,
        "start_time_sec": 8.0,
        "end_time_sec": 20.0,
        "duration_sec": 12.0,
        "actor": "person_01",
        "zone": "machine_area_3",
    },
    {
        "activity_id": "act_004",
        "type": "inspecting",
        "subtype": "quality_check",
        "description": "Quality inspector examining circuit boards",
        "confidence": 0.92,
        "start_frame": 620,
        "end_frame": 800,
        "start_time_sec": 20.7,
        "end_time_sec": 26.7,
        "duration_sec": 6.0,
        "actor": "person_03",
        "zone": "quality_station",
    },
    {
        "activity_id": "act_005",
        "type": "transporting",
        "subtype": "forklift_movement",
        "description": "Forklift transporting pallet to storage",
        "confidence": 0.91,
        "start_frame": 820,
        "end_frame": 1100,
        "start_time_sec": 27.3,
        "end_time_sec": 36.7,
        "duration_sec": 9.4,
        "actor": "vehicle_01",
        "zone": "storage_aisle_2",
    },
    {
        "activity_id": "act_006",
        "type": "assembling",
        "subtype": "robot_assembly",
        "description": "Robotic arm assembling components on circuit board",
        "confidence": 0.97,
        "start_frame": 1120,
        "end_frame": 1500,
        "start_time_sec": 37.3,
        "end_time_sec": 50.0,
        "duration_sec": 12.7,
        "actor": "robot_arm_01",
        "zone": "assembly_line",
    },
]


class ActivityDetector:
    def __init__(self) -> None:
        self._threshold: float = 0.5
        self._timeline: list[dict[str, Any]] = []

    async def detect_activity(self, video_data: bytes | str) -> list[dict[str, Any]]:
        detected = [
            a for a in PREDEFINED_ACTIVITIES if a["confidence"] >= self._threshold
        ]
        self._timeline = detected
        return detected

    async def classify_activity(self, video_data: bytes | str, activity_features: dict[str, Any]) -> dict[str, Any]:
        return {
            "primary_type": "operating",
            "primary_confidence": 0.88,
            "secondary_type": "walking",
            "secondary_confidence": 0.09,
            "alternatives": [
                {"type": "operating", "confidence": 0.88},
                {"type": "walking", "confidence": 0.09},
                {"type": "inspecting", "confidence": 0.03},
            ],
            "features": activity_features,
        }

    async def track_activity(self, video_data: bytes | str, activity_id: str) -> dict[str, Any]:
        matched = next((a for a in PREDEFINED_ACTIVITIES if a["activity_id"] == activity_id), None)
        if matched is None:
            return {"activity_id": activity_id, "found": False}
        return {
            **matched,
            "progress": 0.65,
            "remaining_sec": max(0, matched["end_time_sec"] - matched["start_time_sec"]) * 0.35,
            "status": "in_progress",
        }

    async def get_activity_timeline(self, video_data: bytes | str) -> list[dict[str, Any]]:
        return self._timeline or await self.detect_activity(video_data)

    async def set_activity_threshold(self, threshold: float) -> None:
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("Threshold must be between 0.0 and 1.0")
        self._threshold = threshold
