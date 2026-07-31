"""
Integration Manager - Lifecycle management
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import hashlib


class ManagerAction(Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    ENABLE = "enable"
    DISABLE = "disable"
    SYNC = "sync"
    TEST = "test"


@dataclass
class ManagerEvent:
    event_id: str
    action: ManagerAction
    integration_id: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    user: str = "system"


class IntegrationManager:
    def __init__(self):
        self.integrations: Dict[str, Dict[str, Any]] = {}
        self.event_log: List[ManagerEvent] = []
        self.groups: Dict[str, List[str]] = {}
        self.schedules: Dict[str, Dict[str, Any]] = {}

    def create_integration(self, name: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
        integration_id = hashlib.sha256(f"{name}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        integration = {"id": integration_id, "name": name, "config": config or {}, "status": "active", "created_at": datetime.now().isoformat(), "updated_at": datetime.now().isoformat()}
        self.integrations[integration_id] = integration
        self._log_event(ManagerAction.CREATE, integration_id, {"name": name})
        return integration

    def update_integration(self, integration_id: str, **kwargs) -> bool:
        integration = self.integrations.get(integration_id)
        if integration:
            for k, v in kwargs.items():
                integration[k] = v
            integration["updated_at"] = datetime.now().isoformat()
            self._log_event(ManagerAction.UPDATE, integration_id, kwargs)
            return True
        return False

    def delete_integration(self, integration_id: str) -> bool:
        if integration_id in self.integrations:
            del self.integrations[integration_id]
            self._log_event(ManagerAction.DELETE, integration_id)
            return True
        return False

    def get_integration(self, integration_id: str) -> Optional[Dict[str, Any]]:
        return self.integrations.get(integration_id)

    def list_integrations(self) -> List[Dict[str, Any]]:
        return list(self.integrations.values())

    def create_group(self, name: str, integration_ids: List[str] = None) -> None:
        self.groups[name] = integration_ids or []

    def add_to_group(self, group_name: str, integration_id: str) -> bool:
        if group_name in self.groups:
            self.groups[group_name].append(integration_id)
            return True
        return False

    def get_group(self, group_name: str) -> List[Dict[str, Any]]:
        ids = self.groups.get(group_name, [])
        return [self.integrations[i] for i in ids if i in self.integrations]

    def schedule_sync(self, integration_id: str, interval_seconds: int = 3600) -> None:
        self.schedules[integration_id] = {"interval": interval_seconds, "last_run": None, "next_run": datetime.now().isoformat()}

    def get_schedule(self, integration_id: str) -> Optional[Dict[str, Any]]:
        return self.schedules.get(integration_id)

    def test_integration(self, integration_id: str) -> Dict[str, Any]:
        integration = self.integrations.get(integration_id)
        if not integration:
            return {"success": False, "error": "Not found"}
        self._log_event(ManagerAction.TEST, integration_id)
        return {"success": True, "integration_id": integration_id, "tested_at": datetime.now().isoformat()}

    def _log_event(self, action: ManagerAction, integration_id: str, details: Dict[str, Any] = None) -> None:
        event = ManagerEvent(event_id=hashlib.sha256(f"{action.value}{integration_id}{datetime.now().isoformat()}".encode()).hexdigest()[:16], action=action, integration_id=integration_id, details=details or {})
        self.event_log.append(event)

    def get_events(self, integration_id: str = None) -> List[ManagerEvent]:
        if integration_id:
            return [e for e in self.event_log if e.integration_id == integration_id]
        return self.event_log

    def count(self) -> int:
        return len(self.integrations)
