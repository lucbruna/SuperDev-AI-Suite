"""
Customer AI Engine - Core orchestration engine.

Coordinates chatbot, voice, omnichannel, sales, support,
personalization, sentiment, loyalty, and automation intelligence.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from .customer_context import CustomerContext
from .customer_events import CustomerEvent, CustomerEventBus, EventType
from .customer_models import (
    Conversation, CustomerProfile, Ticket, LeadScore,
    Recommendation, SentimentResult, LoyaltyTier,
    Campaign,
)
from .customer_config import CustomerConfig
from .customer_metrics import KPICalculator

logger = logging.getLogger(__name__)


class EngineState(Enum):
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class EngineConfig:
    config: CustomerConfig
    event_bus: CustomerEventBus
    context: CustomerContext
    auto_chat_enabled: bool = True
    omnichannel_enabled: bool = True
    sentiment_monitoring_enabled: bool = True
    auto_approval_threshold: float = 5000.0
    decision_interval_seconds: int = 600
    enable_autonomous_mode: bool = False


@dataclass
class EngineMetrics:
    state: EngineState = EngineState.INITIALIZING
    start_time: Optional[datetime] = None
    conversations_handled: int = 0
    tickets_resolved: int = 0
    sales_made: int = 0
    recommendations_given: int = 0
    sentiments_analyzed: int = 0
    campaigns_sent: int = 0
    alerts_generated: int = 0
    errors: int = 0
    last_action_time: Optional[datetime] = None
    subsystem_status: Dict[str, str] = field(default_factory=dict)


class CustomerEngine:
    def __init__(self, config: EngineConfig):
        self.config = config
        self.metrics = EngineMetrics()
        self._subsystems: Dict[str, Any] = {}
        self._running = False
        self._main_task: Optional[asyncio.Task] = None
        self._decision_loop_task: Optional[asyncio.Task] = None

    async def initialize(self) -> None:
        logger.info("Initializing Customer AI Engine...")
        self.metrics.state = EngineState.INITIALIZING
        self.metrics.start_time = datetime.utcnow()
        await self._initialize_subsystems()
        await self._register_event_handlers()
        self.metrics.state = EngineState.RUNNING
        logger.info("Customer AI Engine initialized")

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._decision_loop_task = asyncio.create_task(self._decision_loop())
        logger.info("Customer AI Engine started")

    async def stop(self) -> None:
        logger.info("Stopping Customer AI Engine...")
        self._running = False
        if self._decision_loop_task:
            self._decision_loop_task.cancel()
            try: await self._decision_loop_task
            except asyncio.CancelledError: pass
        await self._shutdown_subsystems()
        self.metrics.state = EngineState.STOPPED
        logger.info("Customer AI Engine stopped")

    async def pause(self) -> None:
        self._running = False
        self.metrics.state = EngineState.PAUSED

    async def resume(self) -> None:
        if not self._running:
            self._running = True
            self._decision_loop_task = asyncio.create_task(self._decision_loop())
            self.metrics.state = EngineState.RUNNING

    async def _initialize_subsystems(self) -> None:
        from .chatbot.chatbot_engine import ChatbotEngine
        from .voice.voice_customer_engine import VoiceCustomerEngine
        from .omnichannel.omnichannel_engine import OmnichannelEngine
        from .sales.sales_ai_engine import SalesAIEngine
        from .support.support_engine import SupportEngine
        from .personalization.personalization_engine import PersonalizationEngine
        from .sentiment.sentiment_engine import SentimentEngine
        from .loyalty.loyalty_engine import LoyaltyEngine
        from .automation.customer_automation import CustomerAutomation

        self._subsystems = {
            "chatbot": ChatbotEngine(self.config.config, self.config.context, self.config.event_bus),
            "voice": VoiceCustomerEngine(self.config.config, self.config.context, self.config.event_bus),
            "omnichannel": OmnichannelEngine(self.config.config, self.config.context, self.config.event_bus),
            "sales": SalesAIEngine(self.config.config, self.config.context, self.config.event_bus),
            "support": SupportEngine(self.config.config, self.config.context, self.config.event_bus),
            "personalization": PersonalizationEngine(self.config.config, self.config.context, self.config.event_bus),
            "sentiment": SentimentEngine(self.config.config, self.config.context, self.config.event_bus),
            "loyalty": LoyaltyEngine(self.config.config, self.config.context, self.config.event_bus),
            "automation": CustomerAutomation(self.config.config, self.config.context, self.config.event_bus),
        }
        for name, sub in self._subsystems.items():
            await sub.initialize()
            self.metrics.subsystem_status[name] = "initialized"

    async def _register_event_handlers(self) -> None:
        self.config.event_bus.subscribe(EventType.CUSTOMER_ANGRY, self._handle_customer_angry)
        self.config.event_bus.subscribe(EventType.TICKET_ESCALATED, self._handle_ticket_escalated)
        self.config.event_bus.subscribe(EventType.SALES_OPPORTUNITY, self._handle_sales_opportunity)
        self.config.event_bus.subscribe(EventType.LOYALTY_RISK, self._handle_loyalty_risk)

    async def _decision_loop(self) -> None:
        while self._running:
            try:
                if self.config.enable_autonomous_mode:
                    await self._make_autonomous_decisions()
                await asyncio.sleep(self.config.decision_interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Decision loop error: {e}")
                self.metrics.errors += 1
                await asyncio.sleep(60)

    async def _make_autonomous_decisions(self) -> None:
        sentiment = await self._subsystems["sentiment"].get_overall_sentiment()
        if sentiment < 50:
            await self._subsystems["automation"].trigger_retention_campaign()

    async def _handle_customer_angry(self, event: CustomerEvent) -> None:
        self.metrics.alerts_generated += 1
        await self._subsystems["support"].escalate(event.payload)

    async def _handle_ticket_escalated(self, event: CustomerEvent) -> None:
        self.metrics.alerts_generated += 1
        await self._subsystems["support"].handle_escalation(event.payload)

    async def _handle_sales_opportunity(self, event: CustomerEvent) -> None:
        self.metrics.alerts_generated += 1
        await self._subsystems["sales"].handle_opportunity(event.payload)

    async def _handle_loyalty_risk(self, event: CustomerEvent) -> None:
        self.metrics.alerts_generated += 1
        await self._subsystems["loyalty"].handle_risk(event.payload)

    async def _shutdown_subsystems(self) -> None:
        for name, sub in self._subsystems.items():
            try:
                await sub.shutdown()
                self.metrics.subsystem_status[name] = "stopped"
            except Exception as e:
                logger.error(f"Error shutting down {name}: {e}")

    async def send_message(self, channel: str, customer_id: str, message: str) -> Conversation:
        self.metrics.conversations_handled += 1
        return await self._subsystems["chatbot"].process(customer_id, message)

    async def get_customer_profile(self, customer_id: str) -> CustomerProfile:
        return await self._subsystems["personalization"].get_profile(customer_id)

    async def get_ticket(self, ticket_id: str) -> Ticket:
        return await self._subsystems["support"].get_ticket(ticket_id)

    async def get_recommendations(self, customer_id: str) -> List[Recommendation]:
        self.metrics.recommendations_given += 1
        return await self._subsystems["sales"].recommend(customer_id)

    async def analyze_sentiment(self, text: str) -> SentimentResult:
        self.metrics.sentiments_analyzed += 1
        return await self._subsystems["sentiment"].analyze(text)

    async def get_loyalty_status(self, customer_id: str) -> LoyaltyTier:
        return await self._subsystems["loyalty"].get_status(customer_id)

    async def run_campaign(self, campaign: Campaign) -> Campaign:
        self.metrics.campaigns_sent += 1
        return await self._subsystems["automation"].run_campaign(campaign)

    async def get_kpis(self) -> Dict[str, float]:
        calc = KPICalculator(self.config.context)
        return await calc.calculate_all()

    def get_metrics(self) -> EngineMetrics:
        return self.metrics

    def get_subsystem(self, name: str):
        return self._subsystems.get(name)
