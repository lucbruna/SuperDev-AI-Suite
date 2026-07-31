"""
Dashboard Home Component
"""
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field


@dataclass
class MetricCard:
    title: str
    value: str
    change: float = 0.0
    change_type: str = "increase"
    icon: str = ""
    color: str = "blue"


@dataclass
class ActivityItem:
    id: str
    title: str
    description: str
    timestamp: str = ""
    icon: str = ""
    type: str = "info"


class DashboardHome:
    def __init__(self):
        self.metrics: List[MetricCard] = []
        self.activities: List[ActivityItem] = []
        self.welcome_message: str = "Welcome to SuperDev AI Suite"
        
    def add_metric(self, metric: MetricCard) -> None:
        self.metrics.append(metric)
        
    def add_activity(self, activity: ActivityItem) -> None:
        self.activities.insert(0, activity)
        if len(self.activities) > 50:
            self.activities = self.activities[:50]
            
    def render(self) -> Dict[str, Any]:
        return {
            "welcomeMessage": self.welcome_message,
            "metrics": [{"title": m.title, "value": m.value, "change": m.change} for m in self.metrics],
            "activities": [{"title": a.title, "description": a.description} for a in self.activities[:10]],
        }
