"""CX Config — Configuration for customer experience."""
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CXConfigEntry:
    key: str
    value: Any
    description: str = ""


@dataclass
class CXConfig:
    enabled: bool = True
    max_customers: int = 100000
    default_tier: str = "bronze"
    loyalty_points_per_dollar: int = 10
    chatbot_enabled: bool = True
    sentiment_analysis_enabled: bool = True
    auto_escalation_threshold: float = 0.3
    recommendation_limit: int = 5
    ticket_timeout_hours: int = 24
    lead_score_threshold: float = 0.7
    journey_stages: list[str] = field(default_factory=lambda: [
        "awareness", "interest", "consideration", "purchase", "retention", "advocacy"
    ])
    custom_settings: dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        return self.custom_settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.custom_settings[key] = value
