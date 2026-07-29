from __future__ import annotations

from typing import Any


SAMPLE_COLORS = [
    {"name": "crimson", "hex": "#DC143C", "rgb": (220, 20, 60), "percentage": 15.2},
    {"name": "steel_blue", "hex": "#4682B4", "rgb": (70, 130, 180), "percentage": 32.7},
    {"name": "dark_slate_gray", "hex": "#2F4F4F", "rgb": (47, 79, 79), "percentage": 28.1},
    {"name": "white_smoke", "hex": "#F5F5F5", "rgb": (245, 245, 245), "percentage": 14.0},
    {"name": "goldenrod", "hex": "#DAA520", "rgb": (218, 165, 32), "percentage": 10.0},
]

SAMPLE_TEXT = [
    {"text": "WARNING", "confidence": 0.98, "bbox": [10, 5, 120, 30], "language": "en"},
    {"text": "MAX SPEED 60", "confidence": 0.95, "bbox": [50, 100, 250, 140], "language": "en"},
    {"text": "CAUTION", "confidence": 0.92, "bbox": [300, 200, 420, 230], "language": "en"},
    {"text": "SERIAL: X7-9021-AB", "confidence": 0.88, "bbox": [400, 50, 600, 75], "language": "en"},
]

SAMPLE_CLASSIFICATIONS = [
    {"category": "industrial_equipment", "confidence": 0.93, "subcategories": ["machinery", "conveyor_belt"]},
    {"category": "manufacturing_floor", "confidence": 0.87, "subcategories": ["factory", "assembly_line"]},
]


class ImageAnalyzer:
    def __init__(self) -> None:
        self._cache: dict[int, dict[str, Any]] = {}
        self._analysis_count = 0

    async def analyze_image(self, image_data: bytes | str) -> dict[str, Any]:
        cache_key = hash(image_data) if isinstance(image_data, bytes) else hash(image_data)
        if cache_key in self._cache:
            return self._cache[cache_key]
        self._analysis_count += 1
        result = {
            "analysis_id": self._analysis_count,
            "description": await self.describe_image(image_data),
            "colors": await self.extract_colors(image_data),
            "text": await self.detect_text(image_data),
            "classification": await self.classify_image(image_data),
            "metadata": await self.get_metadata(image_data),
            "objects_detected": 7,
            "dominant_color": "#4682B4",
            "brightness": 0.72,
            "contrast": 0.64,
            "sharpness": 0.81,
            "has_faces": False,
            "has_text": True,
        }
        self._cache[cache_key] = result
        return result

    async def extract_colors(self, image_data: bytes | str) -> list[dict[str, Any]]:
        return SAMPLE_COLORS

    async def detect_text(self, image_data: bytes | str) -> list[dict[str, Any]]:
        return SAMPLE_TEXT

    async def classify_image(self, image_data: bytes | str) -> dict[str, Any]:
        return SAMPLE_CLASSIFICATIONS[0]

    async def get_metadata(self, image_data: bytes | str) -> dict[str, Any]:
        return {
            "format": "JPEG",
            "width": 1920,
            "height": 1080,
            "color_space": "sRGB",
            "bit_depth": 8,
            "channels": 3,
            "compression": "lossy",
            "file_size_bytes": len(image_data) if isinstance(image_data, bytes) else 245760,
            "has_exif": True,
            "exif": {
                "make": "Canon",
                "model": "EOS R5",
                "focal_length_mm": 50,
                "aperture": 2.8,
                "iso": 800,
                "exposure_time": "1/250",
                "date_taken": "2026-07-28T14:30:00",
            },
            "dpi": (300, 300),
        }

    def clear_cache(self) -> None:
        self._cache.clear()
