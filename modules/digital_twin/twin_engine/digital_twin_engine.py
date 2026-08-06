"""Twin engine: orchestrates mapping + building into a complete twin."""
from __future__ import annotations

from dataclasses import dataclass, field

from modules.digital_twin.core.digital_twin_context import DigitalTwinContext
from modules.digital_twin.twin_engine.digital_twin_builder import TwinModel
from modules.digital_twin.twin_engine.digital_twin_mapper import (
    MappedEntity,
    TwinMapper,
)


@dataclass(slots=True)
class BuildResult:
    """Outcome of building a twin."""

    model: TwinModel
    mapped_count: int

    def to_dict(self) -> dict[str, object]:
        return {
            "twin": self.model.to_dict(),
            "mapped_count": self.mapped_count,
        }


class TwinEngine:
    """Deterministic twin construction from raw reality records."""

    def __init__(self, mapper: TwinMapper | None = None) -> None:
        self._mapper = mapper or TwinMapper()

    def build(
        self,
        ctx: DigitalTwinContext,
        *,
        name: str = "default",
        raw_entities: list[dict[str, object]] | None = None,
        relationships: list[tuple[str, str, str]] | None = None,
    ) -> BuildResult:
        raws = list(raw_entities or [])
        mapped: list[MappedEntity] = self._mapper.map_many(raws)
        model = TwinModel(name=name)
        for entity in mapped:
            model.add_entity(entity.to_dict())
        for source, target, kind in relationships or []:
            model.add_relationship(source, target, kind)
        ctx.set_artifact("twin", model.to_dict())
        ctx.record("twin.entities", len(model))
        ctx.record("twin.relationships", len(model.relationships))
        ctx.publish(
            "twin.built",
            {"name": name, "entities": len(model), "relationships": len(model.relationships)},
        )
        return BuildResult(model=model, mapped_count=len(mapped))

    def run(self, ctx: DigitalTwinContext) -> BuildResult:
        return self.build(ctx)
