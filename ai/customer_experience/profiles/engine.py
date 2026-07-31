"""Profile engine."""
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from .models import (
    CustomerSegment, BehaviorEvent, CustomerPreference, ProfileInsight,
    SegmentType, BehaviorPattern,
)


class ProfileEngine:
    def __init__(self):
        self._segments: Dict[str, CustomerSegment] = {}
        self._events: Dict[str, List[BehaviorEvent]] = {}
        self._preferences: Dict[str, Dict[str, CustomerPreference]] = {}
        self._insights: Dict[str, List[ProfileInsight]] = {}

    def create_segment(self, segment: CustomerSegment) -> CustomerSegment:
        self._segments[segment.segment_id] = segment
        return segment

    def get_segment(self, segment_id: str) -> Optional[CustomerSegment]:
        return self._segments.get(segment_id)

    def list_segments(self) -> List[CustomerSegment]:
        return list(self._segments.values())

    def add_behavior_event(self, event: BehaviorEvent) -> BehaviorEvent:
        self._events.setdefault(event.customer_id, []).append(event)
        return event

    def get_customer_events(self, customer_id: str) -> List[BehaviorEvent]:
        return self._events.get(customer_id, [])

    def set_preference(self, pref: CustomerPreference) -> CustomerPreference:
        self._preferences.setdefault(pref.customer_id, {})[pref.preference_key] = pref
        return pref

    def get_preference(self, customer_id: str, key: str) -> Optional[CustomerPreference]:
        return self._preferences.get(customer_id, {}).get(key)

    def get_customer_preferences(self, customer_id: str) -> Dict[str, CustomerPreference]:
        return self._preferences.get(customer_id, {})

    def add_insight(self, insight: ProfileInsight) -> ProfileInsight:
        self._insights.setdefault(insight.customer_id, []).append(insight)
        return insight

    def get_customer_insights(self, customer_id: str) -> List[ProfileInsight]:
        return self._insights.get(customer_id, [])

    def analyze_behavior(self, customer_id: str) -> str:
        events = self.get_customer_events(customer_id)
        if len(events) > 20:
            return BehaviorPattern.FREQUENT_BUYER.value
        elif len(events) > 5:
            return BehaviorPattern.WINDOW_SHOPPER.value
        elif len(events) > 0:
            return BehaviorPattern.SEASONAL.value
        return BehaviorPattern.DORMANT.value
