"""Interfaces for the DevOps & Cloud Infrastructure Engine (Volume 37)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from devops_engine.devops_models import (Container, Deployment, Incident,
                                         Pipeline, Resource, Server)


class CloudProviderAPI(ABC):
    """Provisioning and teardown of cloud servers."""

    @abstractmethod
    def provision(self, server: Server) -> bool: ...

    @abstractmethod
    def terminate(self, server: Server) -> bool: ...


class ContainerRuntime(ABC):
    """Start and stop container instances."""

    @abstractmethod
    def start(self, container: Container) -> bool: ...

    @abstractmethod
    def stop(self, container: Container) -> bool: ...


class ClusterOrchestrator(ABC):
    """Roll out deployments to a cluster."""

    @abstractmethod
    def deploy(self, deployment: Deployment) -> dict[str, Any]: ...


class PipelineRunner(ABC):
    """Execute a CI/CD pipeline."""

    @abstractmethod
    def run(self, pipeline: Pipeline) -> dict[str, Any]: ...


class HealthChecker(ABC):
    """Probe a target and return a health result."""

    @abstractmethod
    def check(self, target: str) -> dict[str, Any]: ...


class LogCollector(ABC):
    """Collect log entries from a source."""

    @abstractmethod
    def collect(self, source: str) -> list[dict[str, Any]]: ...


class BackupScheduler(ABC):
    """Execute a backup job."""

    @abstractmethod
    def run(self, job: Any) -> dict[str, Any]: ...


class DisasterRecovery(ABC):
    """Drive an incident through detection to recovery."""

    @abstractmethod
    def recover(self, incident: Incident) -> dict[str, Any]: ...


class AutoScaler(ABC):
    """Apply a scaling decision for a policy."""

    @abstractmethod
    def scale(self, policy: Any, current: int, target: int) -> bool: ...


class CostOptimizer(ABC):
    """Analyze resources and produce cost recommendations."""

    @abstractmethod
    def optimize(self, resources: list[Resource]) -> list[dict[str, Any]]: ...
