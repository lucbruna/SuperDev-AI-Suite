"""Factory for the DevOps & Cloud Infrastructure Engine (Volume 37)."""

from __future__ import annotations

from typing import Any

from devops_engine.backup.backup_engine import BackupEngine
from devops_engine.cicd.cicd_engine import CicdEngine
from devops_engine.cloud.cloud_engine import CloudEngine
from devops_engine.containers.container_engine import ContainerEngine
from devops_engine.cost_optimizer.cost_engine import CostEngine
from devops_engine.devops_config import DevopsConfig
from devops_engine.devops_context import DevopsContext
from devops_engine.devops_engine import DevopsEngine
from devops_engine.devops_events import DevopsEvents
from devops_engine.devops_metrics import DevopsMetrics
from devops_engine.devops_registry import DevopsRegistry
from devops_engine.devops_runtime import DevopsRuntime
from devops_engine.devops_security import DevopsSecurity
from devops_engine.kubernetes.kube_engine import KubeEngine
from devops_engine.logging.logging_engine import LoggingEngine
from devops_engine.monitoring.monitoring_engine import MonitoringEngine
from devops_engine.recovery.recovery_engine import RecoveryEngine
from devops_engine.scaling.scaling_engine import ScalingEngine


def build_devops_engine(config: dict[str, Any] | None = None) -> DevopsEngine:
    """Builds a fully wired DevopsEngine with core services and all
    ten subpackage engines attached to a shared events/metrics bus."""
    cfg = DevopsConfig(config or {})
    registry = DevopsRegistry()
    events = DevopsEvents()
    metrics = DevopsMetrics()
    security = DevopsSecurity(
        approval_threshold=cfg.approval_threshold)
    context = DevopsContext(cfg)
    runtime = DevopsRuntime()
    engine = DevopsEngine(config=cfg, events=events, metrics=metrics,
                          registry=registry, security=security,
                          context=context, runtime=runtime)

    subsystems = {
        "cloud_engine": CloudEngine(cfg, events, metrics, security),
        "container_engine": ContainerEngine(cfg, events, metrics),
        "kube_engine": KubeEngine(cfg, events, metrics, security),
        "cicd_engine": CicdEngine(cfg, events, metrics, security),
        "monitoring_engine": MonitoringEngine(cfg, events, metrics),
        "logging_engine": LoggingEngine(cfg, events, metrics),
        "backup_engine": BackupEngine(cfg, events, metrics),
        "recovery_engine": RecoveryEngine(cfg, events, metrics),
        "scaling_engine": ScalingEngine(cfg, events, metrics),
        "cost_engine": CostEngine(cfg, events, metrics),
    }
    for name, subsystem in subsystems.items():
        engine.attach_subsystem(name, subsystem)
    return engine
