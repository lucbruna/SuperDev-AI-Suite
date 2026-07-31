"""Sentiment engine."""

import uuid
from datetime import datetime

from .models import SatisfactionScore, SentimentResult, SentimentType

POSITIVE_WORDS = {
    "great",
    "excellent",
    "good",
    "love",
    "amazing",
    "wonderful",
    "fantastic",
    "best",
    "happy",
    "perfect",
    "awesome",
    "brilliant",
    "outstanding",
}
NEGATIVE_WORDS = {
    "bad",
    "terrible",
    "hate",
    "awful",
    "worst",
    "poor",
    "horrible",
    "disappointing",
    "angry",
    "sad",
    "frustrated",
    "annoyed",
    "broken",
}


class SentimentEngine:
    def __init__(self):
        self._results: list[SentimentResult] = []
        self._customer_sentiments: dict[str, list[SentimentResult]] = {}
        self._satisfaction: dict[str, SatisfactionScore] = {}

    def analyze(self, text: str, customer_id: str = "") -> SentimentResult:
        words = set(text.lower().split())
        pos_count = len(words & POSITIVE_WORDS)
        neg_count = len(words & NEGATIVE_WORDS)
        total = pos_count + neg_count
        if total == 0:
            sentiment = SentimentType.NEUTRAL
            score = 0.0
        elif pos_count > neg_count:
            sentiment = SentimentType.POSITIVE
            score = pos_count / total
        elif neg_count > pos_count:
            sentiment = SentimentType.NEGATIVE
            score = -neg_count / total
        else:
            sentiment = SentimentType.MIXED
            score = 0.0
        emotions = {}
        if pos_count > 0:
            emotions["happy"] = pos_count / max(total, 1)
        if neg_count > 0:
            emotions["angry"] = neg_count / max(total, 1)
        if not emotions:
            emotions["neutral"] = 1.0
        keywords = list(words & (POSITIVE_WORDS | NEGATIVE_WORDS))
        result = SentimentResult(
            result_id=str(uuid.uuid4())[:8],
            text=text,
            sentiment=sentiment,
            score=score,
            confidence=min(1.0, total * 0.2 + 0.3),
            emotions=emotions,
            keywords=keywords,
        )
        self._results.append(result)
        if customer_id:
            self._customer_sentiments.setdefault(customer_id, []).append(result)
        return result

    def get_customer_sentiment(self, customer_id: str) -> dict[str, Any]:
        results = self._customer_sentiments.get(customer_id, [])
        if not results:
            return {"sentiment": "unknown", "score": 0.0, "count": 0}
        scores = [r.score for r in results]
        avg = sum(scores) / len(scores)
        if avg > 0.2:
            sentiment = "positive"
        elif avg < -0.2:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        return {"sentiment": sentiment, "score": avg, "count": len(results)}

    def update_satisfaction(self, customer_id: str, score: float) -> SatisfactionScore:
        existing = self._satisfaction.get(customer_id)
        if existing:
            existing.sample_size += 1
            existing.score = (existing.score * (existing.sample_size - 1) + score) / existing.sample_size
            existing.last_updated = datetime.now()
            return existing
        sat = SatisfactionScore(customer_id=customer_id, score=score, sample_size=1)
        self._satisfaction[customer_id] = sat
        return sat

    def get_satisfaction(self, customer_id: str) -> SatisfactionScore | None:
        return self._satisfaction.get(customer_id)

    def get_results(self, limit: int = 100) -> list[SentimentResult]:
        return self._results[-limit:]

    def get_stats(self) -> dict:
        return {"total_analyses": len(self._results), "customers_analyzed": len(self._customer_sentiments)}
