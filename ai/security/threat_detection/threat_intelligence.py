"""Threat intelligence."""

from __future__ import annotations

import time
import uuid
from enum import Enum
from typing import Any


class IntelSource(Enum):
    INTERNAL = "internal"
    OSINT = "osint"
    COMMERCIAL = "commercial"
    GOVERNMENT = "government"
    COMMUNITY = "community"


class ThreatIndicator:
    def __init__(
        self, indicator_type: str, value: str, confidence: float = 0.5, source: IntelSource = IntelSource.INTERNAL
    ) -> None:
        self.indicator_id = str(uuid.uuid4())[:8]
        self.type = indicator_type
        self.value = value
        self.confidence = confidence
        self.source = source
        self.created_at = time.time()
        self.ttl = 86400 * 30  # 30 days


class ThreatIntelligence:
    def __init__(self) -> None:
        self._indicators: dict[str, ThreatIndicator] = {}
        self._feeds: dict[str, dict[str, Any]] = {}
        self._correlations: dict[str, list[str]] = {}

    def add_indicator(
        self, indicator_type: str, value: str, confidence: float = 0.5, source: IntelSource = IntelSource.INTERNAL
    ) -> ThreatIndicator:
        indicator = ThreatIndicator(indicator_type, value, confidence, source)
        self._indicators[indicator.indicator_id] = indicator
        return indicator

    def lookup(self, indicator_type: str, value: str) -> ThreatIndicator | None:
        for ind in self._indicators.values():
            if ind.type == indicator_type and ind.value == value and ind.created_at + ind.ttl > time.time():
                return ind
        return None

    def add_feed(self, feed_id: str, name: str, url: str = "") -> None:
        self._feeds[feed_id] = {"name": name, "url": url, "last_updated": time.time(), "indicator_count": 0}

    def update_feed(self, feed_id: str, count: int) -> None:
        if feed_id in self._feeds:
            self._feeds[feed_id]["last_updated"] = time.time()
            self._feeds[feed_id]["indicator_count"] = count

    def correlate(self, indicator_id: str, related_ids: list[str]) -> None:
        self._correlations[indicator_id] = related_ids

    def get_related(self, indicator_id: str) -> list[str]:
        return self._correlations.get(indicator_id, [])

    def list_indicators(self, indicator_type: str = "", min_confidence: float = 0.0) -> list[dict[str, Any]]:
        results = []
        for ind in self._indicators.values():
            if ind.type == indicator_type or not indicator_type:
                if ind.confidence >= min_confidence:
                    results.append(
                        {
                            "id": ind.indicator_id,
                            "type": ind.type,
                            "value": ind.value,
                            "confidence": ind.confidence,
                            "source": ind.source.value,
                        }
                    )
        return results

    def cleanup_expired(self) -> int:
        now = time.time()
        expired = [k for k, v in self._indicators.items() if v.created_at + v.ttl < now]
        for k in expired:
            del self._indicators[k]
        return len(expired)

    def list_feeds(self) -> dict[str, dict[str, Any]]:
        return dict(self._feeds)
