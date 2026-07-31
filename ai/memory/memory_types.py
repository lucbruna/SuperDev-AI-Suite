from __future__ import annotations

from collections.abc import Callable
from enum import Enum, auto
from typing import Any, TypeVar

T = TypeVar("T")

MemoryID = str
MemoryData = dict[str, Any]
Metadata = dict[str, Any]
Tags = list[str]
Timestamp = float
Priority = int


class MemoryScope(Enum):
    """Scope of a memory entry."""
    LOCAL = auto()
    SESSION = auto()
    AGENT = auto()
    GLOBAL = auto()
    PERSISTENT = auto()


class MemoryStatus(Enum):
    """Lifecycle status of a memory entry."""
    PENDING = auto()
    ACTIVE = auto()
    ARCHIVED = auto()
    COMPRESSED = auto()
    EVICTED = auto()
    CORRUPTED = auto()


class MemoryCategory(Enum):
    """Functional category of memory."""
    CONTEXT = auto()
    KNOWLEDGE = auto()
    HISTORY = auto()
    EMBEDDING = auto()
    CACHE = auto()
    CHECKPOINT = auto()
    SNAPSHOT = auto()
    BACKUP = auto()
    METADATA = auto()
    SYSTEM = auto()


class RetentionPolicy(Enum):
    """Policies for memory retention and eviction."""
    KEEP_FOREVER = auto()
    TTL = auto()
    LRU = auto()
    LFU = auto()
    SIZE_LIMIT = auto()
    PRIORITY = auto()


class ConsolidationStrategy(Enum):
    """Strategies for memory consolidation."""
    MERGE = auto()
    SUMMARIZE = auto()
    COMPRESS = auto()
    AGGREGATE = auto()
    LINK = auto()
    DEDUP = auto()


class MemoryEventType(Enum):
    """Types of events emitted by the memory subsystem."""
    STORED = auto()
    RETRIEVED = auto()
    UPDATED = auto()
    DELETED = auto()
    EVICTED = auto()
    EXPIRED = auto()
    CORRUPTED = auto()
    CONSOLIDATED = auto()
    BACKED_UP = auto()
    RESTORED = auto()
    CHECKPOINTED = auto()
    SNAPSHOTTED = auto()
    ERROR = auto()
    WARNING = auto()


MemoryFilter = Callable[[MemoryData], bool]
MemoryTransform = Callable[[MemoryData], MemoryData]
