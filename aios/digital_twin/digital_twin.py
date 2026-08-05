"""DigitalTwin: facade that mirrors, simulates, and predicts entity state."""
from __future__ import annotations

from typing import Any, Optional

from aios.digital_twin.entity import TwinEntity
from aios.digital_twin.prediction import Prediction, Predictor, Snapshot
from aios.digital_twin.simulator import Simulator, TransitionFn
from aios.digital_twin.state_mirror import StateMirror


class DigitalTwin:
    """Composes entity store, state mirror, simulator, and predictor."""

    def __init__(
        self,
        mirror: StateMirror | None = None,
        simulator: Simulator | None = None,
        predictor: Predictor | None = None,
    ) -> None:
        self.mirror = mirror if mirror is not None else StateMirror()
        self.simulator = simulator if simulator is not None else Simulator()
        self.predictor = predictor if predictor is not None else Predictor()
        self._entities: dict[str, TwinEntity] = {}

    def register(self, entity: TwinEntity) -> bool:
        if entity.entity_id in self._entities:
            raise KeyError(f"entity {entity.entity_id!r} already registered")
        self._entities[entity.entity_id] = entity
        return True

    def get(self, entity_id: str) -> Optional[TwinEntity]:
        return self._entities.get(entity_id)

    def entities(self) -> list[str]:
        return sorted(self._entities)

    def sync_tick(self) -> list[Snapshot]:
        """Record a snapshot of every entity's current state."""
        return [self.mirror.record(entity) for entity in self._sorted_entities()]

    def history(self, entity_id: str) -> list[Snapshot]:
        return self.mirror.history(entity_id)

    def diff(self, entity_id: str, from_seq: int, to_seq: int) -> dict[str, tuple[Any, Any]]:
        return self.mirror.diff(entity_id, from_seq, to_seq)

    def simulate(
        self, entity_id: str, transition: TransitionFn, steps: int
    ) -> list[dict[str, Any]]:
        entity = self._require(entity_id)
        return self.simulator.simulate(entity, transition, steps)

    def predict(self, entity_id: str, horizon: int) -> Prediction:
        self._require(entity_id)
        return self.predictor.predict(self.history(entity_id), horizon)

    def snapshot(self) -> dict[str, Any]:
        return {
            "entities": [entity.to_dict() for entity in self._sorted_entities()],
            "mirror": self.mirror.snapshot(),
        }

    def _sorted_entities(self) -> list[TwinEntity]:
        return [self._entities[entity_id] for entity_id in sorted(self._entities)]

    def _require(self, entity_id: str) -> TwinEntity:
        entity = self._entities.get(entity_id)
        if entity is None:
            raise KeyError(f"unknown entity {entity_id!r}")
        return entity
