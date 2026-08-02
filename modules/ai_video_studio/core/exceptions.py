"""Exception hierarchy for the AI Video Studio.

Every exception carries a structured error_code and optional context dict
so that API handlers can serialise them into consistent JSON responses.
"""
from __future__ import annotations
from typing import Any


class VideoStudioError(Exception):
    """Base exception for the entire video studio module."""

    error_code: str = "VIDEOSTUDIO_ERROR"
    status_code: int = 500

    def __init__(
        self,
        message: str = "An unexpected video studio error occurred",
        *,
        context: dict[str, Any] | None = None,
        cause: Exception | None = None,
    ):
        self.message = message
        self.context = context or {}
        self.cause = cause
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "error": self.error_code,
            "message": self.message,
        }
        if self.context:
            result["context"] = self.context
        return result


# ── Validation errors ─────────────────────────────────────────────
class ValidationError(VideoStudioError):
    error_code = "VALIDATION_ERROR"
    status_code = 400

    def __init__(self, message: str = "Validation failed", *, field: str | None = None, **kw: Any):
        ctx = kw.pop("context", {})
        if field:
            ctx["field"] = field
        super().__init__(message, context=ctx, **kw)


# ── Database errors ───────────────────────────────────────────────
class DatabaseError(VideoStudioError):
    error_code = "DATABASE_ERROR"
    status_code = 500


class NotFoundError(DatabaseError):
    error_code = "NOT_FOUND"
    status_code = 404

    def __init__(self, resource: str, resource_id: str, **kw: Any):
        super().__init__(
            f"{resource} with id '{resource_id}' not found",
            context={"resource": resource, "id": resource_id},
            **kw,
        )


# ── Rendering errors ──────────────────────────────────────────────
class RenderingError(VideoStudioError):
    error_code = "RENDERING_ERROR"
    status_code = 500


class FFmpegError(RenderingError):
    error_code = "FFMPEG_ERROR"

    def __init__(self, command: str, stderr: str, **kw: Any):
        super().__init__(
            f"FFmpeg command failed",
            context={"command": command, "stderr": stderr[:500]},
            **kw,
        )


class GPUError(RenderingError):
    error_code = "GPU_ERROR"
    status_code = 503

    def __init__(self, message: str = "GPU unavailable or failed", **kw: Any):
        super().__init__(message, **kw)


class EncodingError(RenderingError):
    error_code = "ENCODING_ERROR"

    def __init__(self, codec: str, reason: str, **kw: Any):
        super().__init__(
            f"Encoding with {codec} failed: {reason}",
            context={"codec": codec, "reason": reason},
            **kw,
        )


# ── Pipeline errors ───────────────────────────────────────────────
class PipelineError(VideoStudioError):
    error_code = "PIPELINE_ERROR"
    status_code = 500

    def __init__(self, pipeline_name: str, message: str = "Pipeline failed", **kw: Any):
        super().__init__(
            message,
            context={"pipeline": pipeline_name, **kw.pop("context", {})},
            **kw,
        )


class PipelineTimeoutError(PipelineError):
    error_code = "PIPELINE_TIMEOUT"
    status_code = 504


# ── Asset errors ──────────────────────────────────────────────────
class AssetError(VideoStudioError):
    error_code = "ASSET_ERROR"
    status_code = 400


class AssetNotFoundError(NotFoundError):
    error_code = "ASSET_NOT_FOUND"

    def __init__(self, asset_id: str, **kw: Any):
        super().__init__("Asset", asset_id, **kw)


class AssetTooLargeError(AssetError):
    error_code = "ASSET_TOO_LARGE"

    def __init__(self, size_mb: float, max_mb: float, **kw: Any):
        super().__init__(
            f"Asset size {size_mb:.1f}MB exceeds limit of {max_mb:.0f}MB",
            context={"size_mb": size_mb, "max_mb": max_mb},
            **kw,
        )


# ── Export errors ─────────────────────────────────────────────────
class ExportError(VideoStudioError):
    error_code = "EXPORT_ERROR"
    status_code = 500


class ExportFormatError(ExportError):
    error_code = "EXPORT_FORMAT_ERROR"

    def __init__(self, format: str, reason: str, **kw: Any):
        super().__init__(
            f"Export format '{format}' error: {reason}",
            context={"format": format, "reason": reason},
            **kw,
        )


class ExportQuotaError(ExportError):
    error_code = "EXPORT_QUOTA_EXCEEDED"
    status_code = 429


# ── API errors ────────────────────────────────────────────────────
class APIError(VideoStudioError):
    error_code = "API_ERROR"
    status_code = 502

    def __init__(self, service: str, status: int, body: str, **kw: Any):
        super().__init__(
            f"External API {service} returned {status}",
            context={"service": service, "status": status, "body": body[:500]},
            **kw,
        )


class RateLimitError(APIError):
    error_code = "RATE_LIMIT"
    status_code = 429


# ── AI errors ─────────────────────────────────────────────────────
class AIError(VideoStudioError):
    error_code = "AI_ERROR"
    status_code = 500


class AITimeoutError(AIError):
    error_code = "AI_TIMEOUT"
    status_code = 504


class AIQuotaError(AIError):
    error_code = "AI_QUOTA_EXCEEDED"
    status_code = 429


# ── Storage errors ────────────────────────────────────────────────
class StorageError(VideoStudioError):
    error_code = "STORAGE_ERROR"
    status_code = 500


class StorageFullError(StorageError):
    error_code = "STORAGE_FULL"
    status_code = 507


# ── Auth errors ───────────────────────────────────────────────────
class AuthenticationError(VideoStudioError):
    error_code = "AUTH_ERROR"
    status_code = 401


class AuthorizationError(VideoStudioError):
    error_code = "FORBIDDEN"
    status_code = 403