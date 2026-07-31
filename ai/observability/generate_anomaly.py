"""Anomaly subsystem generator."""

import os

BASE = r"C:\Users\tomga\OneDrive\Desktop\super_dev_suite\SuperDev\ai\observability\anomaly"


def w(path, content):
    full = os.path.join(BASE, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)


w(
    "anomaly_engine.py",
    '''"""Anomaly detection engine."""
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
''',
)

w(
    "detector.py",
    '''"""Anomaly detector."""
from __future__ import annotations
from typing import Any, Dict, List
import statistics

class StatisticalDetector:
    def __init__(self, sensitivity: float = 2.0) -> None:
        self._sensitivity = sensitivity
        self._history: Dict[str, List[float]] = {}
    def record(self, metric_name: str, value: float) -> None:
        self._history.setdefault(metric_name, []).append(value)
        if len(self._history[metric_name]) > 1000:
            self._history[metric_name] = self._history[metric_name][-1000:]
    def check(self, metric_name: str, value: float) -> bool:
        values = self._history.get(metric_name, [])
        if len(values) < 10:
            return False
        mean = statistics.mean(values)
        stdev = statistics.stdev(values)
        if stdev == 0:
            return False
        z_score = abs(value - mean) / stdev
        return z_score > self._sensitivity
    def get_stats(self, metric_name: str) -> Dict[str, float]:
        values = self._history.get(metric_name, [])
        if not values:
            return {"mean": 0, "stdev": 0, "count": 0}
        return {"mean": statistics.mean(values), "stdev": statistics.stdev(values) if len(values) > 1 else 0, "count": len(values)}
    def list_metrics(self) -> List[str]:
        return list(self._history.keys())
    def clear(self, metric_name: str = "") -> int:
        if metric_name:
            n = len(self._history.get(metric_name, []))
            self._history.pop(metric_name, None)
            return n
        n = sum(len(v) for v in self._history.values())
        self._history.clear()
        return n
''',
)

w(
    "baseline.py",
    '''"""Baseline management."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import time

class BaselineManager:
    def __init__(self) -> None:
        self._baselines: Dict[str, Dict[str, Any]] = {}
    def set_baseline(self, metric_name: str, mean: float, std: float, min_val: float = 0, max_val: float = 0) -> Dict[str, Any]:
        baseline = {"metric": metric_name, "mean": mean, "std": std, "min": min_val, "max": max_val, "updated_at": time.time()}
        self._baselines[metric_name] = baseline
        return baseline
    def get_baseline(self, metric_name: str) -> Optional[Dict[str, Any]]:
        return self._baselines.get(metric_name)
    def update_from_data(self, metric_name: str, values: List[float]) -> Dict[str, Any]:
        import statistics
        if not values:
            return {"error": "no_data"}
        mean = statistics.mean(values)
        std = statistics.stdev(values) if len(values) > 1 else 0
        return self.set_baseline(metric_name, mean, std, min(values), max(values))
    def is_within_baseline(self, metric_name: str, value: float, multiplier: float = 2.0) -> bool:
        baseline = self._baselines.get(metric_name)
        if not baseline:
            return True
        lower = baseline["mean"] - multiplier * baseline["std"]
        upper = baseline["mean"] + multiplier * baseline["std"]
        return lower <= value <= upper
    def list_baselines(self) -> List[Dict[str, Any]]:
        return list(self._baselines.values())
    def remove_baseline(self, metric_name: str) -> bool:
        if metric_name in self._baselines:
            del self._baselines[metric_name]
            return True
        return False
''',
)

