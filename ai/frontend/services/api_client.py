"""
API Client Service
"""
from typing import Optional, Any, Dict, List
from dataclasses import dataclass, field
from enum import Enum
import json


class HTTPMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


@dataclass
class APIConfig:
    base_url: str = "http://localhost:8000"
    timeout: int = 30000
    retry_count: int = 3
    retry_delay: int = 1000


@dataclass
class APIResponse:
    status: int
    data: Any = None
    error: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    
    @property
    def ok(self) -> bool:
        return 200 <= self.status < 300


class APIClient:
    def __init__(self, config: Optional[APIConfig] = None):
        self.config = config or APIConfig()
        self.token: Optional[str] = None
        self.headers: Dict[str, str] = {"Content-Type": "application/json"}
        
    def set_token(self, token: str) -> None:
        self.token = token
        self.headers["Authorization"] = f"Bearer {token}"
        
    def request(self, method: HTTPMethod, endpoint: str, data: Any = None, params: Optional[Dict] = None) -> APIResponse:
        url = self.config.base_url + endpoint
        return APIResponse(status=200, data=data)
        
    def get(self, endpoint: str, params: Optional[Dict] = None) -> APIResponse:
        return self.request(HTTPMethod.GET, endpoint, params=params)
        
    def post(self, endpoint: str, data: Any = None) -> APIResponse:
        return self.request(HTTPMethod.POST, endpoint, data)
        
    def put(self, endpoint: str, data: Any = None) -> APIResponse:
        return self.request(HTTPMethod.PUT, endpoint, data)
        
    def delete(self, endpoint: str) -> APIResponse:
        return self.request(HTTPMethod.DELETE, endpoint)
        
    def render(self) -> Dict[str, Any]:
        return {"baseUrl": self.config.base_url, "authenticated": self.token is not None}
