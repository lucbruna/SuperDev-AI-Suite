"""Anomaly detection engine."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import time

class AnomalyEngine:
    def __init__(self) -> None:
        self._detectors: Dict[str, Any] = {}
        self._anomalies: List[Dict[str, Any]] = []
        self._started = False
    def start(self) -> None:
        self._started = True
    def stop(self) -> None:
        self._started = False
    def register_detector(self, name: str, detector: Any) -> None:
        self._detectors[name] = detector
    def detect(self, metric_name: str, value: float) -> Dict[str, Any]:
        result = {"metric": metric_name, "value": value, "timestamp": time.time(), "anomalies": []}
        for name, detector in self._detectors.items():
            if hasattr(detector, 'check'):
                try:
                    is_anomaly = detector.check(metric_name, value)
                    if is_anomaly:
                        result["anomalies"].append({"detector": name, "anomaly": True})
                except Exception:
                    pass
        if result["anomalies"]:
            self._anomalies.append(result)
        return result
    def get_anomalies(self, limit: int = 100) -> List[Dict[str, Any]]:
        return self._anomalies[-limit:]
    def get_status(self) -> Dict[str, Any]:
        return {"running": self._started, "detectors": len(self._detectors), "anomalies_detected": len(self._anomalies)}
