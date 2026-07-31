"""Metrics subsystem generator."""
import os

BASE = r'C:\Users\tomga\OneDrive\Desktop\super_dev_suite\SuperDev\ai\observability\metrics'

def w(path, content):
    full = os.path.join(BASE, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w', encoding='utf-8') as f:
        f.write(content)

w('metrics_engine.py', '''"""Metrics subsystem engine."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import time

class MetricsEngine:
    def __init__(self) -> None:
        self._collectors: List[str] = []
        self._aggregators: List[str] = []
        self._started = False
    def start(self) -> None:
        self._started = True
    def stop(self) -> None:
        self._started = False
    def is_running(self) -> bool:
        return self._started
    def add_collector(self, name: str) -> None:
        self._collectors.append(name)
    def add_aggregator(self, name: str) -> None:
        self._aggregators.append(name)
    def get_status(self) -> Dict[str, Any]:
        return {"running": self._started, "collectors": len(self._collectors), "aggregators": len(self._aggregators)}
''')

w('collector.py', '''"""Metrics collector."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import time

class MetricsCollector:
    def __init__(self, buffer_size: int = 1000) -> None:
        self._buffer: List[Dict[str, Any]] = []
        self._buffer_size = buffer_size
        self._total_collected = 0
    def collect(self, name: str, value: float, labels: Optional[Dict[str, str]] = None, metric_type: str = "gauge") -> bool:
        point = {"name": name, "value": value, "timestamp": time.time(), "labels": labels or {}, "type": metric_type}
        self._buffer.append(point)
        self._total_collected += 1
        if len(self._buffer) >= self._buffer_size:
            self.flush()
        return True
    def increment(self, name: str, amount: float = 1.0, labels: Optional[Dict[str, str]] = None) -> None:
        self.collect(name, amount, labels, "counter")
    def flush(self) -> int:
        n = len(self._buffer)
        self._buffer = []
        return n
    def get_buffer(self) -> List[Dict[str, Any]]:
        return list(self._buffer)
    def total_collected(self) -> int:
        return self._total_collected
''')

w('aggregator.py', '''"""Metrics aggregator."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import time

class MetricsAggregator:
    def __init__(self) -> None:
        self._series: Dict[str, List[float]] = {}
        self._windows: Dict[str, List[Dict[str, Any]]] = {}
    def add(self, name: str, value: float) -> None:
        self._series.setdefault(name, []).append(value)
        if len(self._series[name]) > 1000:
            self._series[name] = self._series[name][-1000:]
    def aggregate(self, name: str, window: int = 60) -> Dict[str, float]:
        values = self._series.get(name, [])
        if not values:
            return {"min": 0, "max": 0, "avg": 0, "sum": 0, "count": 0}
        recent = values[-window:]
        return {"min": min(recent), "max": max(recent), "avg": sum(recent)/len(recent), "sum": sum(recent), "count": len(recent)}
    def percentile(self, name: str, p: float = 95.0) -> float:
        values = sorted(self._series.get(name, []))
        if not values:
            return 0.0
        idx = int(len(values) * p / 100)
        return values[min(idx, len(values)-1)]
    def get_series(self, name: str) -> List[float]:
        return list(self._series.get(name, []))
    def list_names(self) -> List[str]:
        return list(self._series.keys())
    def clear(self, name: str = "") -> int:
        if name:
            n = len(self._series.get(name, []))
            self._series.pop(name, None)
            return n
        n = sum(len(v) for v in self._series.values())
        self._series.clear()
        return n
''')

w('calculator.py', '''"""Metrics calculator."""
from __future__ import annotations
from typing import Any, Dict, List

class MetricsCalculator:
    @staticmethod
    def rate(values: List[float], window: int = 10) -> float:
        if len(values) < 2 or window < 1:
            return 0.0
        recent = values[-window:]
        return (recent[-1] - recent[0]) / max(len(recent)-1, 1)
    @staticmethod
    def moving_average(values: List[float], window: int = 5) -> float:
        if not values:
            return 0.0
        recent = values[-window:]
        return sum(recent) / len(recent)
    @staticmethod
    def standard_deviation(values: List[float]) -> float:
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
    @staticmethod
    def z_score(value: float, values: List[float]) -> float:
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        std = MetricsCalculator.standard_deviation(values)
        if std == 0:
            return 0.0
        return (value - mean) / std
    @staticmethod
    def trend(values: List[float]) -> str:
        if len(values) < 3:
            return "stable"
        first_half = sum(values[:len(values)//2]) / max(len(values)//2, 1)
        second_half = sum(values[len(values)//2:]) / max(len(values)//2, 1)
        if second_half > first_half * 1.1:
            return "increasing"
        elif second_half < first_half * 0.9:
            return "decreasing"
        return "stable"
''')

w('storage.py', '''"""Metrics storage."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import time

class MetricsStorage:
    def __init__(self, max_series: int = 10000, max_points: int = 1000) -> None:
        self._data: Dict[str, List[Dict[str, Any]]] = {}
        self._max_series = max_series
        self._max_points = max_points
    def store(self, name: str, value: float, labels: Optional[Dict[str, str]] = None, timestamp: float = 0.0) -> bool:
        point = {"value": value, "timestamp": timestamp or time.time(), "labels": labels or {}}
        self._data.setdefault(name, []).append(point)
        if len(self._data[name]) > self._max_points:
            self._data[name] = self._data[name][-self._max_points:]
        return True
    def query(self, name: str, start: float = 0, end: float = 0) -> List[Dict[str, Any]]:
        points = self._data.get(name, [])
        if start:
            points = [p for p in points if p["timestamp"] >= start]
        if end:
            points = [p for p in points if p["timestamp"] <= end]
        return points
    def get_latest(self, name: str) -> Optional[float]:
        points = self._data.get(name, [])
        return points[-1]["value"] if points else None
    def list_names(self) -> List[str]:
        return list(self._data.keys())
    def clear(self, name: str = "") -> int:
        if name:
            n = len(self._data.get(name, []))
            self._data.pop(name, None)
            return n
        n = sum(len(v) for v in self._data.values())
        self._data.clear()
        return n
''')

w('exporter.py', '''"""Metrics exporter."""
from __future__ import annotations
from typing import Any, Dict, List
import json, time

class MetricsExporter:
    def __init__(self) -> None:
        self._exports: List[Dict[str, Any]] = []
    def export_prometheus(self, data: Dict[str, List[Dict[str, Any]]]) -> str:
        lines = []
        for name, points in data.items():
            lines.append(f"# HELP {name} {name} metric")
            lines.append(f"# TYPE {name} gauge")
            for p in points[-1:]:
                labels = ",".join(f'{k}="{v}"' for k, v in p.get("labels", {}).items())
                label_str = f"{{{labels}}}" if labels else ""
                lines.append(f"{name}{label_str} {p['value']}")
        self._exports.append({"format": "prometheus", "timestamp": time.time(), "size": len(lines)})
        return "\\n".join(lines)
    def export_json(self, data: Dict[str, List[Dict[str, Any]]]) -> str:
        self._exports.append({"format": "json", "timestamp": time.time(), "size": len(data)})
        return json.dumps(data, indent=2)
    def export_csv(self, data: Dict[str, List[Dict[str, Any]]]) -> str:
        lines = ["name,value,timestamp"]
        for name, points in data.items():
            for p in points:
                lines.append(f"{name},{p['value']},{p.get('timestamp', '')}")
        self._exports.append({"format": "csv", "timestamp": time.time(), "size": len(lines)})
        return "\\n".join(lines)
    def get_export_history(self) -> List[Dict[str, Any]]:
        return list(self._exports)
''')

w('threshold.py', '''"""Metrics thresholds."""
from __future__ import annotations
from typing import Any, Callable, Dict, List, Optional

class Threshold:
    def __init__(self, name: str, warning: float = 0, critical: float = 0) -> None:
        self.name = name
        self.warning = warning
        self.critical = critical
        self.breached = False
    def check(self, value: float) -> str:
        if value >= self.critical:
            self.breached = True
            return "critical"
        if value >= self.warning:
            self.breached = True
            return "warning"
        self.breached = False
        return "ok"

class MetricsThresholdManager:
    def __init__(self) -> None:
        self._thresholds: Dict[str, Threshold] = {}
        self._violations: List[Dict[str, Any]] = []
    def add_threshold(self, name: str, warning: float, critical: float) -> None:
        self._thresholds[name] = Threshold(name, warning, critical)
    def remove_threshold(self, name: str) -> bool:
        if name in self._thresholds:
            del self._thresholds[name]
            return True
        return False
    def check(self, name: str, value: float) -> str:
        t = self._thresholds.get(name)
        if not t:
            return "no_threshold"
        status = t.check(value)
        if status != "ok":
            self._violations.append({"name": name, "value": value, "status": status})
        return status
    def get_violations(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self._violations[-limit:]
    def list_thresholds(self) -> List[Dict[str, Any]]:
        return [{"name": t.name, "warning": t.warning, "critical": t.critical, "breached": t.breached} for t in self._thresholds.values()]
''')

w('__init__.py', '''"""Metrics subsystem."""
from .metrics_engine import MetricsEngine
from .collector import MetricsCollector
from .aggregator import MetricsAggregator
from .calculator import MetricsCalculator
from .storage import MetricsStorage
from .exporter import MetricsExporter
from .threshold import MetricsThresholdManager

__all__ = [
    "MetricsEngine", "MetricsCollector", "MetricsAggregator",
    "MetricsCalculator", "MetricsStorage", "MetricsExporter",
    "MetricsThresholdManager"
]
''')

print("metrics/: 8 files created")
