"""User preferences."""
from __future__ import annotations
from typing import Any, Dict

class UserPreferences:
    DEFAULTS = {"theme": "light", "language": "pt-BR", "notifications_email": True, "notifications_push": True, "dashboard_layout": "default"}
    def __init__(self) -> None:
        self._prefs: Dict[str, Dict[str, Any]] = {}
    def get(self, user_id: str) -> Dict[str, Any]:
        return {**self.DEFAULTS, **self._prefs.get(user_id, {})}
    def set(self, user_id: str, key: str, value: Any) -> None:
        self._prefs.setdefault(user_id, {})[key] = value
    def set_many(self, user_id: str, values: Dict[str, Any]) -> None:
        self._prefs.setdefault(user_id, {}).update(values)
    def get_one(self, user_id: str, key: str) -> Any:
        return self._prefs.get(user_id, {}).get(key, self.DEFAULTS.get(key))
    def reset(self, user_id: str, key: str) -> bool:
        if user_id in self._prefs and key in self._prefs[user_id]:
            del self._prefs[user_id][key]
            return True
        return False
    def reset_all(self, user_id: str) -> int:
        n = len(self._prefs.get(user_id, {}))
        self._prefs.pop(user_id, None)
        return n
