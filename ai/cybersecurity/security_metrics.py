"""
Security Metrics
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class MetricEntry:
    name: str
    value: float
    unit: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    tags: Dict[str, str] = field(default_factory=dict)


class SecurityMetrics:
    def __init__(self):
        self.metrics: Dict[str, List[MetricEntry]] = {}
        self.counters: Dict[str, int] = {}
        
    def record(self, name: str, value: float, unit: str = "", tags: Dict[str, str] = None) -> None:
        if name not in self.metrics:
            self.metrics[name] = []
        entry = MetricEntry(name=name, value=value, unit=unit, tags=tags or {})
        self.metrics[name].append(entry)
        if len(self.metrics[name]) > 10000:
            self.metrics[name] = self.metrics[name][-10000:]
            
    def increment(self, name: str, amount: int = 1) -> None:
        self.counters[name] = self.counters.get(name, 0) + amount
        
    def decrement(self, name: str, amount: int = 1) -> None:
        self.counters[name] = self.counters.get(name, 0) - amount
        
    def get_counter(self, name: str) -> int:
        return self.counters.get(name, 0)
        
    def get_latest(self, name: str) -> Optional[MetricEntry]:
        if name in self.metrics and self.metrics[name]:
            return self.metrics[name][-1]
        return None
        
    def get_average(self, name: str) -> float:
        entries = self.metrics.get(name, [])
        if not entries:
            return 0
        return sum(e.value for e in entries) / len(entries)
        
    def get_total(self, name: str) -> float:
        entries = self.metrics.get(name, [])
        return sum(e.value for e in entries)
        
    def get_all_counters(self) -> Dict[str, int]:
        return self.counters.copy()
        
    def get_summary(self) -> Dict[str, Any]:
        return {
            "metrics_count": len(self.metrics),
            "total_entries": sum(len(v) for v in self.metrics.values()),
            "counters": self.counters.copy(),
        }
        
    def reset(self) -> None:
        self.metrics.clear()
        self.counters.clear()
