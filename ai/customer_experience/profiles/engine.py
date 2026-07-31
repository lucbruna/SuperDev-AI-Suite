"""Profile engine."""

from .models import (
    BehaviorEvent,
    BehaviorPattern,
    CustomerPreference,
    CustomerSegment,
    ProfileInsight,
)


class ProfileEngine:
    def __init__(self):
        self._segments: dict[str, CustomerSegment] = {}
        self._events: dict[str, list[BehaviorEvent]] = {}
        self._preferences: dict[str, dict[str, CustomerPreference]] = {}
        self._insights: dict[str, list[ProfileInsight]] = {}

    def create_segment(self, segment: CustomerSegment) -> CustomerSegment:
        self._segments[segment.segment_id] = segment
        return segment

    def get_segment(self, segment_id: str) -> CustomerSegment | None:
        return self._segments.get(segment_id)

    def list_segments(self) -> list[CustomerSegment]:
        return list(self._segments.values())

    def add_behavior_event(self, event: BehaviorEvent) -> BehaviorEvent:
        self._events.setdefault(event.customer_id, []).append(event)
        return event

    def get_customer_events(self, customer_id: str) -> list[BehaviorEvent]:
        return self._events.get(customer_id, [])

    def set_preference(self, pref: CustomerPreference) -> CustomerPreference:
        self._preferences.setdefault(pref.customer_id, {})[pref.preference_key] = pref
        return pref

    def get_preference(self, customer_id: str, key: str) -> CustomerPreference | None:
        return self._preferences.get(customer_id, {}).get(key)

    def get_customer_preferences(self, customer_id: str) -> dict[str, CustomerPreference]:
        return self._preferences.get(customer_id, {})

    def add_insight(self, insight: ProfileInsight) -> ProfileInsight:
        self._insights.setdefault(insight.customer_id, []).append(insight)
        return insight

    def get_customer_insights(self, customer_id: str) -> list[ProfileInsight]:
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
