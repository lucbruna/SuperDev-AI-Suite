from __future__ import annotations

from typing import Any, Callable
from uuid import uuid4


PREDEFINED_EVENTS: list[dict[str, Any]] = [
    {
        "event_id": "evt_001",
        "type": "safety_violation",
        "severity": "high",
        "description": "Worker entered restricted zone without safety harness",
        "confidence": 0.93,
        "timestamp_sec": 15.2,
        "frame_index": 456,
        "zone": "restricted_area_a",
        "actors": ["person_04"],
        "action_taken": "alert_supervisor",
    },
    {
        "event_id": "evt_002",
        "type": "production_anomaly",
        "severity": "medium",
        "description": "Conveyor belt speed dropped below threshold",
        "confidence": 0.88,
        "timestamp_sec": 42.7,
        "frame_index": 1281,
        "zone": "assembly_line",
        "actors": ["machine_02"],
        "action_taken": "adjust_speed",
    },
    {
        "event_id": "evt_003",
        "type": "equipment_malfunction",
        "severity": "critical",
        "description": "Robot arm joint 3 temperature exceeded safe limit",
        "confidence": 0.97,
        "timestamp_sec": 68.3,
        "frame_index": 2049,
        "zone": "assembly_line",
        "actors": ["robot_arm_01"],
        "action_taken": "emergency_stop",
    },
    {
        "event_id": "evt_004",
        "type": "quality_defect",
        "severity": "medium",
        "description": "Product defect detected: solder joint crack on circuit board",
        "confidence": 0.91,
        "timestamp_sec": 85.0,
        "frame_index": 2550,
        "zone": "quality_station",
        "actors": ["product_001"],
        "action_taken": "flag_for_rework",
    },
    {
        "event_id": "evt_005",
        "type": "unauthorized_access",
        "severity": "high",
        "description": "Unidentified person detected in secure area after hours",
        "confidence": 0.86,
        "timestamp_sec": 120.5,
        "frame_index": 3615,
        "zone": "secure_storage",
        "actors": ["unknown_person"],
        "action_taken": "trigger_alarm",
    },
    {
        "event_id": "evt_006",
        "type": "maintenance_required",
        "severity": "low",
        "description": "Vibration levels on CNC machine exceed normal range",
        "confidence": 0.79,
        "timestamp_sec": 155.0,
        "frame_index": 4650,
        "zone": "machine_area_3",
        "actors": ["machine_01"],
        "action_taken": "schedule_maintenance",
    },
]


class EventRecognizer:
    def __init__(self) -> None:
        self._subscribers: list[Callable[[dict[str, Any]], None]] = []
        self._recognized_events: list[dict[str, Any]] = []

    async def recognize_event(self, video_data: bytes | str) -> list[dict[str, Any]]:
        self._recognized_events = PREDEFINED_EVENTS.copy()
        for subscriber in self._subscribers:
            for event in self._recognized_events:
                subscriber(event)
        return self._recognized_events

    async def classify_event(self, video_data: bytes | str, event_features: dict[str, Any]) -> dict[str, Any]:
        return {
            "primary_event_type": "safety_violation",
            "primary_confidence": 0.82,
            "secondary_event_type": "production_anomaly",
            "secondary_confidence": 0.11,
            "all_possible_types": [
                {"type": "safety_violation", "confidence": 0.82},
                {"type": "production_anomaly", "confidence": 0.11},
                {"type": "equipment_malfunction", "confidence": 0.05},
                {"type": "quality_defect", "confidence": 0.02},
            ],
            "features": event_features,
        }

    async def get_event_timestamp(self, video_data: bytes | str, event_id: str) -> dict[str, Any] | None:
        for event in PREDEFINED_EVENTS:
            if event["event_id"] == event_id:
                return {
                    "event_id": event_id,
                    "timestamp_sec": event["timestamp_sec"],
                    "timestamp_str": f"00:{int(event['timestamp_sec']) // 60:02d}:{int(event['timestamp_sec']) % 60:02d}",
                    "frame_index": event["frame_index"],
                    "duration_sec": 3.0,
                }
        return None

    async def get_event_details(self, video_data: bytes | str, event_id: str) -> dict[str, Any] | None:
        for event in PREDEFINED_EVENTS:
            if event["event_id"] == event_id:
                return {
                    **event,
                    "detailed_description": f"Event {event['type']} occurred at {event['timestamp_sec']}s in {event['zone']}. {event['description']}",
                    "root_cause_analysis": {
                        "likely_cause": "sensor_threshold_exceeded" if event["severity"] != "low" else "normal_degradation",
                        "contributing_factors": ["worn_component", "environmental_conditions"],
                        "recommended_action": event["action_taken"],
                    },
                    "evidence": {
                        "thumbnail_frame": f"frame_{event['frame_index']}.jpg",
                        "confidence_scores": {"model": event["confidence"], "ensemble": event["confidence"] + 0.02},
                    },
                }
        return None

    async def subscribe_to_events(self, callback: Callable[[dict[str, Any]], None]) -> None:
        self._subscribers.append(callback)

    def clear_subscribers(self) -> None:
        self._subscribers.clear()
