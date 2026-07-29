"""
Employee Context - Shared context for all HR subsystems.

Centralized state management across the HR AI Engine.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from threading import Lock
from typing import Any, Callable, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


@dataclass
class ContextSnapshot:
    timestamp: datetime
    recruitment: Dict[str, Any]
    onboarding: Dict[str, Any]
    performance: Dict[str, Any]
    learning: Dict[str, Any]
    talent: Dict[str, Any]
    culture: Dict[str, Any]
    workforce: Dict[str, Any]
    payroll: Dict[str, Any]
    key_metrics: Dict[str, float]


class SubsystemContext:
    def __init__(self, name: str):
        self._name = name
        self._data: Dict[str, Any] = {}
        self._lock = Lock()

    @property
    def name(self) -> str:
        return self._name

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

    def set_all(self, data: Dict[str, Any]) -> None:
        with self._lock:
            self._data = dict(data)

    def clear(self) -> None:
        with self._lock:
            self._data.clear()

    def __getitem__(self, key: str) -> Any:
        value = self.get(key)
        if value is None and key not in self._data:
            raise KeyError(key)
        return value

    def __setitem__(self, key: str, value: Any) -> None:
        self.set(key, value)

    def __contains__(self, key: str) -> bool:
        with self._lock:
            return key in self._data


class EmployeeContext:
    def __init__(self):
        self._lock = Lock()
        self._state: Dict[str, Any] = {}
        self._metadata: Dict[str, Any] = {}
        self._subsystem_contexts: Dict[str, SubsystemContext] = {}
        self._observers: Dict[str, List[Callable]] = {}
        self._snapshots: List[ContextSnapshot] = []
        self._max_snapshots = 50
        self._init_subsystems()

    def _init_subsystems(self) -> None:
        for name in ["recruitment", "onboarding", "performance", "learning",
                      "talent", "culture", "workforce", "payroll", "metrics"]:
            self._subsystem_contexts[name] = SubsystemContext(name)

    @property
    def recruitment(self) -> SubsystemContext:
        return self._subsystem_contexts["recruitment"]

    @property
    def onboarding(self) -> SubsystemContext:
        return self._subsystem_contexts["onboarding"]

    @property
    def performance(self) -> SubsystemContext:
        return self._subsystem_contexts["performance"]

    @property
    def learning(self) -> SubsystemContext:
        return self._subsystem_contexts["learning"]

    @property
    def talent(self) -> SubsystemContext:
        return self._subsystem_contexts["talent"]

    @property
    def culture(self) -> SubsystemContext:
        return self._subsystem_contexts["culture"]

    @property
    def workforce(self) -> SubsystemContext:
        return self._subsystem_contexts["workforce"]

    @property
    def payroll(self) -> SubsystemContext:
        return self._subsystem_contexts["payroll"]

    @property
    def metrics(self) -> SubsystemContext:
        return self._subsystem_contexts["metrics"]

    def get(self, key: str, default: Any = None) -> Any:
        with self._lock:
            return self._state.get(key, default)

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            self._state[key] = value

    def update(self, data: Dict[str, Any]) -> None:
        with self._lock:
            self._state.update(data)

    def take_snapshot(self) -> ContextSnapshot:
        s = ContextSnapshot(
            timestamp=datetime.utcnow(),
            recruitment=self.recruitment.get_all(),
            onboarding=self.onboarding.get_all(),
            performance=self.performance.get_all(),
            learning=self.learning.get_all(),
            talent=self.talent.get_all(),
            culture=self.culture.get_all(),
            workforce=self.workforce.get_all(),
            payroll=self.payroll.get_all(),
            key_metrics=self.metrics.get_all(),
        )
        self._snapshots.append(s)
        if len(self._snapshots) > self._max_snapshots:
            self._snapshots.pop(0)
        return s
