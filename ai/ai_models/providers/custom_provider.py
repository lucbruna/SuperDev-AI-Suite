"""Custom provider."""
from __future__ import annotations
from typing import Any, Callable, Dict, List

class CustomProvider:
    def __init__(self, name: str = "custom") -> None:
        self._name = name
        self._handler: Callable = lambda p, **kw: {"content": f"Custom response to: {p[:50]}", "status": "ok"}
        self._config: Dict[str, Any] = {}
        self._requests = 0
    def set_handler(self, handler: Callable) -> None:
        self._handler = handler
    def complete(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        self._requests += 1
        try:
            return self._handler(prompt, **kwargs)
        except Exception as e:
            return {"error": str(e), "status": "failed"}
    def set_config(self, config: Dict[str, Any]) -> None:
        self._config = config
    def get_config(self) -> Dict[str, Any]:
        return dict(self._config)
    def get_name(self) -> str:
        return self._name
    def get_stats(self) -> Dict[str, int]:
        return {"requests": self._requests}
    def get_models(self) -> List[str]:
        return [self._name]
