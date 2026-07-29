"""
Customer Context - Shared context for all customer subsystems.

Centralized state management across the Customer AI Engine.
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
    chatbot: Dict[str, Any]
    voice: Dict[str, Any]
    omnichannel: Dict[str, Any]
    sales: Dict[str, Any]
    support: Dict[str, Any]
    personalization: Dict[str, Any]
    sentiment: Dict[str, Any]
    loyalty: Dict[str, Any]
    automation: Dict[str, Any]
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


class CustomerContext:
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
        for name in ["chatbot", "voice", "omnichannel", "sales", "support",
                      "personalization", "sentiment", "loyalty", "automation", "metrics"]:
            self._subsystem_contexts[name] = SubsystemContext(name)

    @property
    def chatbot(self) -> SubsystemContext:
        return self._subsystem_contexts["chatbot"]

    @property
    def voice(self) -> SubsystemContext:
        return self._subsystem_contexts["voice"]

    @property
    def omnichannel(self) -> SubsystemContext:
        return self._subsystem_contexts["omnichannel"]

    @property
    def sales(self) -> SubsystemContext:
        return self._subsystem_contexts["sales"]

    @property
    def support(self) -> SubsystemContext:
        return self._subsystem_contexts["support"]

    @property
    def personalization(self) -> SubsystemContext:
        return self._subsystem_contexts["personalization"]

    @property
    def sentiment(self) -> SubsystemContext:
        return self._subsystem_contexts["sentiment"]

    @property
    def loyalty(self) -> SubsystemContext:
        return self._subsystem_contexts["loyalty"]

    @property
    def automation(self) -> SubsystemContext:
        return self._subsystem_contexts["automation"]

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
            chatbot=self.chatbot.get_all(),
            voice=self.voice.get_all(),
            omnichannel=self.omnichannel.get_all(),
            sales=self.sales.get_all(),
            support=self.support.get_all(),
            personalization=self.personalization.get_all(),
            sentiment=self.sentiment.get_all(),
            loyalty=self.loyalty.get_all(),
            automation=self.automation.get_all(),
            key_metrics=self.metrics.get_all(),
        )
        self._snapshots.append(s)
        if len(self._snapshots) > self._max_snapshots:
            self._snapshots.pop(0)
        return s
