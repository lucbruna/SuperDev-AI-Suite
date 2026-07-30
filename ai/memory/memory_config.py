from __future__ import annotations

from typing import Any, Dict, Optional

from .memory_types import ConsolidationStrategy, RetentionPolicy, MemoryScope


class MemoryConfig:
    """Configuration settings for the memory subsystem."""

    def __init__(
        self,
        max_entries: int = 100000,
        max_size_bytes: int = 1073741824,
        default_ttl: float = 3600.0,
        retention_policy: RetentionPolicy = RetentionPolicy.LRU,
        consolidation_strategy: ConsolidationStrategy = ConsolidationStrategy.MERGE,
        consolidation_interval: float = 300.0,
        backup_interval: float = 86400.0,
        checkpoint_interval: float = 600.0,
        cache_ttl: float = 60.0,
        cache_max_size: int = 10000,
        enable_encryption: bool = False,
        enable_compression: bool = True,
        enable_metrics: bool = True,
        enable_logging: bool = True,
        enable_audit: bool = False,
        default_scope: MemoryScope = MemoryScope.LOCAL,
        auto_consolidate: bool = True,
        auto_evict: bool = True,
        eviction_batch_size: int = 100,
        max_context_length: int = 100,
        embedding_dimension: int = 768,
        storage_backend: str = "memory",
        serializer: str = "json",
        **kwargs: Any,
    ):
        self._max_entries = max_entries
        self._max_size_bytes = max_size_bytes
        self._default_ttl = default_ttl
        self._retention_policy = retention_policy
        self._consolidation_strategy = consolidation_strategy
        self._consolidation_interval = consolidation_interval
        self._backup_interval = backup_interval
        self._checkpoint_interval = checkpoint_interval
        self._cache_ttl = cache_ttl
        self._cache_max_size = cache_max_size
        self._enable_encryption = enable_encryption
        self._enable_compression = enable_compression
        self._enable_metrics = enable_metrics
        self._enable_logging = enable_logging
        self._enable_audit = enable_audit
        self._default_scope = default_scope
        self._auto_consolidate = auto_consolidate
        self._auto_evict = auto_evict
        self._eviction_batch_size = eviction_batch_size
        self._max_context_length = max_context_length
        self._embedding_dimension = embedding_dimension
        self._storage_backend = storage_backend
        self._serializer = serializer
        self._extra: Dict[str, Any] = kwargs

    @property
    def max_entries(self) -> int:
        return self._max_entries

    @property
    def max_size_bytes(self) -> int:
        return self._max_size_bytes

    @property
    def default_ttl(self) -> float:
        return self._default_ttl

    @property
    def retention_policy(self) -> RetentionPolicy:
        return self._retention_policy

    @property
    def consolidation_strategy(self) -> ConsolidationStrategy:
        return self._consolidation_strategy

    @property
    def consolidation_interval(self) -> float:
        return self._consolidation_interval

    @property
    def backup_interval(self) -> float:
        return self._backup_interval

    @property
    def checkpoint_interval(self) -> float:
        return self._checkpoint_interval

    @property
    def cache_ttl(self) -> float:
        return self._cache_ttl

    @property
    def cache_max_size(self) -> int:
        return self._cache_max_size

    @property
    def enable_encryption(self) -> bool:
        return self._enable_encryption

    @property
    def enable_compression(self) -> bool:
        return self._enable_compression

    @property
    def enable_metrics(self) -> bool:
        return self._enable_metrics

    @property
    def enable_logging(self) -> bool:
        return self._enable_logging

    @property
    def enable_audit(self) -> bool:
        return self._enable_audit

    @property
    def default_scope(self) -> MemoryScope:
        return self._default_scope

    @property
    def auto_consolidate(self) -> bool:
        return self._auto_consolidate

    @property
    def auto_evict(self) -> bool:
        return self._auto_evict

    @property
    def eviction_batch_size(self) -> int:
        return self._eviction_batch_size

    @property
    def max_context_length(self) -> int:
        return self._max_context_length

    @property
    def embedding_dimension(self) -> int:
        return self._embedding_dimension

    @property
    def storage_backend(self) -> str:
        return self._storage_backend

    @property
    def serializer(self) -> str:
        return self._serializer

    def get_extra(self, key: str, default: Any = None) -> Any:
        return self._extra.get(key, default)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "max_entries": self._max_entries,
            "max_size_bytes": self._max_size_bytes,
            "default_ttl": self._default_ttl,
            "retention_policy": self._retention_policy.name,
            "consolidation_strategy": self._consolidation_strategy.name,
            "consolidation_interval": self._consolidation_interval,
            "backup_interval": self._backup_interval,
            "checkpoint_interval": self._checkpoint_interval,
            "cache_ttl": self._cache_ttl,
            "cache_max_size": self._cache_max_size,
            "enable_encryption": self._enable_encryption,
            "enable_compression": self._enable_compression,
            "enable_metrics": self._enable_metrics,
            "enable_logging": self._enable_logging,
            "enable_audit": self._enable_audit,
            "default_scope": self._default_scope.name,
            "auto_consolidate": self._auto_consolidate,
            "auto_evict": self._auto_evict,
            "eviction_batch_size": self._eviction_batch_size,
            "max_context_length": self._max_context_length,
            "embedding_dimension": self._embedding_dimension,
            "storage_backend": self._storage_backend,
            "serializer": self._serializer,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> MemoryConfig:
        return cls(
            max_entries=data.get("max_entries", 100000),
            max_size_bytes=data.get("max_size_bytes", 1073741824),
            default_ttl=data.get("default_ttl", 3600.0),
            retention_policy=RetentionPolicy[data.get("retention_policy", "LRU")],
            consolidation_strategy=ConsolidationStrategy[data.get("consolidation_strategy", "MERGE")],
            consolidation_interval=data.get("consolidation_interval", 300.0),
            backup_interval=data.get("backup_interval", 86400.0),
            checkpoint_interval=data.get("checkpoint_interval", 600.0),
            cache_ttl=data.get("cache_ttl", 60.0),
            cache_max_size=data.get("cache_max_size", 10000),
            enable_encryption=data.get("enable_encryption", False),
            enable_compression=data.get("enable_compression", True),
            enable_metrics=data.get("enable_metrics", True),
            enable_logging=data.get("enable_logging", True),
            enable_audit=data.get("enable_audit", False),
            default_scope=MemoryScope[data.get("default_scope", "LOCAL")],
            auto_consolidate=data.get("auto_consolidate", True),
            auto_evict=data.get("auto_evict", True),
            eviction_batch_size=data.get("eviction_batch_size", 100),
            max_context_length=data.get("max_context_length", 100),
            embedding_dimension=data.get("embedding_dimension", 768),
            storage_backend=data.get("storage_backend", "memory"),
            serializer=data.get("serializer", "json"),
        )

    @classmethod
    def defaults(cls) -> MemoryConfig:
        return cls()
