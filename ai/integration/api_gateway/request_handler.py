"""
Request Handler - Process incoming requests
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import json


@dataclass
class RequestData:
    request_id: str
    method: str
    path: str
    headers: Dict[str, str] = field(default_factory=dict)
    body: Any = None
    query: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ValidationResult:
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class RequestHandler:
    def __init__(self):
        self.processed: List[RequestData] = []
        self.validators: Dict[str, Any] = {}
        self.transformers: List[Any] = []

    def create_request(self, method: str, path: str, headers: Dict[str, str] = None, body: Any = None) -> RequestData:
        request_id = hashlib.sha256(f"{method}{path}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        req = RequestData(request_id=request_id, method=method, path=path, headers=headers or {}, body=body)
        self.processed.append(req)
        return req

    def validate(self, request: RequestData) -> ValidationResult:
        errors = []
        if not request.method:
            errors.append("Method required")
        if not request.path:
            errors.append("Path required")
        return ValidationResult(valid=len(errors) == 0, errors=errors)

    def parse_body(self, body: str, content_type: str = "application/json") -> Any:
        if content_type == "application/json":
            try:
                return json.loads(body)
            except json.JSONDecodeError:
                return None
        return body

    def add_validator(self, name: str, validator: Any) -> None:
        self.validators[name] = validator

    def get_recent(self, limit: int = 10) -> List[RequestData]:
        return self.processed[-limit:]

    def count(self) -> int:
        return len(self.processed)
