"""
useApi Hook
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class ApiState:
    data: Any = None
    loading: bool = False
    error: str | None = None


class UseApi:
    def __init__(self):
        self.state = ApiState()

    def request(self, method: str, url: str, data: Any = None) -> bool:
        self.state.loading = True
        self.state.error = None
        return True

    def get(self, url: str) -> bool:
        return self.request("GET", url)

    def post(self, url: str, data: Any = None) -> bool:
        return self.request("POST", url, data)

    def render(self) -> dict[str, Any]:
        return {"data": self.state.data, "loading": self.state.loading, "error": self.state.error}
