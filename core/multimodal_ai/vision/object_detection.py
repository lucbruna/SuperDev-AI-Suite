from __future__ import annotations

from typing import Any
from uuid import uuid4


PREDEFINED_OBJECTS: dict[str, dict[str, Any]] = {
    "machine_01": {
        "type": "machine",
        "subtype": "cnc_router",
        "confidence": 0.97,
        "bbox": [120, 80, 540, 420],
        "status": "operational",
        "speed_rpm": 12000,
    },
    "machine_02": {
        "type": "machine",
        "subtype": "conveyor_belt",
        "confidence": 0.94,
        "bbox": [600, 350, 1100, 500],
        "status": "running",
        "speed_mps": 0.5,
    },
    "product_001": {
        "type": "product",
        "subtype": "circuit_board",
        "confidence": 0.96,
        "bbox": [800, 400, 950, 480],
        "quality": "passed",
        "batch_id": "B2026-07-28-003",
    },
    "person_01": {
        "type": "person",
        "subtype": "worker",
        "confidence": 0.99,
        "bbox": [300, 200, 380, 520],
        "has_helmet": True,
        "has_vest": True,
        "action": "inspecting",
    },
    "vehicle_01": {
        "type": "vehicle",
        "subtype": "forklift",
        "confidence": 0.93,
        "bbox": [50, 450, 250, 580],
        "speed_kmh": 8,
        "load_status": "carrying",
    },
    "robot_arm_01": {
        "type": "robot_arm",
        "subtype": "6_axis",
        "confidence": 0.98,
        "bbox": [1000, 100, 1200, 450],
        "joint_angles": [15, -30, 45, 90, -10, 5],
    },
    "safety_barrier": {
        "type": "safety_equipment",
        "subtype": "barrier",
        "confidence": 0.89,
        "bbox": [400, 550, 700, 600],
        "condition": "intact",
    },
}


class ObjectDetector:
    def __init__(self) -> None:
        self._tracking_data: dict[str, list[dict[str, Any]]] = {}
        self._detection_count = 0

    async def detect_objects(self, image_data: bytes | str) -> list[dict[str, Any]]:
        self._detection_count += 1
        return [
            {**obj, "object_id": f"{obj['type']}_{i:03d}", "detection_id": self._detection_count}
            for i, obj in enumerate(PREDEFINED_OBJECTS.values())
        ]

    async def classify_object(self, image_data: bytes | str, bbox: list[int]) -> dict[str, Any]:
        return {
            "type": "machine",
            "subtype": "unknown",
            "confidence": 0.76,
            "possible_types": [
                {"type": "machine", "confidence": 0.76},
                {"type": "vehicle", "confidence": 0.12},
                {"type": "product", "confidence": 0.08},
            ],
        }

    async def count_objects(self, image_data: bytes | str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for obj in PREDEFINED_OBJECTS.values():
            t = obj["type"]
            counts[t] = counts.get(t, 0) + 1
        return counts

    async def track_object(
        self, image_data: bytes | str, object_id: str
    ) -> dict[str, Any]:
        if object_id not in self._tracking_data:
            self._tracking_data[object_id] = []
        position = {"x": 320, "y": 240, "frame": len(self._tracking_data[object_id])}
        self._tracking_data[object_id].append(position)
        return {
            "object_id": object_id,
            "trajectory": self._tracking_data[object_id],
            "current_position": position,
            "velocity": {"dx": 2.5, "dy": -1.3},
            "tracking_active": True,
        }

    async def get_detection_map(self, image_data: bytes | str) -> dict[str, Any]:
        return {
            "width": 1920,
            "height": 1080,
            "objects": [
                {"type": o["type"], "bbox": o["bbox"], "confidence": o["confidence"]}
                for o in PREDEFINED_OBJECTS.values()
            ],
            "heatmap_url": "data:image/png;base64,SAMPLE_HEATMAP",
            "object_density": 0.035,
            "zones": [
                {"name": "loading_zone", "bbox": [0, 400, 300, 600], "object_count": 2},
                {"name": "assembly_line", "bbox": [600, 300, 1200, 550], "object_count": 3},
                {"name": "quality_station", "bbox": [750, 380, 980, 510], "object_count": 1},
            ],
        }
