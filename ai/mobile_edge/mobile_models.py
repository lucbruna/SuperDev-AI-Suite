"""Mobile Models - Data models for mobile/edge platform."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class SyncStrategy(Enum):
    FULL = "full"
    INCREMENTAL = "incremental"
    DELTA = "delta"
    ON_DEMAND = "on_demand"


class ConnectionType(Enum):
    WIFI = "wifi"
    CELLULAR = "cellular"
    BLUETOOTH = "bluetooth"
    USB = "usb"
    SATELLITE = "satellite"
    OFFLINE = "offline"


class BatteryMode(Enum):
    NORMAL = "normal"
    POWER_SAVER = "power_saver"
    ULTRA_SAVER = "ultra_saver"
    CHARGING = "charging"


@dataclass
class SyncConfig:
    strategy: SyncStrategy = SyncStrategy.INCREMENTAL
    interval_seconds: int = 300
    wifi_only: bool = True
    compression: bool = True
    encryption: bool = True
    max_batch_size: int = 1000
    retry_attempts: int = 3


@dataclass
class OfflineConfig:
    enabled: bool = True
    cache_size_mb: int = 500
    max_offline_days: int = 7
    auto_sync: bool = True
    priority_data: list[str] = field(default_factory=list)


@dataclass
class EdgeConfig:
    max_model_size_mb: float = 500.0
    preferred_accelerator: str = "cpu"
    inference_timeout_ms: int = 5000
    cache_results: bool = True
    max_concurrent_inferences: int = 1


@dataclass
class MobileProfile:
    user_id: str
    devices: list[str] = field(default_factory=list)
    preferences: dict[str, Any] = field(default_factory=dict)
    sync_config: SyncConfig = field(default_factory=SyncConfig)
    offline_config: OfflineConfig = field(default_factory=OfflineConfig)
    edge_config: EdgeConfig = field(default_factory=EdgeConfig)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class DeviceCapability:
    has_camera: bool = False
    has_gps: bool = False
    has_biometric: bool = False
    has_nfc: bool = False
    has_gpu: bool = False
    has_npu: bool = False
    max_storage_mb: float = 0.0
    ram_mb: float = 0.0
    screen_width: int = 0
    screen_height: int = 0