w(
    "pattern_analysis.py",
    '''"""Pattern analysis."""
from __future__ import annotations
from typing import Any, Dict, List

class PatternAnalyzer:
    def __init__(self) -> None:
        self._patterns: Dict[str, List[float]] = {}
    def record(self, metric_name: str, value: float) -> None:
        self._patterns.setdefault(metric_name, []).append(value)
        if len(self._patterns[metric_name]) > 1000:
            self._patterns[metric_name] = self._patterns[metric_name][-1000:]
    def detect_trend(self, metric_name: str) -> str:
        values = self._patterns.get(metric_name, [])
        if len(values) < 5:
            return "insufficient_data"
        recent = values[-5:]
        if all(recent[i] <= recent[i+1] for i in range(len(recent)-1)):
            return "increasing"
        if all(recent[i] >= recent[i+1] for i in range(len(recent)-1)):
            return "decreasing"
        return "fluctuating"
    def detect_periodicity(self, metric_name: str, period: int = 24) -> bool:
        values = self._patterns.get(metric_name, [])
        if len(values) < period * 2:
            return False
        correlations = []
        for i in range(len(values) - period):
            correlations.append(values[i] * values[i + period])
        avg_corr = sum(correlations) / len(correlations) if correlations else 0
        return avg_corr > 0
    def list_metrics(self) -> List[str]:
        return list(self._patterns.keys())
    def get_values(self, metric_name: str) -> List[float]:
        return list(self._patterns.get(metric_name, []))
''',
)

w(
    "prediction.py",
    '''"""Anomaly prediction."""
from __future__ import annotations
from typing import Any, Dict, List
import statistics

class AnomalyPredictor:
    def __init__(self) -> None:
        self._history: Dict[str, List[float]] = {}
    def record(self, metric_name: str, value: float) -> None:
        self._history.setdefault(metric_name, []).append(value)
        if len(self._history[metric_name]) > 1000:
            self._history[metric_name] = self._history[metric_name][-1000:]
    def predict_next(self, metric_name: str) -> Dict[str, float]:
        values = self._history.get(metric_name, [])
        if len(values) < 3:
            return {"predicted": 0, "confidence": 0}
        mean = statistics.mean(values[-10:])
        trend = (values[-1] - values[-min(10, len(values))]) / max(min(10, len(values)), 1)
        predicted = values[-1] + trend
        stdev = statistics.stdev(values) if len(values) > 1 else 0
        confidence = max(0, 1 - (stdev / max(abs(mean), 1)))
        return {"predicted": predicted, "confidence": confidence}
    def predict_anomaly_probability(self, metric_name: str, value: float) -> float:
        values = self._history.get(metric_name, [])
        if len(values) < 10:
            return 0.0
        mean = statistics.mean(values)
        stdev = statistics.stdev(values)
        if stdev == 0:
            return 0.0
        z = abs(value - mean) / stdev
        return min(z / 4.0, 1.0)
    def list_metrics(self) -> List[str]:
        return list(self._history.keys())
''',
)

w(
    "scoring.py",
    '''"""Anomaly scoring."""
from __future__ import annotations
from typing import Any, Dict, List

class AnomalyScorer:
    def __init__(self) -> None:
        self._scores: List[Dict[str, Any]] = []
    def score(self, metric: str, value: float, baseline_mean: float, baseline_std: float) -> Dict[str, Any]:
        if baseline_std == 0:
            z_score = 0
        else:
            z_score = abs(value - baseline_mean) / baseline_std
        severity = "low"
        if z_score > 3:
            severity = "critical"
        elif z_score > 2.5:
            severity = "high"
        elif z_score > 2:
            severity = "medium"
        result = {"metric": metric, "value": value, "z_score": z_score, "severity": severity}
        self._scores.append(result)
        return result
    def get_scores(self, severity: str = "", limit: int = 100) -> List[Dict[str, Any]]:
        results = self._scores
        if severity:
            results = [s for s in results if s["severity"] == severity]
        return results[-limit:]
    def get_summary(self) -> Dict[str, int]:
        summary: Dict[str, int] = {}
        for s in self._scores:
            sev = s["severity"]
            summary[sev] = summary.get(sev, 0) + 1
        return summary
    def clear(self) -> int:
        n = len(self._scores)
        self._scores.clear()
        return n
''',
)

w(
    "__init__.py",
    '''"""Anomaly subsystem."""
from .anomaly_engine import AnomalyEngine
from .detector import StatisticalDetector
from .baseline import BaselineManager
from .pattern_analysis import PatternAnalyzer
from .prediction import AnomalyPredictor
from .scoring import AnomalyScorer

__all__ = [
    "AnomalyEngine", "StatisticalDetector", "BaselineManager",
    "PatternAnalyzer", "AnomalyPredictor", "AnomalyScorer"
]
''',
)

print("anomaly/: 7 files created")
