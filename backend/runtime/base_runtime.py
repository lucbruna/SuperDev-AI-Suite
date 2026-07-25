from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import AsyncIterator, Any


class RuntimeStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class Language(str, Enum):
    PYTHON = "python"
    NODEJS = "nodejs"
    GO = "go"
    RUST = "rust"
    SHELL = "shell"
    BASH = "bash"


@dataclass
class ResourceLimits:
    max_memory_mb: int = 512
    max_cpu_percent: float = 50.0
    max_execution_time_seconds: int = 300
    max_output_size_bytes: int = 10 * 1024 * 1024
    max_disk_mb: int = 1024


@dataclass
class ExecutionResult:
    run_id: str
    status: RuntimeStatus
    stdout: str = ""
    stderr: str = ""
    exit_code: int | None = None
    execution_time_ms: float = 0.0
    memory_used_mb: float = 0.0
    error: str | None = None
    artifacts: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class RuntimeConfig:
    language: Language
    code: str
    filename: str | None = None
    entry_point: str | None = None
    dependencies: list[str] = field(default_factory=list)
    env_vars: dict[str, str] = field(default_factory=dict)
    resource_limits: ResourceLimits = field(default_factory=ResourceLimits)
    working_directory: str | None = None
    network_access: bool = False


class BaseRuntime(ABC):
    """Abstract base class for code execution runtimes."""

    @property
    @abstractmethod
    def language(self) -> Language:
        ...

    @property
    @abstractmethod
    def supported_extensions(self) -> list[str]:
        ...

    @abstractmethod
    async def execute(
        self,
        config: RuntimeConfig,
        run_id: str,
    ) -> ExecutionResult:
        ...

    @abstractmethod
    async def stream(
        self,
        config: RuntimeConfig,
        run_id: str,
    ) -> AsyncIterator[str]:
        ...

    async def health_check(self) -> bool:
        return True

    async def close(self) -> None:
        pass
