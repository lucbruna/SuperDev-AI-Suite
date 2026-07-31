"""
Webhook Validator - Validate webhook payloads
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
import hashlib
import hmac


@dataclass
class ValidationResult:
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class WebhookValidator:
    def __init__(self):
        self.schemas: Dict[str, Dict[str, Any]] = {}
        self.secrets: Dict[str, str] = {}

    def register_schema(self, event_type: str, schema: Dict[str, Any]) -> None:
        self.schemas[event_type] = schema

    def validate_payload(self, event_type: str, payload: Dict[str, Any]) -> ValidationResult:
        errors = []
        warnings = []
        schema = self.schemas.get(event_type)
        if schema:
            required = schema.get("required", [])
            for field in required:
                if field not in payload:
                    errors.append(f"Missing required field: {field}")
        return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)

    def verify_signature(self, payload: str, signature: str, secret: str) -> bool:
        expected = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)

    def set_secret(self, webhook_id: str, secret: str) -> None:
        self.secrets[webhook_id] = secret

    def count(self) -> int:
        return len(self.schemas)
