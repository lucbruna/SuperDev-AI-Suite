"""ERP and CRM datasource ingestion."""

from __future__ import annotations

from typing import Any, Callable, Iterable

from data_intelligence.data_models import SourceType
from data_intelligence.ingestion.base import BaseSource


class ErpSource(BaseSource):
    """Fetches business records from an ERP system.

    ``fetcher(module, since)`` returns the raw records for the module
    (e.g. "sales", "inventory", "orders"). If no fetcher is supplied the
    source returns an empty list (configure a fetcher for real systems).
    """

    source_type = SourceType.ERP

    def __init__(self, source_id: str, name: str, module: str = "sales",
                 fetcher: Callable[..., Iterable[dict[str, Any]]] | None = None,
                 **config: Any) -> None:
        super().__init__(source_id, name, module=module, fetcher=fetcher,
                         **config)
        self.module = module
        self._fetcher = fetcher

    def fetch(self, source: Any = None) -> Iterable[dict[str, Any]]:  # noqa: ARG002
        if self._fetcher is None:
            return []
        return list(self._fetcher(self.module))


class CrmSource(BaseSource):
    """Fetches customer records from a CRM system.

    ``fetcher(entity)`` returns records for the entity (e.g. "contacts",
    "deals", "leads").
    """

    source_type = SourceType.CRM

    def __init__(self, source_id: str, name: str, entity: str = "contacts",
                 fetcher: Callable[..., Iterable[dict[str, Any]]] | None = None,
                 **config: Any) -> None:
        super().__init__(source_id, name, entity=entity, fetcher=fetcher,
                         **config)
        self.entity = entity
        self._fetcher = fetcher

    def fetch(self, source: Any = None) -> Iterable[dict[str, Any]]:  # noqa: ARG002
        if self._fetcher is None:
            return []
        return list(self._fetcher(self.entity))
