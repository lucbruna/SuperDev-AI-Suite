"""Storage models."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class StorageType(Enum):
    DATA_LAKE = "data_lake"
    DATA_WAREHOUSE = "data_warehouse"
    OBJECT_STORAGE = "object_storage"
    CACHE = "cache"


class StorageTier(Enum):
    HOT = "hot"
    WARM = "warm"
    COLD = "cold"
    ARCHIVE = "archive"


@dataclass
class StorageBucket:
    bucket_id: str
    name: str = ""
    storage_type: StorageType = StorageType.DATA_LAKE
    tier: StorageTier = StorageTier.HOT
    capacity_bytes: int = 0
    used_bytes: int = 0
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def utilization_pct(self) -> float:
        return (self.used_bytes / self.capacity_bytes * 100) if self.capacity_bytes > 0 else 0.0


@dataclass
class StoredObject:
    object_id: str
    bucket_id: str = ""
    key: str = ""
    content_type: str = ""
    size_bytes: int = 0
    checksum: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime | None = None


@dataclass
class DataPartition:
    partition_id: str
    dataset: str = ""
    key: str = ""
    tier: StorageTier = StorageTier.HOT
    record_count: int = 0
    size_bytes: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime | None = None
