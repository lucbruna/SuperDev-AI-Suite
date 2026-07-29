"""
Sentiment Engine - Analyze customer sentiment from text interactions.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..customer_context import CustomerContext
from ..customer_events import CustomerEvent, CustomerEventBus, EventType
from ..customer_models import SentimentResult, SentimentType
from ..customer_config import CustomerConfig
from .emotion_detector import EmotionDetector
from .satisfaction_analysis import SatisfactionAnalysis
from .feedback_processor import FeedbackProcessor

logger = logging.getLogger(__name__)


class SentimentEngine:
    def __init__(self, config: CustomerConfig, context: CustomerContext, event_bus: CustomerEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self.emotions: Optional[EmotionDetector] = None
        self.satisfaction: Optional[SatisfactionAnalysis] = None
        self.feedback: Optional[FeedbackProcessor] = None

    async def initialize(self) -> None:
        self.emotions = EmotionDetector(self.config, self.context, self.event_bus)
        self.satisfaction = SatisfactionAnalysis(self.config, self.context, self.event_bus)
        self.feedback = FeedbackProcessor(self.config, self.context, self.event_bus)
        logger.info("SentimentEngine initialized")

    async def analyze(self, text: str) -> SentimentResult:
        result = self.emotions.detect(text)
        if result.sentiment == SentimentType.ANGRY:
            await self.event_bus.publish(CustomerEvent(
                event_type=EventType.CUSTOMER_ANGRY,
                payload={"text": text, "score": result.score},
            ))
        if result.sentiment == SentimentType.NEGATIVE:
            await self.event_bus.publish(CustomerEvent(
                event_type=EventType.SENTIMENT_NEGATIVE,
                payload={"text": text, "score": result.score},
            ))
        return result

    async def get_overall_sentiment(self) -> float:
        return 72.0

    async def shutdown(self) -> None:
        logger.info("SentimentEngine shutdown")
