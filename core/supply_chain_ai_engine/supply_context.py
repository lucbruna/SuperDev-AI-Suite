"""
Supply Chain Context - Shared context manager for all supply chain subsystems.

Provides a centralized context that carries shared state,
configuration references, and subsystem access across the engine.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set
from threading import Lock

logger = logging.getLogger(__name__)


class ContextError(Exception):
    """Base exception for context errors."""


@dataclass
class ContextSnapshot:
    """Immutable snapshot of context state at a point in time."""
    timestamp: datetime
    inventory_data: Dict[str, Any]
    demand_data: Dict[str, Any]
    procurement_data: Dict[str, Any]
    supplier_data: Dict[str, Any]
    logistics_data: Dict[str, Any]
    warehouse_data: Dict[str, Any]
    forecasting_data: Dict[str, Any]
    key_metrics: Dict[str, float]


class SupplyChainContext:
    """
    Central context manager for the Supply Chain AI Engine.
    
    Manages shared state, configuration references, and provides
    access to all subsystem contexts.
    
    Thread-safe context sharing across all subsystems.
    """
    
    def __init__(self):
        self._lock = Lock()
        self._state: Dict[str, Any] = {}
        self._metadata: Dict[str, Any] = {}
        self._subsystem_contexts: Dict[str, "SubsystemContext"] = {}
        self._observers: Dict[str, List[Callable]] = {}
        self._snapshots: List[ContextSnapshot] = []
        self._max_snapshots = 50
        
        self._init_subsystem_contexts()
        logger.info("SupplyChainContext initialized")
        
    def _init_subsystem_contexts(self) -> None:
        """Initialize default subsystem contexts."""
        self._subsystem_contexts["inventory"] = SubsystemContext("inventory")
        self._subsystem_contexts["demand"] = SubsystemContext("demand")
        self._subsystem_contexts["procurement"] = SubsystemContext("procurement")
        self._subsystem_contexts["suppliers"] = SubsystemContext("suppliers")
        self._subsystem_contexts["logistics"] = SubsystemContext("logistics")
        self._subsystem_contexts["warehouse"] = SubsystemContext("warehouse")
        self._subsystem_contexts["forecasting"] = SubsystemContext("forecasting")
        self._subsystem_contexts["optimization"] = SubsystemContext("optimization")
        self._subsystem_contexts["integrations"] = SubsystemContext("integrations")
        self._subsystem_contexts["metrics"] = SubsystemContext("metrics")
        
    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from context."""
        with self._lock:
            return self._state.get(key, default)
            
    def set(self, key: str, value: Any) -> None:
        """Set a value in context."""
        with self._lock:
            self._state[key] = value
            self._notify_observers(key, value)
            
    def update(self, data: Dict[str, Any]) -> None:
        """Bulk update context values."""
        with self._lock:
            self._state.update(data)
            for key, value in data.items():
                self._notify_observers(key, value)
                
    def delete(self, key: str) -> None:
        """Remove a key from context."""
        with self._lock:
            if key in self._state:
                del self._state[key]
                self._notify_observers(key, None)
                
    def clear(self) -> None:
        """Clear all context state."""
        with self._lock:
            self._state.clear()
            self._notify_observers("__clear__", None)
            
    def __getitem__(self, key: str) -> Any:
        value = self.get(key)
        if value is None and key not in self._state:
            raise KeyError(key)
        return value
        
    def __setitem__(self, key: str, value: Any) -> None:
        self.set(key, value)
        
    def __contains__(self, key: str) -> bool:
        with self._lock:
            return key in self._state
            
    def __len__(self) -> int:
        with self._lock:
            return len(self._state)
            
    def keys(self) -> Set[str]:
        with self._lock:
            return set(self._state.keys())
            
    def items(self) -> List[tuple]:
        with self._lock:
            return list(self._state.items())
            
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value."""
        return self._metadata.get(key, default)
        
    def set_metadata(self, key: str, value: Any) -> None:
        """Set metadata value."""
        self._metadata[key] = value
        
    @property
    def inventory(self) -> "SubsystemContext":
        return self._subsystem_contexts["inventory"]
        
    @property
    def demand(self) -> "SubsystemContext":
        return self._subsystem_contexts["demand"]
        
    @property
    def procurement(self) -> "SubsystemContext":
        return self._subsystem_contexts["procurement"]
        
    @property
    def suppliers(self) -> "SubsystemContext":
        return self._subsystem_contexts["suppliers"]
        
    @property
    def logistics(self) -> "SubsystemContext":
        return self._subsystem_contexts["logistics"]
        
    @property
    def warehouse(self) -> "SubsystemContext":
        return self._subsystem_contexts["warehouse"]
        
    @property
    def forecasting(self) -> "SubsystemContext":
        return self._subsystem_contexts["forecasting"]
        
    @property
    def optimization(self) -> "SubsystemContext":
        return self._subsystem_contexts["optimization"]
        
    @property
    def integrations(self) -> "SubsystemContext":
        return self._subsystem_contexts["integrations"]
        
    @property
    def metrics(self) -> "SubsystemContext":
        return self._subsystem_contexts["metrics"]
        
    def get_subsystem_context(self, name: str) -> Optional["SubsystemContext"]:
        """Get a specific subsystem context by name."""
        return self._subsystem_contexts.get(name)
        
    def register_observer(self, key: str, callback: Callable) -> None:
        """Register an observer for changes to a key."""
        with self._lock:
            if key not in self._observers:
                self._observers[key] = []
            self._observers[key].append(callback)
            
    def unregister_observer(self, key: str, callback: Callable) -> None:
        """Unregister an observer."""
        with self._lock:
            if key in self._observers:
                self._observers[key].remove(callback)
                
    def _notify_observers(self, key: str, value: Any) -> None:
        """Notify observers of a change."""
        observers = self._observers.get(key, [])
        for callback in observers:
            try:
                callback(key, value)
            except Exception as e:
                logger.error(f"Observer callback error for {key}: {e}")
                
    def take_snapshot(self) -> ContextSnapshot:
        """Take a snapshot of current context state."""
        with self._lock:
            snapshot = ContextSnapshot(
                timestamp=datetime.utcnow(),
                inventory_data=self.inventory.get_all(),
                demand_data=self.demand.get_all(),
                procurement_data=self.procurement.get_all(),
                supplier_data=self.suppliers.get_all(),
                logistics_data=self.logistics.get_all(),
                warehouse_data=self.warehouse.get_all(),
                forecasting_data=self.forecasting.get_all(),
                key_metrics=self.metrics.get_all(),
            )
            self._snapshots.append(snapshot)
            if len(self._snapshots) > self._max_snapshots:
                self._snapshots.pop(0)
            return snapshot
            
    def get_snapshot(self, index: int = -1) -> Optional[ContextSnapshot]:
        """Get a previous snapshot. Negative index from end."""
        if not self._snapshots:
            return None
        return self._snapshots[index]
        
    def rollback_to_snapshot(self, snapshot: ContextSnapshot) -> None:
        """Rollback context to a previous snapshot."""
        with self._lock:
            self.inventory.set_all(snapshot.inventory_data)
            self.demand.set_all(snapshot.demand_data)
            self.procurement.set_all(snapshot.procurement_data)
            self.suppliers.set_all(snapshot.supplier_data)
            self.logistics.set_all(snapshot.logistics_data)
            self.warehouse.set_all(snapshot.warehouse_data)
            self.forecasting.set_all(snapshot.forecasting_data)
            self.metrics.set_all(snapshot.key_metrics)
            logger.info("Context rolled back to snapshot from %s", snapshot.timestamp)


class SubsystemContext:
    """
    Subsystem-specific context manager.
    
    Each subsystem (inventory, demand, etc.) gets its own
    isolated context space within the global context.
    """
    
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
            
    def keys(self) -> Set[str]:
        with self._lock:
            return set(self._data.keys())
            
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
            
    def __len__(self) -> int:
        with self._lock:
            return len(self._data)
            
    def __repr__(self) -> str:
        return f"SubsystemContext('{self._name}', {len(self._data)} keys)"