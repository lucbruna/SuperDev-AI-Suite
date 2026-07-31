"""DevOps Engine facade (Volume 37).

Aggregate facade over the DevOps subsystems, exposing subsystem engines
lazily via ``engine.cloud_engine`` once attached.
"""

from __future__ import annotations

from typing import Any

from devops_engine.devops_config import DevopsConfig
from devops_engine.devops_context import DevopsContext
from devops_engine.devops_events import DevopsEvents
from devops_engine.devops_logger import get_logger
from devops_engine.devops_manager import DevopsManager
from devops_engine.devops_metrics import DevopsMetrics
from devops_engine.devops_models import (Server, Deployment, Pipeline,
                                         HealthCheckResult, HealthStatus,
                                         BackupJob, RestoreJob, Incident,
                                         CostRecord, Severity)
from devops_engine.devops_registry import DevopsRegistry
from devops_engine.devops_runtime import DevopsRuntime
from devops_engine.devops_security import DevopsSecurity


class DevopsEngine:
    """Aggregate facade over the DevOps subsystems."""

    def __init__(self, config: DevopsConfig | None = None,
                 events: DevopsEvents | None = None,
                 metrics: DevopsMetrics | None = None,
                 registry: DevopsRegistry | None = None,
                 security: DevopsSecurity | None = None,
                 context: DevopsContext | None = None,
                 runtime: DevopsRuntime | None = None) -> None:
        self._log = get_logger()
        self.config = config or DevopsConfig()
        self.events = events or DevopsEvents()
        self.metrics = metrics or DevopsMetrics()
        self.registry = registry or DevopsRegistry()
        self.security = security or DevopsSecurity(
            approval_threshold=self.config.approval_threshold)
        self.context = context or DevopsContext()
        self.runtime = runtime or DevopsRuntime()
        self.manager = DevopsManager(
            registry=self.registry, events=self.events, metrics=self.metrics,
            config=self.config, context=self.context, security=self.security,
            engine=self)
        self._subsystems: dict[str, Any] = {}

    # -- lifecycle ----------------------------------------------------------
    def start(self) -> bool:
        return self.runtime.start()

    def stop(self) -> bool:
        return self.runtime.stop()

    def run(self) -> bool:
        return self.start()

    # -- subsystem attachment ----------------------------------------------
    def attach_subsystem(self, name: str, engine: Any) -> None:
        self._subsystems[name] = engine
        setattr(self, name, engine)
        setattr(self.manager, name, engine)

    def __getattr__(self, name: str) -> Any:
        if name in self._subsystems:
            return self._subsystems[name]
        raise AttributeError(f"no subsystem or attribute '{name}'")

    # -- provisioning facade -------------------------------------------------
    def provision_server(self, name: str, cpu: int = 0,
                         memory_gb: int = 0) -> Server:
        return self.manager.provision_server(name, cpu, memory_gb)

    def list_servers(self) -> list[Server]:
        return self.manager.list_servers()

    def terminate_server(self, server_id: str, actor: str) -> bool:
        return self.manager.terminate_server(server_id, actor)

    # -- deploy / pipeline facade -------------------------------------------
    def deploy(self, name: str, image: str, replicas: int = 1,
               cluster_id: str = "") -> Deployment:
        return self.manager.deploy(name, image, replicas, cluster_id)

    def create_pipeline(self, name: str, steps: list[str] | None = None
                        ) -> Pipeline:
        return self.manager.create_pipeline(name, steps)

    def run_pipeline(self, pipeline_id: str) -> bool:
        return self.manager.run_pipeline(pipeline_id)

    # -- observability facade -----------------------------------------------
    def check_health(self, target: str,
                     status: HealthStatus | None = None,
                     latency_ms: float = 10.0) -> HealthCheckResult:
        return self.manager.check_health(target,
                                         status or HealthStatus.HEALTHY,
                                         latency_ms)

    def collect_log(self, source: str, message: str,
                    level: str = "info"):
        return self.manager.collect_log(source, message, level)

    # -- backup / recovery facade -------------------------------------------
    def start_backup(self, target: str) -> BackupJob:
        return self.manager.start_backup(target)

    def restore(self, backup_id: str, target: str = "") -> RestoreJob:
        return self.manager.restore(backup_id, target)

    def raise_incident(self, title: str,
                       severity: Severity = Severity.WARNING,
                       source: str = "core") -> Incident:
        return self.manager.raise_incident(title, severity, source)

    def resolve_incident(self, incident_id: str) -> bool:
        return self.manager.resolve_incident(incident_id)

    # -- misc ---------------------------------------------------------------
    def record_cost(self, resource: str, amount: float,
                    period: str = "") -> CostRecord:
        return self.manager.record_cost(resource, amount, period)

    def stats(self) -> dict[str, Any]:
        return {
            "manager": self.manager.stats(),
            "subsystems": list(self._subsystems),
            "runtime": self.runtime.state(),
        }
