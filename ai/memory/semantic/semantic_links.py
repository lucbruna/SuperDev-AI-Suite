from __future__ import annotations

from typing import Any


class SemanticLink:
    """A typed link between two semantic entities or concepts."""

    def __init__(
        self,
        source_id: str,
        target_id: str,
        link_type: str,
        weight: float = 1.0,
        metadata: dict[str, Any] | None = None,
    ):
        self._source_id = source_id
        self._target_id = target_id
        self._type = link_type
        self._weight = weight
        self._metadata = metadata or {}

    @property
    def source_id(self) -> str:
        return self._source_id

    @property
    def target_id(self) -> str:
        return self._target_id

    @property
    def link_type(self) -> str:
        return self._type

    @property
    def weight(self) -> float:
        return self._weight

    @property
    def metadata(self) -> dict[str, Any]:
        return dict(self._metadata)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self._source_id,
            "target": self._target_id,
            "type": self._type,
            "weight": self._weight,
            "metadata": dict(self._metadata),
        }
