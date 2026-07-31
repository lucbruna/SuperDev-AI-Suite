"""Digital Twin configuration."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from enum import Enum
from dataclasses import dataclass, field

class TwinType(Enum):
    ENTERPRISE = "enterprise"
    SOFTWARE = "software"
    INDUSTRIAL = "industrial"
    INFRASTRUCTURE = "infrastructure"
    ORGANIZATIONAL = "organizational"

class SyncMode(Enum):
    REALTIME = "realtime"
    NEAR_REALTIME = "near_realtime"
    BATCH = "batch"
    MANUAL = "manual"

@dataclass
class SimulationLimits:
    max_entities: int = 10000
    max_events: int = 100000
    max_scenarios: int = 100
    max_time_steps: int = 10000
    max_duration_seconds: float = 300.0

@dataclass
class SynchronizationConfig:
    mode: SyncMode = SyncMode.NEAR_REALTIME
    interval_seconds: float = 5.0
    batch_size: int = 100
    conflict_resolution: str = "latest_wins"

@dataclass
class TwinConfig:
    twin_type: TwinType = TwinType.ENTERPRISE
    name: str = "default_twin"
    description: str = ""
    limits: SimulationLimits = field(default_factory=SimulationLimits)
    sync_config: SynchronizationConfig = field(default_factory=SynchronizationConfig)
    auto_sync: bool = True
    validation_enabled: bool = True
    analytics_enabled: bool = True
    visualization_enabled: bool = True
    prediction_enabled: bool = True
    optimization_enabled: bool = True
    security_enabled: bool = True
    debug_mode: bool = False
