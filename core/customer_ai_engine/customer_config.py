"""
Customer Configuration - Global customer AI engine configuration.
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ChatbotConfig:
    auto_respond: bool = True
    confidence_threshold: float = 0.7
    enable_knowledge_search: bool = True
    max_context_messages: int = 50
    fallback_message: str = "I'll transfer you to a human agent."
    language: str = "pt-BR"


@dataclass
class VoiceConfig:
    enabled: bool = True
    stt_language: str = "pt-BR"
    tts_voice: str = "default"
    max_call_duration_minutes: int = 30
    enable_recording: bool = True
    enable_transcription: bool = True


@dataclass
class OmnichannelConfig:
    enable_whatsapp: bool = True
    enable_email: bool = True
    enable_webchat: bool = True
    enable_social: bool = False
    enable_sms: bool = False
    history_unification: bool = True


@dataclass
class SalesConfig:
    enable_lead_scoring: bool = True
    enable_recommendations: bool = True
    min_lead_score_for_action: float = 60.0
    recommendation_limit: int = 5
    conversion_prediction_enabled: bool = True


@dataclass
class SupportConfig:
    auto_ticket_creation: bool = True
    enable_smart_routing: bool = True
    enable_solution_recommendation: bool = True
    escalation_timeout_minutes: int = 30
    max_tickets_per_agent: int = 10
    sla_hours_critical: int = 4
    sla_hours_high: int = 8
    sla_hours_medium: int = 24
    sla_hours_low: int = 72


@dataclass
class PersonalizationConfig:
    enable_behavior_tracking: bool = True
    enable_profile_analysis: bool = True
    profile_update_frequency_hours: int = 24
    max_segments_per_customer: int = 5


@dataclass
class SentimentConfig:
    enable_emotion_detection: bool = True
    enable_satisfaction_analysis: bool = True
    alert_on_negative: bool = True
    negative_threshold: float = 0.4
    analysis_language: str = "pt-BR"


@dataclass
class LoyaltyConfig:
    enable_rewards: bool = True
    points_per_currency_spent: float = 1.0
    tier_upgrade_points: Dict[str, int] = field(default_factory=lambda: {"silver": 1000, "gold": 5000, "platinum": 20000, "diamond": 50000})
    retention_campaign_days: int = 90


@dataclass
class AutomationConfig:
    enable_campaigns: bool = True
    enable_triggers: bool = True
    enable_workflows: bool = True
    max_campaigns_per_day: int = 5
    workflow_execution_limit: int = 1000


@dataclass
class SecurityConfig:
    enable_encryption: bool = True
    enable_access_control: bool = True
    audit_trail_enabled: bool = True
    sensitive_fields: List[str] = field(default_factory=lambda: ["phone", "email", "address", "payment_info", "conversation"])
    session_timeout_minutes: int = 30


@dataclass
class IntegrationConfig:
    enable_erp_sync: bool = True
    enable_crm_sync: bool = True
    enable_finance_sync: bool = True
    crm_sync_interval_minutes: int = 60
    decision_center_enabled: bool = True


@dataclass
class CustomerConfig:
    engine_name: str = "CustomerAIEngine"
    engine_version: str = "1.0.0"
    environment: str = "production"
    log_level: str = "INFO"
    enable_telemetry: bool = True
    chatbot: ChatbotConfig = field(default_factory=ChatbotConfig)
    voice: VoiceConfig = field(default_factory=VoiceConfig)
    omnichannel: OmnichannelConfig = field(default_factory=OmnichannelConfig)
    sales: SalesConfig = field(default_factory=SalesConfig)
    support: SupportConfig = field(default_factory=SupportConfig)
    personalization: PersonalizationConfig = field(default_factory=PersonalizationConfig)
    sentiment: SentimentConfig = field(default_factory=SentimentConfig)
    loyalty: LoyaltyConfig = field(default_factory=LoyaltyConfig)
    automation: AutomationConfig = field(default_factory=AutomationConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    integrations: IntegrationConfig = field(default_factory=IntegrationConfig)
    enable_customer_digital_twin: bool = True
    enable_autonomous_cx: bool = True
    enable_continuous_learning: bool = True
    _extra: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CustomerConfig":
        config = cls()
        for key, value in data.items():
            if hasattr(config, key) and not key.startswith("_"):
                if isinstance(value, dict) and key in cls.__dataclass_fields__:
                    sub = getattr(config, key)
                    if hasattr(sub, "__dataclass_fields__"):
                        for sk, sv in value.items():
                            if hasattr(sub, sk):
                                setattr(sub, sk, sv)
                        continue
                setattr(config, key, value)
            else:
                config._extra[key] = value
        return config

    @classmethod
    def from_json(cls, path: str) -> "CustomerConfig":
        if not os.path.exists(path):
            return cls()
        with open(path) as f:
            return cls.from_dict(json.load(f))

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self, path: str) -> None:
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2, default=str)

    def validate(self) -> List[str]:
        errors = []
        if self.chatbot.confidence_threshold < 0 or self.chatbot.confidence_threshold > 1:
            errors.append("confidence_threshold must be between 0 and 1")
        if self.sales.min_lead_score_for_action < 0:
            errors.append("min_lead_score_for_action must be positive")
        if self.loyalty.points_per_currency_spent <= 0:
            errors.append("points_per_currency_spent must be positive")
        return errors
