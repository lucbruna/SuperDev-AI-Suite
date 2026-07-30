from __future__ import annotations

from typing import Any, Dict, List, Optional, Protocol, runtime_checkable

from .memory_types import MemoryData, MemoryID, Metadata, Tags, Timestamp


@runtime_checkable
class Storable(Protocol):
    """Protocol for objects that can be stored in memory."""

    def to_memory_data(self) -> MemoryData: ...

    @classmethod
    def from_memory_data(cls, data: MemoryData) -> Storable: ...


@runtime_checkable
class Identifiable(Protocol):
    """Protocol for objects with a memory identifier."""

    @property
    def memory_id(self) -> MemoryID: ...


@runtime_checkable
class Expirable(Protocol):
    """Protocol for objects that can expire."""

    @property
    def expires_at(self) -> Timestamp: ...

    @property
    def is_expired(self) -> bool: ...


@runtime_checkable
class Prioritizable(Protocol):
    """Protocol for objects with priority."""

    @property
    def priority(self) -> int: ...


@runtime_checkable
class Serializable(Protocol):
    """Protocol for serializable memory objects."""

    def serialize(self) -> bytes: ...

    @classmethod
    def deserialize(cls, data: bytes) -> Serializable: ...


@runtime_checkable
class Taggable(Protocol):
    """Protocol for objects that support tags."""

    @property
    def tags(self) -> Tags: ...

    def has_tag(self, tag: str) -> bool: ...


@runtime_checkable
class Mergeable(Protocol):
    """Protocol for objects that can be merged."""

    def merge(self, other: Mergeable) -> Mergeable: ...


@runtime_checkable
class Compressible(Protocol):
    """Protocol for objects that can be compressed."""

    def compress(self) -> bytes: ...

    def decompress(self, data: bytes) -> Compressible: ...
