"""Manager for the DevOps & Cloud Infrastructure Engine (Volume 37)."""

from __future__ import annotations

import time
from typing import Any

from devops_engine.devops_config import DevopsConfig
from devops_engine.devops_context import DevopsContext
from devops_engine.devops_events import (DevopsEventType, DevopsEvents)
from devops_engine.devops_metrics import DevopsMetrics
from devops_engine.devops_models import (BackupJob, BackupStatus, Build,
                                         BuildStatus, Cluster, ClusterStatus,
                                         Container, ContainerStatus,
                                         CostRecord, Deployment,
                                         DeploymentStatus, HealthCheckResult,
                                         HealthStatus, Incident, IncidentStatus,
                                         LogEntry, MetricSample, Pipeline,
                                         PipelineStatus, Release,
                                         ReleaseStatus, Resource,
                                         ResourceStatus, RestoreJob,
                                         RestoreStatus, RiskLevel, Server,
                                         Severity, Snapshot)
from devops_engine.devops_protocols import new_id
from devops_engine.devops_registry import DevopsRegistry
from devops_engine.devops_security import DevopsSecurity


class DevopsManager:
    """Core operations: provisioning, deploys, pipelines, health, backups,
    restores, incidents and cost records."""

    def __init__(self, registry: DevopsRegistry,
                 events: DevopsEvents,
                 metrics: DevopsMetrics,
                 config: DevopsConfig,
                 context: DevopsContext,
                 security: DevopsSecurity,
                 engine: Any = None) -> None:
        self.registry = registry
        self.events = events
        self.metrics = metrics
        self.config = config
        self.context = context
        self.security = security
        self.engine = engine

    # -- servers / resources -------------------------------------------------
    def provision_server(self, name: str, cpu: int = 0,
                         memory_gb: int = 0) -> Server:
        server = Server(
            server_id=new_id("server"), name=name,
            provider=self.config.provider,
            region=self.config.region,
            cpu=cpu or self.config.default_cpu,
            memory_gb=memory_gb or self.config.default_memory_gb,
            status=ResourceStatus.RUNNING, created_at=time.time())
        self.registry.register_server(server)
        self.metrics.increment("devops.servers")
        self.events.publish(DevopsEventType.RESOURCE_PROVISIONED,
                            {"server_id": server.server_id, "name": name})
        return server

    def get_server(self, server_id: str) -> Server | None:
        return self.registry.get_server(server_id)

    def list_servers(self) -> list[Server]:
        return self.registry.list_servers()

    def terminate_server(self, server_id: str, actor: str) -> bool:
        server = self.registry.get_server(server_id)
        if server is None:
            return False
        if not self.security.approve(actor):
            self.security.audit_deny(actor, server_id)
            return False
        server.status = ResourceStatus.TERMINATED
        self.metrics.increment("devops.servers", -1)
        self.events.publish(DevopsEventType.RESOURCE_TERMINATED,
                            {"server_id": server_id, "actor": actor})
        return True

    def register_resource(self, resource: Resource) -> Resource:
        self.registry.register_resource(resource)
        self.metrics.increment("devops.resources")
        return resource

    # -- containers ----------------------------------------------------------
    def register_container(self, container: Container) -> Container:
        self.registry.register_container(container)
        self.metrics.increment("devops.containers")
        self.events.publish(DevopsEventType.CONTAINER_CREATED,
                            {"container_id": container.container_id})
        return container

    def list_containers(self) -> list[Container]:
        return self.registry.list_containers()

    def set_container_status(self, container_id: str,
                             status: ContainerStatus) -> bool:
        container = self.registry.get_container(container_id)
        if container is None:
            return False
        container.status = status
        return True

    # -- deployments ---------------------------------------------------------
    def deploy(self, name: str, image: str, replicas: int = 1,
               cluster_id: str = "") -> Deployment:
        deployment = Deployment(
            deployment_id=new_id("deployment"), name=name,
            cluster_id=cluster_id, image=image,
            replicas=replicas, desired=replicas,
            status=DeploymentStatus.COMPLETED, created_at=time.time())
        self.registry.register_deployment(deployment)
        self.metrics.increment("devops.deployments")
        self.events.publish(DevopsEventType.DEPLOYMENT_CREATED,
                            {"deployment_id": deployment.deployment_id})
        self.events.publish(DevopsEventType.DEPLOYMENT_COMPLETED,
                            {"deployment_id": deployment.deployment_id})
        return deployment

    def list_deployments(self) -> list[Deployment]:
        return self.registry.list_deployments()

    # -- pipelines / builds / releases ----------------------------------------
    def create_pipeline(self, name: str,
                        steps: list[str] | None = None) -> Pipeline:
        pipeline = Pipeline(
            pipeline_id=new_id("pipeline"), name=name,
            status=PipelineStatus.PENDING, steps=list(steps or []),
            created_at=time.time())
        self.registry.register_pipeline(pipeline)
        return pipeline

    def run_pipeline(self, pipeline_id: str) -> bool:
        pipeline = self.registry.get_pipeline(pipeline_id)
        if pipeline is None:
            return False
        pipeline.status = PipelineStatus.RUNNING
        pipeline.started_at = time.time()
        self.events.publish(DevopsEventType.PIPELINE_STARTED,
                            {"pipeline_id": pipeline_id})
        build = Build(build_id=new_id("build"), pipeline_id=pipeline_id,
                      status=BuildStatus.BUILDING, created_at=time.time())
        self.registry.register_build(build)
        build.status = BuildStatus.SUCCEEDED
        pipeline.status = PipelineStatus.SUCCEEDED
        pipeline.finished_at = time.time()
        self.metrics.increment("devops.builds")
        self.events.publish(DevopsEventType.BUILD_SUCCEEDED,
                            {"build_id": build.build_id})
        self.events.publish(DevopsEventType.PIPELINE_SUCCEEDED,
                            {"pipeline_id": pipeline_id})
        return True

    def release(self, pipeline_id: str, version: str = "1.0.0") -> Release:
        release = Release(
            release_id=new_id("release"), pipeline_id=pipeline_id,
            version=version, status=ReleaseStatus.DEPLOYED,
            deployed_at=time.time())
        self.registry.register_release(release)
        self.events.publish(DevopsEventType.RELEASE_DEPLOYED,
                            {"release_id": release.release_id,
                             "version": version})
        return release

    # -- observability --------------------------------------------------------
    def check_health(self, target: str,
                     status: HealthStatus = HealthStatus.HEALTHY,
                     latency_ms: float = 10.0) -> HealthCheckResult:
        result = HealthCheckResult(
            check_id=new_id("check"), target=target, status=status,
            latency_ms=latency_ms, checked_at=time.time())
        self.registry.register_health(result)
        self.metrics.increment("devops.health_checks")
        self.events.publish(DevopsEventType.HEALTH_CHECKED,
                            {"check_id": result.check_id, "target": target,
                             "status": status.value})
        return result

    def record_metric(self, name: str, value: float,
                      unit: str = "", source: str = "") -> MetricSample:
        sample = MetricSample(
            metric_id=new_id("metric"), name=name, value=value, unit=unit,
            source=source, sampled_at=time.time())
        self.registry.register_metric(sample)
        return sample

    def collect_log(self, source: str, message: str,
                    level: str = "info") -> LogEntry:
        entry = LogEntry(
            log_id=new_id("log"), source=source, level=level,
            message=message, timestamp=time.time())
        self.registry.register_log(entry)
        self.metrics.increment("devops.logs")
        self.events.publish(DevopsEventType.LOG_COLLECTED,
                            {"log_id": entry.log_id, "source": source})
        return entry

    # -- backups / restores ---------------------------------------------------
    def start_backup(self, target: str) -> BackupJob:
        backup = BackupJob(
            backup_id=new_id("backup"), target=target,
            status=BackupStatus.SUCCEEDED,
            encrypted=self.config.backup_encrypted,
            started_at=time.time(), finished_at=time.time(),
            created_at=time.time())
        self.registry.register_backup(backup)
        snapshot = Snapshot(
            snapshot_id=new_id("snapshot"), backup_id=backup.backup_id,
            name=f"snapshot-{backup.backup_id}", created_at=time.time())
        self.registry.register_snapshot(snapshot)
        self.metrics.increment("devops.backups")
        self.events.publish(DevopsEventType.BACKUP_STARTED,
                            {"backup_id": backup.backup_id})
        self.events.publish(DevopsEventType.BACKUP_SUCCEEDED,
                            {"backup_id": backup.backup_id})
        self.events.publish(DevopsEventType.SNAPSHOT_CREATED,
                            {"snapshot_id": snapshot.snapshot_id})
        return backup

    def restore(self, backup_id: str, target: str = "") -> RestoreJob:
        backup = self.registry.get_backup(backup_id)
        if backup is None:
            raise ValueError(f"backup not found: {backup_id}")
        restore = RestoreJob(
            restore_id=new_id("restore"), backup_id=backup_id,
            target=target or backup.target,
            status=RestoreStatus.SUCCEEDED,
            started_at=time.time(), finished_at=time.time())
        self.registry.register_restore(restore)
        self.metrics.increment("devops.restores")
        self.events.publish(DevopsEventType.RESTORE_STARTED,
                            {"restore_id": restore.restore_id})
        self.events.publish(DevopsEventType.RESTORE_SUCCEEDED,
                            {"restore_id": restore.restore_id})
        return restore

    # -- incidents ------------------------------------------------------------
    def raise_incident(self, title: str, severity: Severity = Severity.WARNING,
                       source: str = "core") -> Incident:
        incident = Incident(
            incident_id=new_id("incident"), title=title, severity=severity,
            source=source, detected_at=time.time())
        self.registry.register_incident(incident)
        self.events.publish(DevopsEventType.INCIDENT_DETECTED,
                            {"incident_id": incident.incident_id,
                             "severity": severity.value})
        return incident

    def resolve_incident(self, incident_id: str) -> bool:
        incident = self.registry.get_incident(incident_id)
        if incident is None:
            return False
        incident.status = IncidentStatus.RESOLVED
        incident.resolved_at = time.time()
        self.events.publish(DevopsEventType.INCIDENT_RESOLVED,
                            {"incident_id": incident_id})
        return True

    def list_incidents(self) -> list[Incident]:
        return self.registry.list_incidents()

    # -- cost -----------------------------------------------------------------
    def record_cost(self, resource: str, amount: float,
                    period: str = "") -> CostRecord:
        cost = CostRecord(
            cost_id=new_id("cost"), provider=self.config.provider,
            region=self.config.region, resource=resource, amount=amount,
            period=period, created_at=time.time())
        self.registry.register_cost(cost)
        self.metrics.increment("devops.costs")
        self.events.publish(DevopsEventType.COST_RECORDED,
                            {"cost_id": cost.cost_id, "amount": amount})
        return cost

    # -- stats ---------------------------------------------------------------
    def stats(self) -> dict[str, Any]:
        return {
            "registry": self.registry.stats(),
            "metrics": self.metrics.snapshot(),
            "config": self.config.snapshot(),
            "context": self.context.snapshot(),
        }
