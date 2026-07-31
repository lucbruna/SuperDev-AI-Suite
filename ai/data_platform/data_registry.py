"""Data Platform Registry — Registry for data platform components."""
from typing import Any


class DataPlatformRegistry:
    def __init__(self):
        self._sources: dict[str, Any] = {}
        self._schemas: dict[str, Any] = {}
        self._pipelines: dict[str, Any] = {}
        self._catalog: dict[str, Any] = {}

    def register_source(self, source_id: str, metadata: dict[str, Any]) -> None:
        self._sources[source_id] = metadata

    def get_source(self, source_id: str) -> dict[str, Any] | None:
        return self._sources.get(source_id)

    def register_schema(self, schema_id: str, metadata: dict[str, Any]) -> None:
        self._schemas[schema_id] = metadata

    def get_schema(self, schema_id: str) -> dict[str, Any] | None:
        return self._schemas.get(schema_id)

    def register_pipeline(self, pipeline_id: str, metadata: dict[str, Any]) -> None:
        self._pipelines[pipeline_id] = metadata

    def get_pipeline(self, pipeline_id: str) -> dict[str, Any] | None:
        return self._pipelines.get(pipeline_id)

    def register_catalog(self, entry_id: str, metadata: dict[str, Any]) -> None:
        self._catalog[entry_id] = metadata

    def get_catalog(self, entry_id: str) -> dict[str, Any] | None:
        return self._catalog.get(entry_id)

    def list_sources(self) -> list[str]:
        return list(self._sources.keys())

    def list_schemas(self) -> list[str]:
        return list(self._schemas.keys())

    def list_pipelines(self) -> list[str]:
        return list(self._pipelines.keys())

    def list_catalog(self) -> list[str]:
        return list(self._catalog.keys())

    def get_stats(self) -> dict[str, int]:
        return {
            "sources": len(self._sources),
            "schemas": len(self._schemas),
            "pipelines": len(self._pipelines),
            "catalog": len(self._catalog),
        }
