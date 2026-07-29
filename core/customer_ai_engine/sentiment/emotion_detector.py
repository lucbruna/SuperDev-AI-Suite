"""
Emotion Detector - Detect emotions from text using keyword analysis.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional

from ..customer_context import CustomerContext
from ..customer_events import CustomerEventBus
from ..customer_models import SentimentResult, SentimentType
from ..customer_config import CustomerConfig

logger = logging.getLogger(__name__)


class EmotionDetector:
    def __init__(self, config: CustomerConfig, context: CustomerContext, event_bus: CustomerEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self._positive_words = [
            "obrigado", "ótimo", "excelente", "maravilhoso", "perfeito", "adorei", "amei",
            "satisfeito", "feliz", "bom", "ótima", "rapidez", "eficiente", "parabéns",
        ]
        self._negative_words = [
            "péssimo", "horrível", "decepcionado", "frustrado", "raiva", "insatisfeito",
            "lento", "demorado", "problema", "erro", "ruim", "pior", "odeio", "detestei",
        ]
        self._angry_words = [
            "reclamação", "processo", "advogado", "procon", "justiça", "indenização",
            "absurdo", "vergonha", "inaceitável", "revoltado",
        ]

    def detect(self, text: str) -> SentimentResult:
        text_lower = text.lower()
        angry_score = self._score_words(text_lower, self._angry_words, 3.0)
        negative_score = self._score_words(text_lower, self._negative_words, 2.0)
        positive_score = self._score_words(text_lower, self._positive_words, 1.5)
        total = angry_score + negative_score + positive_score or 1
        if angry_score > 0:
            sentiment = SentimentType.ANGRY
            normalized = 1.0 - (angry_score / total)
        elif negative_score > positive_score:
            sentiment = SentimentType.NEGATIVE
            normalized = 1.0 - (negative_score / total)
        elif positive_score > negative_score:
            sentiment = SentimentType.POSITIVE
            normalized = positive_score / total
        else:
            sentiment = SentimentType.NEUTRAL
            normalized = 0.5
        return SentimentResult(
            text=text,
            sentiment=sentiment,
            score=round(normalized * 100, 1),
            confidence=round(max(angry_score, negative_score, positive_score) / max(total, 1), 2),
            emotions={
                "positive": round(positive_score / total * 100, 1),
                "negative": round(negative_score / total * 100, 1),
                "angry": round(angry_score / total * 100, 1),
            },
        )

    def _score_words(self, text: str, words: List[str], weight: float) -> float:
        score = 0
        for word in words:
            if word in text:
                score += weight
        return score
