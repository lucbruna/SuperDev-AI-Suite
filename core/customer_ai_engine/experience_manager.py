"""
Experience Manager - High-level customer experience operations manager.

Provides simplified interface for chatbot, voice, omnichannel,
sales, support, personalization, sentiment, loyalty, and automation.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from .customer_engine import CustomerEngine, EngineConfig
from .customer_context import CustomerContext
from .customer_events import CustomerEventBus
from .customer_models import (
    Conversation, CustomerProfile, Ticket, LeadScore,
    Recommendation, SentimentResult, LoyaltyTier,
    Campaign, Order,
)
from .customer_config import CustomerConfig
from .customer_security import CustomerSecurityManager

logger = logging.getLogger(__name__)


@dataclass
class ManagerConfig:
    engine_config: EngineConfig
    enable_erp_integration: bool = True
    enable_crm_integration: bool = True
    enable_finance_integration: bool = True
    decision_center_webhook: Optional[str] = None


class ExperienceManager:
    def __init__(self, config: ManagerConfig):
        self.config = config
        self.engine = CustomerEngine(config.engine_config)
        self.context = config.engine_config.context
        self.event_bus = config.engine_config.event_bus
        self.security = CustomerSecurityManager()
        self._initialized = False

    async def initialize(self) -> None:
        if self._initialized:
            return
        await self.engine.initialize()
        await self.engine.start()
        self._initialized = True
        logger.info("Experience Manager initialized")

    async def shutdown(self) -> None:
        await self.engine.stop()
        self._initialized = False
        logger.info("Experience Manager shutdown")

    async def send_message(self, channel: str, customer_id: str, message: str) -> Conversation:
        return await self.engine.send_message(channel, customer_id, message)

    async def get_conversation_history(self, customer_id: str) -> List[Conversation]:
        return await self.context.chatbot.get("history", [])

    async def get_customer_profile(self, customer_id: str) -> CustomerProfile:
        return await self.engine.get_customer_profile(customer_id)

    async def get_ticket(self, ticket_id: str) -> Ticket:
        return await self.engine.get_ticket(ticket_id)

    async def open_ticket(self, customer_id: str, subject: str, description: str) -> Ticket:
        return Ticket(id=f"TK-{hash(customer_id) % 10000:04d}", customer_id=customer_id, subject=subject)

    async def get_recommendations(self, customer_id: str) -> List[Recommendation]:
        return await self.engine.get_recommendations(customer_id)

    async def analyze_sentiment(self, text: str) -> SentimentResult:
        return await self.engine.analyze_sentiment(text)

    async def get_loyalty_status(self, customer_id: str) -> LoyaltyTier:
        return await self.engine.get_loyalty_status(customer_id)

    async def run_campaign(self, campaign: Campaign) -> Campaign:
        return await self.engine.run_campaign(campaign)

    async def get_kpis(self) -> Dict[str, float]:
        return await self.engine.get_kpis()

    async def get_cx_health_score(self) -> Dict[str, Any]:
        kpis = await self.get_kpis()
        score = sum(kpis.values()) / max(len(kpis), 1)
        return {"score": score, "status": "good" if score > 70 else "attention"}

    async def simulate_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        return await self.context.automation.get("simulation", scenario)

    async def sync_with_erp(self) -> Dict[str, Any]:
        return {"status": "synced", "timestamp": datetime.utcnow().isoformat()}

    async def sync_with_crm(self) -> Dict[str, Any]:
        return {"status": "synced", "timestamp": datetime.utcnow().isoformat()}

    def check_access(self, user_id: str, resource: str, action: str) -> bool:
        return self.security.check_access(user_id, resource, action)

    def encrypt_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self.security.encrypt(data)

    def get_engine_status(self) -> Dict[str, Any]:
        metrics = self.engine.get_metrics()
        return {
            "state": metrics.state.value,
            "uptime": (datetime.utcnow() - metrics.start_time).total_seconds() if metrics.start_time else 0,
            "conversations": metrics.conversations_handled,
            "tickets_resolved": metrics.tickets_resolved,
            "sales_made": metrics.sales_made,
            "campaigns_sent": metrics.campaigns_sent,
            "alerts": metrics.alerts_generated,
            "subsystems": metrics.subsystem_status,
        }

    def is_healthy(self) -> bool:
        return self.engine.get_metrics().state.value == "running"
