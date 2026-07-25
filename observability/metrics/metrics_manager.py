from typing import Dict
from .prometheus_metrics import Counter, Gauge, Histogram


class MetricsManager:
    def __init__(self) -> None:
        self._counters: Dict[str, Counter] = {}
        self._gauges: Dict[str, Gauge] = {}
        self._histograms: Dict[str, Histogram] = {}

    def counter(self, name: str, description: str = "") -> Counter:
        if name not in self._counters:
            self._counters[name] = Counter(name, description)
        return self._counters[name]

    def gauge(self, name: str, description: str = "") -> Gauge:
        if name not in self._gauges:
            self._gauges[name] = Gauge(name, description)
        return self._gauges[name]

    def histogram(self, name: str, description: str = "") -> Histogram:
        if name not in self._histograms:
            self._histograms[name] = Histogram(name, description)
        return self._histograms[name]

    def get_all(self) -> Dict[str, Dict[str, object]]:
        return {
            "counters": {n: c.export() for n, c in self._counters.items()},
            "gauges": {n: g.export() for n, g in self._gauges.items()},
            "histograms": {n: h.export() for n, h in self._histograms.items()},
        }

    def reset(self) -> None:
        self._counters.clear()
        self._gauges.clear()
        self._histograms.clear()
