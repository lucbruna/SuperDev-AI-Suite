"""Reusable, editable scene-object presets for the DARKSTUDIO studios.

Objects are intentionally represented as SceneCanvas primitives so they can
be recolored, repositioned, animated, and rendered without external assets.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any


OBJECTS: dict[str, dict[str, Any]] = {
    "thermometer": {
        "id": "thermometer", "name": "Termômetro", "studio_id": "whymentary",
        "category": "health", "description": "Termômetro clínico ilustrado",
        "primitives": {
            "rects": [{"x": 0, "y": 0, "w": 14, "h": 76, "color": "#F8FAFC", "outline": "#334155"},
                      {"x": 4, "y": 18, "w": 6, "h": 48, "color": "#EF4444"}],
            "circles": [{"x": 7, "y": 73, "radius": 12, "color": "#EF4444"}],
        },
    },
    "water_glass": {
        "id": "water_glass", "name": "Copo de água", "studio_id": "whymentary",
        "category": "health", "description": "Copo transparente com água",
        "primitives": {
            "rects": [{"x": 0, "y": 0, "w": 48, "h": 62, "color": "#BFDBFE", "outline": "#2563EB"},
                      {"x": 3, "y": 28, "w": 42, "h": 31, "color": "#60A5FA"}],
        },
    },
    "coffee_cup": {
        "id": "coffee_cup", "name": "Xícara de café", "studio_id": "whymentary",
        "category": "health", "description": "Xícara de café vista de frente",
        "primitives": {
            "rects": [{"x": 0, "y": 12, "w": 48, "h": 34, "color": "#F8FAFC", "outline": "#334155"},
                      {"x": 9, "y": 4, "w": 30, "h": 10, "color": "#78350F"}],
            "circles": [{"x": 52, "y": 28, "radius": 12, "color": "#F8FAFC"}],
        },
    },
    "phone": {
        "id": "phone", "name": "Celular", "studio_id": "whymentary",
        "category": "technology", "description": "Smartphone ilustrado",
        "primitives": {
            "rects": [{"x": 0, "y": 0, "w": 42, "h": 76, "color": "#1F2937", "outline": "#111827"},
                      {"x": 4, "y": 8, "w": 34, "h": 58, "color": "#93C5FD"}],
            "circles": [{"x": 21, "y": 71, "radius": 2, "color": "#F8FAFC"}],
        },
    },
    "stethoscope": {
        "id": "stethoscope", "name": "Estetoscópio", "studio_id": "whymentary",
        "category": "health", "description": "Estetoscópio médico simplificado",
        "primitives": {
            "lines": [{"x1": 8, "y1": 0, "x2": 8, "y2": 42, "color": "#2563EB", "width": 5},
                      {"x1": 8, "y1": 42, "x2": 40, "y2": 42, "color": "#2563EB", "width": 5},
                      {"x1": 40, "y1": 42, "x2": 40, "y2": 12, "color": "#2563EB", "width": 5}],
            "circles": [{"x": 40, "y": 8, "radius": 8, "color": "#94A3B8"}],
        },
    },
    "parchment_map": {
        "id": "parchment_map", "name": "Mapa antigo", "studio_id": "historical_documentary",
        "category": "history", "description": "Mapa de pergaminho envelhecido",
        "primitives": {
            "rects": [{"x": 0, "y": 0, "w": 150, "h": 100, "color": "#C9A66B", "outline": "#6B4F2A"},
                      {"x": 16, "y": 18, "w": 112, "h": 3, "color": "#8B6B43"},
                      {"x": 28, "y": 46, "w": 92, "h": 3, "color": "#8B6B43"}],
        },
    },
    "stone_column": {
        "id": "stone_column", "name": "Coluna de pedra", "studio_id": "historical_documentary",
        "category": "architecture", "description": "Coluna clássica de pedra",
        "primitives": {
            "rects": [{"x": 18, "y": 20, "w": 44, "h": 112, "color": "#A8A29E"},
                      {"x": 8, "y": 10, "w": 64, "h": 14, "color": "#D6D3D1"},
                      {"x": 8, "y": 128, "w": 64, "h": 14, "color": "#78716C"}],
        },
    },
    "torch": {
        "id": "torch", "name": "Tocha", "studio_id": "historical_documentary",
        "category": "environment", "description": "Tocha acesa para cenário histórico",
        "primitives": {
            "rects": [{"x": 12, "y": 28, "w": 12, "h": 70, "color": "#78350F"}],
            "circles": [{"x": 18, "y": 18, "radius": 13, "color": "#F97316"},
                        {"x": 18, "y": 11, "radius": 7, "color": "#FDE68A"}],
        },
    },
    "compass": {
        "id": "compass", "name": "Bússola", "studio_id": "historical_documentary",
        "category": "navigation", "description": "Bússola antiga de navegação",
        "primitives": {
            "circles": [{"x": 35, "y": 35, "radius": 34, "color": "#B08D57"},
                        {"x": 35, "y": 35, "radius": 26, "color": "#E7D8B1"},
                        {"x": 35, "y": 35, "radius": 4, "color": "#7F1D1D"}],
            "lines": [{"x1": 35, "y1": 8, "x2": 35, "y2": 62, "color": "#7F1D1D", "width": 3},
                      {"x1": 8, "y1": 35, "x2": 62, "y2": 35, "color": "#44403C", "width": 2}],
        },
    },
    "sailing_ship": {
        "id": "sailing_ship", "name": "Navio à vela", "studio_id": "historical_documentary",
        "category": "transport", "description": "Navio histórico estilizado",
        "primitives": {
            "rects": [{"x": 0, "y": 70, "w": 120, "h": 18, "color": "#78350F"},
                      {"x": 57, "y": 8, "w": 5, "h": 64, "color": "#451A03"}],
            "rects": [{"x": 64, "y": 16, "w": 38, "h": 46, "color": "#F5E6C8"},
                      {"x": 22, "y": 24, "w": 30, "h": 40, "color": "#E7D8B1"}],
        },
    },
}


def list_scene_objects(studio_id: str | None = None) -> list[dict[str, Any]]:
    """Return object metadata filtered by studio, without exposing mutable data."""
    if studio_id not in (None, "whymentary", "historical_documentary"):
        raise ValueError(f"Unknown studio '{studio_id}'")
    return [
        {key: value for key, value in item.items() if key != "primitives"}
        for item in OBJECTS.values()
        if studio_id is None or item["studio_id"] == studio_id
    ]


def compose_scene_object(
    scene: dict[str, Any], object_id: str, *, x: float = 0, y: float = 0,
    scale: float = 1.0,
) -> dict[str, Any]:
    """Copy a scene and append translated/scaled primitives for one library object."""
    if object_id not in OBJECTS:
        raise ValueError(f"Unknown scene object '{object_id}'")
    if scale <= 0:
        raise ValueError("scale must be greater than zero")
    result = deepcopy(scene)
    item = OBJECTS[object_id]
    result.setdefault("object_ids", []).append(object_id)
    for layer, primitives in item["primitives"].items():
        transformed = []
        for primitive in primitives:
            current = deepcopy(primitive)
            for key in ("x", "x1"):
                if key in current:
                    current[key] = x + float(current[key]) * scale
            for key in ("y", "y1"):
                if key in current:
                    current[key] = y + float(current[key]) * scale
            for key in ("w", "h", "radius", "width"):
                if key in current:
                    current[key] = float(current[key]) * scale
            if "x2" in current:
                current["x2"] = x + float(current["x2"]) * scale
            if "y2" in current:
                current["y2"] = y + float(current["y2"]) * scale
            if "points" in current:
                current["points"] = [
                    [x + float(px) * scale, y + float(py) * scale]
                    for px, py in current["points"]
                ]
            transformed.append(current)
        result.setdefault(layer, []).extend(transformed)
    return result
