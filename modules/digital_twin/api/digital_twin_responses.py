"""Response envelope for the Digital Twin API."""
from __future__ import annotations

from dataclasses import dataclass, field

HTTP_OK = 200
HTTP_BAD_REQUEST = 400
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404
HTTP_INTERNAL_ERROR = 500


@dataclass(slots=True)
class ApiResponse:
    """Uniform response shape returned by every API endpoint."""

    ok: bool
    data: dict[str, object] = field(default_factory=dict)
    error: str = ""
    status_code: int = HTTP_OK

    def to_dict(self) -> dict[str, object]:
        return {
            "ok": self.ok,
            "data": self.data,
            "error": self.error,
            "status_code": self.status_code,
        }

    @classmethod
    def success(cls, data: dict[str, object] | None = None) -> "ApiResponse":
        return cls(ok=True, data=data or {})

    @classmethod
    def failure(
        cls, message: str, status_code: int = HTTP_BAD_REQUEST
    ) -> "ApiResponse":
        return cls(ok=False, error=message, status_code=status_code)

    @classmethod
    def forbidden(cls, message: str = "permission denied") -> "ApiResponse":
        return cls.failure(message, HTTP_FORBIDDEN)

    @classmethod
    def not_found(cls, message: str = "endpoint not found") -> "ApiResponse":
        return cls.failure(message, HTTP_NOT_FOUND)

    @classmethod
    def internal(cls, message: str = "internal error") -> "ApiResponse":
        return cls.failure(message, HTTP_INTERNAL_ERROR)
