"""Sentiment models."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum


class SentimentType(Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    MIXED = "mixed"


class EmotionType(Enum):
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    SURPRISED = "surprised"
    FEARFUL = "fearful"
    DISGUSTED = "disgusted"
    NEUTRAL = "neutral"


@dataclass
class SentimentResult:
    result_id: str
    text: str = ""
    sentiment: SentimentType = SentimentType.NEUTRAL
    score: float = 0.0
    confidence: float = 0.0
    emotions: Dict[str, float] = field(default_factory=dict)
    keywords: List[str] = field(default_factory=list)
    analyzed_at: datetime = field(default_factory=datetime.now)


@dataclass
class EmotionAnalysis:
    analysis_id: str
    text: str = ""
    primary_emotion: EmotionType = EmotionType.NEUTRAL
    emotion_scores: Dict[str, float] = field(default_factory=dict)
    intensity: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class SatisfactionScore:
    customer_id: str = ""
    score: float = 0.0
    sample_size: int = 0
    factors: List[str] = field(default_factory=list)
    trend: str = "stable"
    last_updated: datetime = field(default_factory=datetime.now)
