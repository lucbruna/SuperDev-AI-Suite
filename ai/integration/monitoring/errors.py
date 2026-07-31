"""
Error Monitor - Error tracking
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ErrorSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ErrorRecord:
    error_id: str
    integration_id: str
    error_type: str
    message: str
    severity: ErrorSeverity = ErrorSeverity.MEDIUM
    stack_trace: str = ""
    occurred_at: datetime = field(default_factory=datetime.now)
    resolved: bool = False


class ErrorMonitor:
    def __init__(self):
        self.errors: dict[str, list[ErrorRecord]] = {}
        self.error_counts: dict[str, int] = {}

    def record_error(
        self,
        integration_id: str,
        error_type: str,
        message: str,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        stack_trace: str = "",
    ) -> ErrorRecord:
        error_id = f"err_{integration_id}_{len(self.errors.get(integration_id, []))}"
        error = ErrorRecord(
            error_id=error_id,
            integration_id=integration_id,
            error_type=error_type,
            message=message,
            severity=severity,
            stack_trace=stack_trace,
        )
        self.errors.setdefault(integration_id, []).append(error)
        self.error_counts[integration_id] = self.error_counts.get(integration_id, 0) + 1
        return error

    def resolve_error(self, error_id: str) -> bool:
        for errors in self.errors.values():
            for error in errors:
                if error.error_id == error_id:
                    error.resolved = True
                    return True
        return False

    def get_errors(self, integration_id: str, severity: ErrorSeverity = None) -> list[ErrorRecord]:
        errors = self.errors.get(integration_id, [])
        if severity:
            errors = [e for e in errors if e.severity == severity]
        return errors

    def get_error_count(self, integration_id: str) -> int:
        return self.error_counts.get(integration_id, 0)

    def get_unresolved(self, integration_id: str = None) -> list[ErrorRecord]:
        if integration_id:
            return [e for e in self.errors.get(integration_id, []) if not e.resolved]
        all_errors = []
        for errors in self.errors.values():
            all_errors.extend([e for e in errors if not e.resolved])
        return all_errors

    def count(self) -> int:
        return sum(len(v) for v in self.errors.values())
