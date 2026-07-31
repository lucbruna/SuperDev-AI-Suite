from __future__ import annotations

from typing import Any

from .archive import Archive
from .compression import Compression
from .consolidation import Consolidation
from .indexing import Indexing
from .optimizer import Optimizer
from .persistence import Persistence
from .retrieval import Retrieval
from .storage import Storage
from .synchronization import Synchronization
from .validator import Validator


class LongTermMemory:
    """High-level facade for long-term memory operations."""

    def __init__(
        self,
        storage: Storage | None = None,
        persistence: Persistence | None = None,
        consolidation: Consolidation | None = None,
        retrieval: Retrieval | None = None,
        archive: Archive | None = None,
        indexing: Indexing | None = None,
        compression: Compression | None = None,
        optimizer: Optimizer | None = None,
        validator: Validator | None = None,
        synchronization: Synchronization | None = None,
    ):
        self._storage = storage or Storage()
        self._persistence = persistence or Persistence(self._storage)
        self._consolidation = consolidation or Consolidation()
        self._retrieval = retrieval or Retrieval(self._storage)
        self._archive = archive or Archive(self._storage)
        self._indexing = indexing or Indexing()
        self._compression = compression or Compression()
        self._optimizer = optimizer or Optimizer()
        self._validator = validator or Validator()
        self._synchronization = synchronization or Synchronization()

    @property
    def storage(self) -> Storage:
        return self._storage

    @property
    def persistence(self) -> Persistence:
        return self._persistence

    @property
    def consolidation(self) -> Consolidation:
        return self._consolidation

    @property
    def retrieval(self) -> Retrieval:
        return self._retrieval

    @property
    def archive(self) -> Archive:
        return self._archive

    @property
    def indexing(self) -> Indexing:
        return self._indexing

    @property
    def compression(self) -> Compression:
        return self._compression

    @property
    def optimizer(self) -> Optimizer:
        return self._optimizer

    @property
    def validator(self) -> Validator:
        return self._validator

    @property
    def synchronization(self) -> Synchronization:
        return self._synchronization

    def store(self, key: str, data: dict[str, Any]) -> None:
        if not self._validator.validate(data):
            return
        compressed = self._compression.compress(data)
        self._storage.put(key, compressed)
        self._indexing.add(key, data)
        self._persistence.persist(key, compressed)

    def retrieve(self, key: str) -> dict[str, Any] | None:
        data = self._storage.get(key)
        if data is None:
            data = self._persistence.load(key)
            if data:
                self._storage.put(key, data)
        if data is None:
            return None
        return self._compression.decompress(data)

    def delete(self, key: str) -> bool:
        self._indexing.remove(key)
        return self._storage.delete(key)

    def search(self, query: str) -> list[dict[str, Any]]:
        keys = self._indexing.search(query)
        results: list[dict[str, Any]] = []
        for key in keys[:50]:
            data = self.retrieve(key)
            if data:
                results.append({"key": key, "data": data})
        return results

    def consolidate(self, source: Any) -> int:
        return self._consolidation.run(source, self)

    def optimize(self) -> dict[str, Any]:
        return self._optimizer.run(self._storage, self._indexing)

    def snapshot(self) -> dict[str, Any]:
        return {
            "storage_size": self._storage.count,
            "index_size": self._indexing.count,
            "archive_size": self._archive.count,
        }
