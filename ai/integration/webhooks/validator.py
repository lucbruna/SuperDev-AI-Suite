"""
Webhook Validator - Validate webhook payloads
"""
import hashlib
import hmac
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ValidationResult:
    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class WebhookValidator:
    def __init__(self):
        self.schemas: dict[str, dict[str, Any]] = {}
        self.secrets: dict[str, str] = {}

    def register_schema(self, event_type: str, schema: dict[str, Any]) -> None:
        self.schemas[event_type] = schema

    def validate_payload(self, event_type: str, payload: dict[str, Any]) -> ValidationResult:
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
