from __future__ import annotations

from typing import Any


SAMPLE_RELATIONSHIPS = [
    {"subject": "conveyor_belt_01", "predicate": "transports", "object": "product_001", "confidence": 0.95},
    {"subject": "person_01", "predicate": "inspects", "object": "product_001", "confidence": 0.91},
    {"subject": "robot_arm_01", "predicate": "assembles", "object": "machine_02", "confidence": 0.88},
    {"subject": "forklift_01", "predicate": "carries", "object": "pallet_01", "confidence": 0.93},
    {"subject": "safety_barrier_01", "predicate": "protects", "object": "person_01", "confidence": 0.79},
]


class ImageUnderstanding:
    def __init__(self) -> None:
        self._understanding_count = 0

    async def understand_scene(self, image_data: bytes | str) -> dict[str, Any]:
        self._understanding_count += 1
        return {
            "scene_id": self._understanding_count,
            "scene_type": "industrial_manufacturing",
            "description": await self.describe_image(image_data),
            "objects": [
                {"type": "machine", "count": 3, "positions": ["left", "center", "right"]},
                {"type": "person", "count": 2, "activities": ["inspecting", "operating"]},
                {"type": "product", "count": 5, "stages": ["assembly", "inspection"]},
            ],
            "activities": ["assembly", "quality_inspection", "material_handling"],
            "safety_assessment": {
                "compliant": True,
                "violations": [],
                "ppe_compliance": 0.95,
            },
            "confidence": 0.91,
        }

    async def describe_image(self, image_data: bytes | str) -> dict[str, Any]:
        return {
            "brief": "An industrial manufacturing floor with conveyor belts, robotic arms, and workers conducting quality inspection.",
            "detailed": (
                "The image shows a well-lit manufacturing facility with a central conveyor system. "
                "Two robotic arms are working on the assembly line while a worker in safety gear "
                "inspects circuit boards at the quality control station. A forklift is transporting "
                "materials in the background."
            ),
            "tags": [
                "manufacturing", "factory", "automation", "quality_control",
                "safety", "assembly_line", "robotics", "industrial",
            ],
            "sentiment": "neutral",
            "complexity": "high",
        }

    async def answer_about_image(self, image_data: bytes | str, question: str) -> dict[str, Any]:
        qa_map: dict[str, str] = {
            "how many machines": "There are 2 machines visible: a CNC router and a conveyor belt system.",
            "is anyone wearing safety gear": "Yes, the worker in the scene is wearing a hard hat and safety vest.",
            "what is being produced": "Circuit boards are being assembled and inspected on the production line.",
        }
        for key, answer in qa_map.items():
            if key in question.lower():
                return {"question": question, "answer": answer, "confidence": 0.93}
        return {
            "question": question,
            "answer": "I cannot determine that from the image.",
            "confidence": 0.45,
        }

    async def extract_information(self, image_data: bytes | str, fields: list[str] | None = None) -> dict[str, Any]:
        info: dict[str, Any] = {
            "text_content": ["WARNING", "MAX SPEED 60", "CAUTION", "SERIAL: X7-9021-AB"],
            "barcodes": [
                {"type": "qr", "value": "https://example.com/product/X7-9021-AB", "bbox": [800, 50, 850, 100]},
            ],
            "faces": [],
            "license_plates": [],
            "signage": [
                {"text": "WARNING", "type": "safety_sign", "bbox": [10, 5, 120, 30]},
                {"text": "MAX SPEED 60", "type": "regulatory_sign", "bbox": [50, 100, 250, 140]},
            ],
            "colors": {
                "industrial_blue": {"hex": "#4682B4", "percentage": 40},
                "safety_yellow": {"hex": "#FFD700", "percentage": 15},
                "gray": {"hex": "#808080", "percentage": 30},
            },
        }
        if fields:
            return {k: v for k, v in info.items() if k in fields}
        return info

    async def identify_relationships(self, image_data: bytes | str) -> list[dict[str, Any]]:
        return SAMPLE_RELATIONSHIPS
