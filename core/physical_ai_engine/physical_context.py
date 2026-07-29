from __future__ import annotations

import logging
from threading import Lock
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class SubsystemContext:
    def __init__(self, name: str):
        self._name = name
        self._data: Dict[str, Any] = {}
        self._lock = Lock()

    def get(self, key: str, default: Any = None) -> Any:
        with self._lock:
            return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            self._data[key] = value

    def update(self, data: Dict[str, Any]) -> None:
        with self._lock:
            self._data.update(data)

    def delete(self, key: str) -> None:
        with self._lock:
            self._data.pop(key, None)

    def get_all(self) -> Dict[str, Any]:
        with self._lock:
            return dict(self._data)

    def clear(self) -> None:
        with self._lock:
            self._data.clear()


class PhysicalContext:
    def __init__(self):
        self._lock = Lock()
        self._state: Dict[str, Any] = {}
        self._subsystem_contexts: Dict[str, SubsystemContext] = {}
        self._init_subsystems()

    def _init_subsystems(self) -> None:
        for name in ["robotics", "automation", "iot", "sensors", "vision",
                      "motion", "simulation", "digital_twin", "maintenance", "devices", "safety"]:
            self._subsystem_contexts[name] = SubsystemContext(name)

    @property
    def robotics(self) -> SubsystemContext:
        return self._subsystem_contexts["robotics"]

    @property
    def automation(self) -> SubsystemContext:
        return self._subsystem_contexts["automation"]

    @property
    def iot(self) -> SubsystemContext:
        return self._subsystem_contexts["iot"]

    @property
    def sensors(self) -> SubsystemContext:
        return self._subsystem_contexts["sensors"]

    @property
    def vision(self) -> SubsystemContext:
        return self._subsystem_contexts["vision"]

    @property
    def motion(self) -> SubsystemContext:
        return self._subsystem_contexts["motion"]

    @property
    def simulation(self) -> SubsystemContext:
        return self._subsystem_contexts["simulation"]

    @property
    def digital_twin(self) -> SubsystemContext:
        return self._subsystem_contexts["digital_twin"]

    @property
    def maintenance(self) -> SubsystemContext:
        return self._subsystem_contexts["maintenance"]

    @property
    def devices(self) -> SubsystemContext:
        return self._subsystem_contexts["devices"]

    @property
    def safety(self) -> SubsystemContext:
        return self._subsystem_contexts["safety"]

    def get(self, key: str, default: Any = None) -> Any:
        with self._lock:
            return self._state.get(key, default)

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            self._state[key] = value

    def update(self, data: Dict[str, Any]) -> None:
        with self._lock:
            self._state.update(data)
