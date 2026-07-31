"""Organization settings."""
from __future__ import annotations
from typing import Any, Dict

class OrganizationSettings:
    DEFAULTS = {"timezone": "America/Sao_Paulo", "language": "pt-BR", "currency": "BRL", "notifications_enabled": True, "2fa_enabled": False}
    def __init__(self) -> None:
        self._settings: Dict[str, Dict[str, Any]] = {}
    def get_all(self, org_id: str) -> Dict[str, Any]:
        return {**self.DEFAULTS, **self._settings.get(org_id, {})}
    def get(self, org_id: str, key: str) -> Any:
        return self._settings.get(org_id, {}).get(key, self.DEFAULTS.get(key))
    def set(self, org_id: str, key: str, value: Any) -> None:
        self._settings.setdefault(org_id, {})[key] = value
    def set_many(self, org_id: str, values: Dict[str, Any]) -> None:
        self._settings.setdefault(org_id, {}).update(values)
    def reset(self, org_id: str, key: str) -> bool:
        if org_id in self._settings and key in self._settings[org_id]:
            del self._settings[org_id][key]
            return True
        return False
    def reset_all(self, org_id: str) -> int:
        n = len(self._settings.get(org_id, {}))
        self._settings.pop(org_id, None)
        return n
