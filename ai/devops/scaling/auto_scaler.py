"""Auto scaler."""
from __future__ import annotations
from typing import Any, Dict, List

class AutoScaler:
    def __init__(self) -> None:
        self._scales: Dict[str, Dict[str, Any]] = {}
    def configure(self, name: str, min: int = 1, max: int = 10, metric: str = "cpu") -> Dict[str, Any]:
        config = {"name": name, "min": min, "max": max, "metric": metric, "current": min}
        self._scales[name] = config
        return config
    def scale(self, name: str, value: float, threshold: float = 70.0) -> Dict[str, Any]:
        if name not in self._scales:
            return {"error": "not_found"}
        config = self._scales[name]
        if value > threshold and config["current"] < config["max"]:
            config["current"] += 1
            return {"name": name, "action": "scaled_up", "replicas": config["current"]}
        elif value < threshold * 0.5 and config["current"] > config["min"]:
            config["current"] -= 1
            return {"name": name, "action": "scaled_down", "replicas": config["current"]}
        return {"name": name, "action": "maintained", "replicas": config["current"]}
    def get(self, name: str) -> Dict[str, Any]:
        return self._scales.get(name, {"error": "not_found"})
    def list_all(self) -> List[Dict[str, Any]]:
        return list(self._scales.values())
    def count(self) -> int:
        return len(self._scales)
