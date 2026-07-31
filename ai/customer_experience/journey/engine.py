"""Journey engine."""

import uuid
from datetime import datetime

from .models import (
    CustomerJourney,
    JourneyOptimization,
    JourneyStage,
    LifecycleStage,
    Touchpoint,
    TouchpointType,
)


class JourneyEngine:
    def __init__(self):
        self._journeys: dict[str, CustomerJourney] = {}
        self._customer_journeys: dict[str, str] = {}

    def start_journey(self, customer_id: str) -> CustomerJourney:
        journey_id = str(uuid.uuid4())[:8]
        journey = CustomerJourney(
            journey_id=journey_id,
            customer_id=customer_id,
            current_stage=JourneyStage.AWARENESS,
            stages=[LifecycleStage(stage=JourneyStage.AWARENESS)],
        )
        self._journeys[journey_id] = journey
        self._customer_journeys[customer_id] = journey_id
        return journey

    def get_journey(self, customer_id: str) -> CustomerJourney | None:
        jid = self._customer_journeys.get(customer_id)
        if jid:
            return self._journeys.get(jid)
        return None

    def get_journey_by_id(self, journey_id: str) -> CustomerJourney | None:
        return self._journeys.get(journey_id)

    def advance_stage(self, customer_id: str, new_stage: JourneyStage) -> bool:
        journey = self.get_journey(customer_id)
        if not journey:
            return False
        now = datetime.now()
        if journey.stages:
            current = journey.stages[-1]
            current.exited_at = now
            current.duration_days = (now - current.entered_at).total_seconds() / 86400
        journey.current_stage = new_stage
        journey.stages.append(LifecycleStage(stage=new_stage))
        journey.last_activity = now
        return True

    def add_touchpoint(self, customer_id: str, touchpoint: Touchpoint) -> bool:
        journey = self.get_journey(customer_id)
        if not journey:
            return False
        touchpoint.customer_id = customer_id
        journey.touchpoints.append(touchpoint)
        journey.last_activity = datetime.now()
        return True

    def get_touchpoints(self, customer_id: str, touchpoint_type: TouchpointType | None = None) -> list[Touchpoint]:
        journey = self.get_journey(customer_id)
        if not journey:
            return []
        if touchpoint_type:
            return [t for t in journey.touchpoints if t.touchpoint_type == touchpoint_type]
        return journey.touchpoints

    def calculate_conversion_score(self, customer_id: str) -> float:
        journey = self.get_journey(customer_id)
        if not journey:
            return 0.0
        stages_completed = len([s for s in journey.stages if s.exited_at is not None])
        total_stages = len(JourneyStage)
        touchpoint_score = min(1.0, len(journey.touchpoints) / 10)
        stage_score = stages_completed / total_stages
        score = stage_score * 0.6 + touchpoint_score * 0.4
        journey.conversion_score = score
        return score

    def get_journeys(self) -> list[CustomerJourney]:
        return list(self._journeys.values())

    def get_stats(self) -> dict:
        journeys = list(self._journeys.values())
        avg_score = sum(j.conversion_score for j in journeys) / len(journeys) if journeys else 0.0
        return {
            "total_journeys": len(journeys),
            "avg_conversion_score": avg_score,
        }

    def optimize(self, customer_id: str) -> list[JourneyOptimization]:
        journey = self.get_journey(customer_id)
        if not journey:
            return []
        opts = []
        if journey.current_stage == JourneyStage.AWARENESS:
            opts.append(
                JourneyOptimization(
                    optimization_id=str(uuid.uuid4())[:8],
                    stage=JourneyStage.AWARENESS,
                    suggestion="Increase touchpoint frequency to advance to Interest stage",
                    expected_impact=0.15,
                    priority="high",
                )
            )
        if len(journey.touchpoints) < 3:
            opts.append(
                JourneyOptimization(
                    optimization_id=str(uuid.uuid4())[:8],
                    stage=journey.current_stage,
                    suggestion="Add more engagement touchpoints",
                    expected_impact=0.1,
                    priority="medium",
                )
            )
        return opts
