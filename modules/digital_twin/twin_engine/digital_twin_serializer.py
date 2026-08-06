"""Serialization helpers for twin models and snapshots."""
from __future__ import annotations

import json

from modules.digital_twin.twin_engine.digital_twin_builder import TwinModel
from modules.digital_twin.twin_engine.digital_twin_snapshot import (
    TwinSnapshot,
    TwinSnapshotter,
)


class TwinSerializer:
    """Dict/JSON round-trips for TwinModel and TwinSnapshot."""

    @staticmethod
    def model_to_dict(model: TwinModel) -> dict[str, object]:
        return model.to_dict()

    @staticmethod
    def model_from_dict(data: dict[str, object]) -> TwinModel:
        model = TwinModel(name=str(data.get("name", "default")))
        entities = data.get("entities", {})
        if isinstance(entities, dict):
            for key, value in entities.items():
                if isinstance(value, dict):
                    model.add_entity(dict(value))
        relationships = data.get("relationships", [])
        if isinstance(relationships, list):
            for rel in relationships:
                if isinstance(rel, dict) and {"source", "target", "kind"} <= set(rel):
                    model.add_relationship(
                        str(rel["source"]), str(rel["target"]), str(rel["kind"])
                    )
        meta = data.get("meta")
        if isinstance(meta, dict):
            model.meta = dict(meta)
        return model

    @staticmethod
    def to_json(model: TwinModel, *, indent: int = 2) -> str:
        return json.dumps(model.to_dict(), ensure_ascii=False, indent=indent)

    @staticmethod
    def from_json(text: str) -> TwinModel:
        data = json.loads(text)
        if not isinstance(data, dict):
            raise ValueError("twin json must be an object")
        return TwinSerializer.model_from_dict(data)

    @staticmethod
    def snapshot_to_dict(snapshot: TwinSnapshot) -> dict[str, object]:
        return snapshot.to_dict()

    @staticmethod
    def snapshot_from_dict(data: dict[str, object], snapshotter: TwinSnapshotter) -> TwinSnapshot:
        model = TwinSerializer.model_from_dict(data)
        return snapshotter.capture(model)
