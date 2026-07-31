"""
Response Manager - Format and return responses
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ResponseData:
    status_code: int
    body: Any = None
    headers: Dict[str, str] = field(default_factory=dict)
    duration_ms: float = 0.0
    cached: bool = False


class ResponseManager:
    def __init__(self):
        self.responses: List[ResponseData] = []
        self.cache: Dict[str, ResponseData] = {}
        self.default_headers: Dict[str, str] = {"Content-Type": "application/json", "X-Powered-By": "SuperDev"}

    def create_response(self, status_code: int, body: Any = None, headers: Dict[str, str] = None) -> ResponseData:
        resp = ResponseData(status_code=status_code, body=body, headers={**self.default_headers, **(headers or {})})
        self.responses.append(resp)
        return resp

    def success(self, data: Any = None) -> ResponseData:
        return self.create_response(200, data)

    def created(self, data: Any = None) -> ResponseData:
        return self.create_response(201, data)

    def bad_request(self, error: str = "Bad Request") -> ResponseData:
        return self.create_response(400, {"error": error})

    def unauthorized(self, error: str = "Unauthorized") -> ResponseData:
        return self.create_response(401, {"error": error})

    def not_found(self, error: str = "Not Found") -> ResponseData:
        return self.create_response(404, {"error": error})

    def server_error(self, error: str = "Internal Server Error") -> ResponseData:
        return self.create_response(500, {"error": error})

    def set_cache(self, key: str, response: ResponseData, ttl: int = 60) -> None:
        self.cache[key] = response

    def get_cache(self, key: str) -> Optional[ResponseData]:
        return self.cache.get(key)

    def clear_cache(self) -> None:
        self.cache.clear()

    def get_recent(self, limit: int = 10) -> List[ResponseData]:
        return self.responses[-limit:]

    def count(self) -> int:
        return len(self.responses)
