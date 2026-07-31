"""Data Platform Registry — Registry for data platform components."""
from typing import Dict, Any, List, Optional


class DataPlatformRegistry:
    def __init__(self):
        self._sources: Dict[str, Any] = {}
        self._schemas: Dict[str, Any] = {}
        self._pipelines: Dict[str, Any] = {}
        self._catalog: Dict[str, Any] = {}

    def register_source(self, source_id: str, metadata: Dict[str, Any]) -> None:
        self._sources[source_id] = metadata

    def get_source(self, source_id: str) -> Optional[Dict[str, Any]]:
        return self._sources.get(source_id)

    def register_schema(self, schema_id: str, metadata: Dict[str, Any]) -> None:
        self._schemas[schema_id] = metadata

    def get_schema(self, schema_id: str) -> Optional[Dict[str, Any]]:
        return self._schemas.get(schema_id)

    def register_pipeline(self, pipeline_id: str, metadata: Dict[str, Any]) -> None:
        self._pipelines[pipeline_id] = metadata

    def get_pipeline(self, pipeline_id: str) -> Optional[Dict[str, Any]]:
        return self._pipelines.get(pipeline_id)

    def register_catalog(self, entry_id: str, metadata: Dict[str, Any]) -> None:
        self._catalog[entry_id] = metadata

    def get_catalog(self, entry_id: str) -> Optional[Dict[str, Any]]:
        return self._catalog.get(entry_id)

    def list_sources(self) -> List[str]:
        return list(self._sources.keys())

    def list_schemas(self) -> List[str]:
        return list(self._schemas.keys())

    def list_pipelines(self) -> List[str]:
        return list(self._pipelines.keys())

    def list_catalog(self) -> List[str]:
        return list(self._catalog.keys())

    def get_stats(self) -> Dict[str, int]:
        return {
            "sources": len(self._sources),
            "schemas": len(self._schemas),
            "pipelines": len(self._pipelines),
            "catalog": len(self._catalog),
        }
