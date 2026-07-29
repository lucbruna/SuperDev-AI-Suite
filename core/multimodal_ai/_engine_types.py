from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from .multimodal_config import MultimodalConfig
from .multimodal_security import MultimodalSecurityManager


class EngineState(Enum):
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class EngineConfig:
    config: MultimodalConfig
    security: MultimodalSecurityManager
    auto_start: bool = True
    enable_text: bool = True
    enable_voice: bool = True
    enable_vision: bool = True
    enable_video: bool = True
    enable_documents: bool = True
    enable_sensors: bool = True
    enable_conversation: bool = True
    enable_translation: bool = True
    max_concurrent_tasks: int = 50


@dataclass
class EngineMetrics:
    state: EngineState = EngineState.INITIALIZING
    start_time: Optional[datetime] = None
    inputs_processed: int = 0
    outputs_generated: int = 0
    sessions_created: int = 0
    errors: int = 0
    total_processing_time_ms: float = 0.0
    modality_counts: Dict[str, int] = field(default_factory=dict)
    subsystem_status: Dict[str, str] = field(default_factory=dict)
    last_action_time: Optional[datetime] = None
