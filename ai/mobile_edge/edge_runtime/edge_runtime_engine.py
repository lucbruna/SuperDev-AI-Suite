"""Edge Runtime Engine - Core edge AI runtime management."""

from dataclasses import dataclass
from enum import Enum


class RuntimeState(Enum):
    IDLE = "idle"
    RUNNING = "running"
    OPTIMIZING = "optimizing"
    ERROR = "error"


@dataclass
class RuntimeConfig:
    device_id: str
    max_memory_mb: float = 512.0
    max_cpu_percent: float = 80.0
    enable_gpu: bool = False
    enable_npu: bool = False
    power_mode: str = "balanced"


class EdgeRuntimeEngine:
    def __init__(self):
        self.configs: dict[str, RuntimeConfig] = {}
        self.states: dict[str, RuntimeState] = {}
        self.metrics: dict[str, dict[str, float]] = {}

    def configure(self, device_id: str, **kwargs) -> RuntimeConfig:
        config = RuntimeConfig(device_id=device_id, **kwargs)
        self.configs[device_id] = config
        self.states[device_id] = RuntimeState.IDLE
        return config

    def start(self, device_id: str) -> bool:
        if device_id in self.configs:
            self.states[device_id] = RuntimeState.RUNNING
            return True
        return False

    def stop(self, device_id: str) -> bool:
        if device_id in self.states:
            self.states[device_id] = RuntimeState.IDLE
            return True
        return False

    def get_state(self, device_id: str) -> RuntimeState:
        return self.states.get(device_id, RuntimeState.IDLE)

    def record_metric(self, device_id: str, metric: str, value: float) -> None:
        self.metrics.setdefault(device_id, {})[metric] = value

    def get_metrics(self, device_id: str) -> dict[str, float]:
        return self.metrics.get(device_id, {})

    def list_devices(self) -> list[str]:
        return list(self.configs.keys())

    def count(self) -> int:
        return len(self.configs)
