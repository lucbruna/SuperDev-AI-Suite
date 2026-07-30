from __future__ import annotations

import os
from typing import Any

from .api_models import APIConfig


class APIConfigManager:
    """Manages API configuration with env override support."""

    def __init__(self) -> None:
        self._config = APIConfig()
        self._load_from_env()

    def _load_from_env(self) -> None:
        self._config.host = os.getenv("API_HOST", self._config.host)
        self._config.port = int(os.getenv("API_PORT", str(self._config.port)))
        self._config.debug = os.getenv("API_DEBUG", str(self._config.debug)).lower() in ("true", "1", "yes")
        self._config.jwt_secret = os.getenv("JWT_SECRET", self._config.jwt_secret)
        self._config.jwt_algorithm = os.getenv("JWT_ALGORITHM", self._config.jwt_algorithm)
        self._config.jwt_expiry_minutes = int(os.getenv("JWT_EXPIRY_MINUTES", str(self._config.jwt_expiry_minutes)))
        self._config.rate_limit_default = int(os.getenv("RATE_LIMIT_DEFAULT", str(self._config.rate_limit_default)))
        self._config.log_level = os.getenv("API_LOG_LEVEL", self._config.log_level)
        self._config.max_request_size_mb = int(os.getenv("API_MAX_REQUEST_SIZE_MB", str(self._config.max_request_size_mb)))
        self._config.request_timeout_sec = int(os.getenv("API_REQUEST_TIMEOUT_SEC", str(self._config.request_timeout_sec)))
        self._config.enable_docs = os.getenv("API_ENABLE_DOCS", str(self._config.enable_docs)).lower() in ("true", "1", "yes")
        self._config.enable_metrics = os.getenv("API_ENABLE_METRICS", str(self._config.enable_metrics)).lower() in ("true", "1", "yes")

        cors_origins = os.getenv("API_CORS_ORIGINS", "")
        if cors_origins:
            self._config.cors_origins = [o.strip() for o in cors_origins.split(",")]

        allowed_hosts = os.getenv("API_ALLOWED_HOSTS", "")
        if allowed_hosts:
            self._config.allowed_hosts = [h.strip() for h in allowed_hosts.split(",")]

    @property
    def config(self) -> APIConfig:
        return self._config

    def update(self, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)

    def to_dict(self) -> dict[str, Any]:
        return {k: str(v) if isinstance(v, (list,)) else v for k, v in self._config.__dict__.items() if not k.startswith("_")}
