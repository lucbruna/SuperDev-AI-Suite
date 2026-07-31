"""NoSQL (MongoDB) datasource ingestion."""

from __future__ import annotations

from typing import Any, Iterable

from data_intelligence.data_models import SourceType
from data_intelligence.ingestion.base import BaseSource


class MongoSource(BaseSource):
    """Fetches documents from a MongoDB collection.

    The ``collection`` must expose a ``find`` method returning an iterable
    of dicts (as pymongo collections do). The default ``find`` uses a
    filter and limit from the constructor.
    """

    source_type = SourceType.MONGODB

    def __init__(self, source_id: str, name: str, collection: Any,
                 filter_query: dict[str, Any] | None = None,
                 limit: int | None = None, **config: Any) -> None:
        super().__init__(source_id, name, collection=collection,
                         filter_query=filter_query, limit=limit, **config)
        self._collection = collection
        self._filter = filter_query or {}
        self._limit = limit

    def fetch(self, source: Any = None) -> Iterable[dict[str, Any]]:  # noqa: ARG002
        if self._collection is None:
            raise RuntimeError("MongoSource requires a collection")
        docs = self._collection.find(self._filter)
        if self._limit is not None:
            docs = docs.limit(self._limit)
        return [dict(doc) for doc in docs]
