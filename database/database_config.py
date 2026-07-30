from __future__ import annotations

import json
import os
from typing import Any

from .database_logger import DatabaseLogger
from .database_models import ConnectionConfig, DatabaseConfig, DatabaseType, PoolConfig, PoolStrategy


class DatabaseConfigManager:
    """Configuration management for database connections."""

    def __init__(self, logger: DatabaseLogger | None = None) -> None:
        self._config = DatabaseConfig()
        self._logger = logger or DatabaseLogger("database.config")

    def load_from_dict(self, data: dict[str, Any]) -> DatabaseConfig:
        cfg = DatabaseConfig()
        cfg.default_driver = data.get("default_driver", "postgresql")
        cfg.migrations_dir = data.get("migrations_dir", "migrations")
        cfg.enable_metrics = data.get("enable_metrics", True)
        cfg.enable_health = data.get("enable_health", True)
        cfg.log_queries = data.get("log_queries", False)
        cfg.slow_query_threshold_ms = data.get("slow_query_threshold_ms", 1000.0)

        for name, conn_data in data.get("connections", {}).items():
            cfg.connections[name] = self._parse_connection(name, conn_data)

        for name, pool_data in data.get("pools", {}).items():
            cfg.pools[name] = self._parse_pool(pool_data)

        self._config = cfg
        self._logger.info(f"Loaded config: {len(cfg.connections)} connections, {len(cfg.pools)} pools")
        return cfg

    def load_from_json(self, path: str) -> DatabaseConfig:
        if not os.path.exists(path):
            self._logger.error(f"Config file not found: {path}")
            return self._config
        with open(path) as f:
            data = json.load(f)
        return self.load_from_dict(data)

    def load_from_env(self, prefix: str = "DB_") -> DatabaseConfig:
        data: dict[str, Any] = {
            "connections": {},
            "pools": {},
        }
        for key, value in os.environ.items():
            if not key.startswith(prefix):
                continue
            parts = key[len(prefix) :].lower().split("_", 2)
            if len(parts) == 3:
                conn_name, field = parts[0], parts[2]
                if conn_name not in data["connections"]:
                    data["connections"][conn_name] = {}
                data["connections"][conn_name][field] = value
            elif len(parts) == 1 and parts[0] == "DEFAULT":
                data["default_driver"] = value.lower()
        return self.load_from_dict(data)

    def get_config(self) -> DatabaseConfig:
        return self._config

    def get_connection(self, name: str) -> ConnectionConfig | None:
        return self._config.connections.get(name)

    def get_pool(self, name: str) -> PoolConfig | None:
        return self._config.pools.get(name)

    def add_connection(self, name: str, config: ConnectionConfig) -> None:
        self._config.connections[name] = config

    def add_pool(self, name: str, config: PoolConfig) -> None:
        self._config.pools[name] = config

    def _parse_connection(self, name: str, data: dict[str, Any]) -> ConnectionConfig:
        return ConnectionConfig(
            dsn=data.get("dsn", ""),
            host=data.get("host", "localhost"),
            port=int(data.get("port", 5432)),
            database=data.get("database", ""),
            username=data.get("username", ""),
            password=data.get("password", ""),
            timeout=float(data.get("timeout", 30.0)),
            ssl=bool(data.get("ssl", False)),
            options=data.get("options", {}),
            driver_type=DatabaseType(data.get("driver_type", "postgresql")),
        )

    def _parse_pool(self, data: dict[str, Any]) -> PoolConfig:
        return PoolConfig(
            min_size=int(data.get("min_size", 2)),
            max_size=int(data.get("max_size", 10)),
            strategy=PoolStrategy(data.get("strategy", "dynamic")),
            acquire_timeout=float(data.get("acquire_timeout", 30.0)),
            max_idle_time=float(data.get("max_idle_time", 300.0)),
            max_lifetime=float(data.get("max_lifetime", 3600.0)),
            validation_query=data.get("validation_query", "SELECT 1"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "default_driver": self._config.default_driver,
            "connections": {k: v.__dict__ for k, v in self._config.connections.items()},
            "pools": {k: v.__dict__ for k, v in self._config.pools.items()},
            "migrations_dir": self._config.migrations_dir,
            "enable_metrics": self._config.enable_metrics,
        }
