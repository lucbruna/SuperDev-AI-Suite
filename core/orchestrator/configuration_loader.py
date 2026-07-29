"""Configuration Loader — structured configuration for the SuperDev platform.

Loads configuration from files (JSON, YAML, TOML), environment variables,
and CLI arguments with proper validation and merging.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, ValidationError

from .exceptions import OrchestratorError


class DatabaseConfig(BaseModel):
    url: str = Field(default="postgresql+asyncpg://superdev:superdev@localhost:5432/superdev")
    pool_size: int = Field(default=10, ge=1)
    max_overflow: int = Field(default=20, ge=0)
    echo: bool = Field(default=False)
    migrate_on_boot: bool = Field(default=True)


class RedisConfig(BaseModel):
    host: str = Field(default="localhost")
    port: int = Field(default=6379, ge=1, le=65535)
    password: str = Field(default="")
    db: int = Field(default=0, ge=0, le=16)
    decode_responses: bool = Field(default=True)


class AuthConfig(BaseModel):
    secret_key: str = Field(default="superdev-secret-key-change-in-production")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30, ge=1)
    refresh_token_expire_days: int = Field(default=7, ge=1)
    mfa_enabled: bool = Field(default=False)


class AIConfig(BaseModel):
    default_model: str = Field(default="gpt-4")
    default_provider: str = Field(default="openai")
    max_tokens: int = Field(default=4096, ge=1)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    timeout_seconds: int = Field(default=60, ge=1)


class PluginConfig(BaseModel):
    enabled: bool = Field(default=True)
    allow_unsigned: bool = Field(default=False)
    max_plugins: int = Field(default=50, ge=0)
    sandbox_enabled: bool = Field(default=True)


class MonitoringConfig(BaseModel):
    metrics_enabled: bool = Field(default=True)
    tracing_enabled: bool = Field(default=True)
    health_check_interval: int = Field(default=30, ge=1)
    export_otlp: bool = Field(default=False)
    otlp_endpoint: str = Field(default="")


class ServerConfig(BaseModel):
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000, ge=1, le=65535)
    workers: int = Field(default=1, ge=1)
    reload: bool = Field(default=False)
    cors_origins: list[str] = Field(default=["*"])
    docs_url: str = Field(default="/docs")
    root_path: str = Field(default="")


class OrchestratorConfig(BaseModel):
    """Complete configuration for the SuperDev platform."""
    environment: str = Field(default="development")
    version: str = Field(default="5.0.0")
    debug: bool = Field(default=False)
    state_path: str = Field(default="")
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    auth: AuthConfig = Field(default_factory=AuthConfig)
    ai: AIConfig = Field(default_factory=AIConfig)
    plugins: PluginConfig = Field(default_factory=PluginConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    server: ServerConfig = Field(default_factory=ServerConfig)


class ConfigurationLoader:
    """Loads and validates platform configuration from multiple sources.

    Priority (highest wins):
    1. CLI arguments / explicit overrides
    2. Environment variables (SUPERDEV_*)
    3. Config file (JSON/YAML)
    4. Default values
    """

    def __init__(self) -> None:
        self._config: OrchestratorConfig | None = None
        self._loaded_from: str = "defaults"

    async def load(
        self,
        config_path: str = "",
        overrides: dict[str, Any] | None = None,
    ) -> OrchestratorConfig:
        """Load and merge configuration from all sources."""
        base = OrchestratorConfig()

        # 1. Load from file if provided
        if config_path:
            base = self._load_from_file(config_path, base)
            self._loaded_from = config_path

        # 2. Override from environment
        base = self._load_from_env(base)

        # 3. Override from explicit overrides
        if overrides:
            base = self._merge_dict(base, overrides)
            self._loaded_from = f"{self._loaded_from} + overrides"

        # Validate
        try:
            self._config = OrchestratorConfig(**base.model_dump())
        except ValidationError as e:
            raise OrchestratorError(f"Configuration validation failed: {e}")

        # Set environment from config
        os.environ.setdefault("SUPERDEV_ENV", self._config.environment)

        return self._config

    def _load_from_file(
        self, path: str, base: OrchestratorConfig,
    ) -> OrchestratorConfig:
        """Load configuration from a JSON file."""
        p = Path(path)
        if not p.exists():
            raise OrchestratorError(f"Configuration file not found: {path}")

        try:
            with open(p) as f:
                data = json.load(f)
            return self._merge_dict(base, data)
        except json.JSONDecodeError as e:
            raise OrchestratorError(f"Invalid JSON in config file: {e}")

    def _load_from_env(self, config: OrchestratorConfig) -> OrchestratorConfig:
        """Override configuration from environment variables (SUPERDEV_*)."""
        mapping = {
            "SUPERDEV_ENV": ("environment", str),
            "SUPERDEV_DEBUG": ("debug", bool),
            "SUPERDEV_DB_URL": ("database", "url", str),
            "SUPERDEV_DB_POOL_SIZE": ("database", "pool_size", int),
            "SUPERDEV_REDIS_HOST": ("redis", "host", str),
            "SUPERDEV_REDIS_PORT": ("redis", "port", int),
            "SUPERDEV_REDIS_PASSWORD": ("redis", "password", str),
            "SUPERDEV_AUTH_SECRET": ("auth", "secret_key", str),
            "SUPERDEV_AI_MODEL": ("ai", "default_model", str),
            "SUPERDEV_AI_PROVIDER": ("ai", "default_provider", str),
            "SUPERDEV_SERVER_PORT": ("server", "port", int),
            "SUPERDEV_SERVER_HOST": ("server", "host", str),
            "SUPERDEV_METRICS_ENABLED": ("monitoring", "metrics_enabled", bool),
        }

        for env_var, *path_and_type in mapping.items():
            value = os.environ.get(env_var)
            if value is None:
                continue

            # Parse the path and type from the mapping
            *attr_path, type_func = path_and_type
            typed_value = self._cast(value, type_func)

            # Navigate to the correct nested attribute
            current = config
            for attr in attr_path:
                if hasattr(current, attr):
                    current = getattr(current, attr)
                else:
                    break
            else:
                if hasattr(current, attr_path[-1]):
                    setattr(current, attr_path[-1], typed_value)

        return config

    def _cast(self, value: str, type_func: type) -> Any:
        """Cast a string to the target type."""
        if type_func == bool:
            return value.lower() in ("true", "1", "yes")
        return type_func(value)

    def _merge_dict(self, config: OrchestratorConfig, data: dict) -> OrchestratorConfig:
        """Recursively merge a dict into a pydantic model."""
        merged = config.model_dump()
        self._deep_merge(merged, data)
        return OrchestratorConfig(**merged)

    def _deep_merge(self, base: dict, override: dict) -> None:
        """Recursively merge override into base dict."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value

    def get(self) -> OrchestratorConfig:
        """Get the loaded configuration. Raises if not loaded yet."""
        if self._config is None:
            raise OrchestratorError("Configuration not loaded yet. Call load() first.")
        return self._config

    @property
    def is_loaded(self) -> bool:
        return self._config is not None

    def get_loaded_from(self) -> str:
        return self._loaded_from
