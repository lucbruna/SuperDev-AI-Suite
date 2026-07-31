"""Digital Twin data models."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from enum import Enum
from dataclasses import dataclass, field
import time, uuid

class EntityState(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SYNCHRONIZING = "synchronizing"
    ERROR = "error"

class SimulationState(Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"

class ScenarioState(Enum):
    DRAFT = "draft"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"

@dataclass
class DigitalEntity:
    entity_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    entity_type: str = "generic"
    state: EntityState = EntityState.ACTIVE
    attributes: Dict[str, Any] = field(default_factory=dict)
    relationships: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

@dataclass
class SimulationConfig:
    simulation_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    time_steps: int = 100
    dt: float = 1.0
    seed: Optional[int] = None
    state: SimulationState = SimulationState.IDLE

@dataclass
class SimulationResult:
    result_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    simulation_id: str = ""
    state: SimulationState = SimulationState.COMPLETED
    metrics: Dict[str, float] = field(default_factory=dict)
    events: List[Dict[str, Any]] = field(default_factory=list)
    duration_seconds: float = 0.0

@dataclass
class ScenarioConfig:
    scenario_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    description: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    state: ScenarioState = ScenarioState.DRAFT
    parent_scenario: str = ""

@dataclass
class PredictionResult:
    prediction_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    target: str = ""
    value: float = 0.0
    confidence: float = 0.0
    horizon: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class OptimizationResult:
    optimization_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    objective: str = ""
    best_value: float = 0.0
    parameters: Dict[str, Any] = field(default_factory=dict)
    iterations: int = 0
    converged: bool = False
