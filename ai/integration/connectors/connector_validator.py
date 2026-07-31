"""
Connector Validator - Validate connector configs
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field


@dataclass
class ValidationResult:
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class ConnectorValidator:
    def __init__(self):
        self.rules: Dict[str, List[str]] = {}
        self.required_fields: Dict[str, List[str]] = {}

    def add_rule(self, connector_type: str, fields: List[str]) -> None:
        self.required_fields[connector_type] = fields

    def validate(self, connector_type: str, config: Dict[str, Any]) -> ValidationResult:
        errors = []
        warnings = []
        required = self.required_fields.get(connector_type, [])
        for field_name in required:
            if field_name not in config:
                errors.append(f"Missing required field: {field_name}")
        if "timeout" in config and config["timeout"] <= 0:
            warnings.append("Timeout should be positive")
        return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)

    def validate_endpoint(self, endpoint: str) -> ValidationResult:
        errors = []
        if not endpoint:
            errors.append("Endpoint cannot be empty")
        elif not endpoint.startswith(("http://", "https://", "ftp://", "mongodb://", "postgresql://")):
            warnings = ["Endpoint does not start with a known protocol"]
            return ValidationResult(valid=True, warnings=warnings)
        return ValidationResult(valid=len(errors) == 0, errors=errors)

    def count(self) -> int:
        return len(self.required_fields)
