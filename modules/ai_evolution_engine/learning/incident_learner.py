"""Incident learner: stores resolved incident history for reuse."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class IncidentRecord:
    """A recorded incident with its resolution signature."""

    incident_id: str
    category: str
    symptom: str
    resolution: str
    occurrence_count: int = 1

    def to_dict(self) -> dict[str, object]:
        return {
            "incident_id": self.incident_id,
            "category": self.category,
            "symptom": self.symptom,
            "resolution": self.resolution,
            "occurrence_count": self.occurrence_count,
        }


class IncidentLearner:
    """Keeps deterministic incident records (no clock/network)."""

    def __init__(self, max_records: int = 200) -> None:
        self._records: dict[str, IncidentRecord] = {}
        self._max = max_records

    def record(self, record: IncidentRecord) -> None:
        existing = self._records.get(record.incident_id)
        if existing is not None:
            existing.occurrence_count += 1
            return
        if len(self._records) >= self._max:
            oldest = min(self._records, key=lambda k: self._records[k].occurrence_count)
            del self._records[oldest]
        self._records[record.incident_id] = record

    def resolve(self, symptom: str) -> IncidentRecord | None:
        for record in self._records.values():
            if record.symptom == symptom:
                return record
        return None

    def all(self) -> list[IncidentRecord]:
        return list(self._records.values())
