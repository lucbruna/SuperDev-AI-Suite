"""Central registry for the DevOps & Cloud Infrastructure Engine (V37)."""

from __future__ import annotations

from typing import Any

from devops_engine.devops_models import (AutoscalePolicy, BackupJob, Build,
                                         Cluster, Container, CostRecommendation,
                                         CostRecord, Deployment, HealthCheckResult,
                                         Image, Incident, LogEntry, MetricSample,
                                         Pipeline, Pod, Release, Resource,
                                         RestoreJob, Server, Service, Snapshot)


class DevopsRegistry:
    """Public CRUD over all core DevOps entities. Subsystems keep their
    own specialized stores."""

    def __init__(self) -> None:
        self._servers: dict[str, Server] = {}
        self._resources: dict[str, Resource] = {}
        self._containers: dict[str, Container] = {}
        self._images: dict[str, Image] = {}
        self._clusters: dict[str, Cluster] = {}
        self._pods: dict[str, Pod] = {}
        self._deployments: dict[str, Deployment] = {}
        self._services: dict[str, Service] = {}
        self._pipelines: dict[str, Pipeline] = {}
        self._builds: dict[str, Build] = {}
        self._releases: dict[str, Release] = {}
        self._health: dict[str, HealthCheckResult] = {}
        self._metrics: dict[str, MetricSample] = {}
        self._logs: dict[str, LogEntry] = {}
        self._backups: dict[str, BackupJob] = {}
        self._snapshots: dict[str, Snapshot] = {}
        self._restores: dict[str, RestoreJob] = {}
        self._incidents: dict[str, Incident] = {}
        self._policies: dict[str, AutoscalePolicy] = {}
        self._costs: dict[str, CostRecord] = {}
        self._recommendations: dict[str, CostRecommendation] = {}

    # -- servers ------------------------------------------------------------
    def register_server(self, server: Server) -> None:
        self._servers[server.server_id] = server

    def get_server(self, server_id: str) -> Server | None:
        return self._servers.get(server_id)

    def list_servers(self) -> list[Server]:
        return list(self._servers.values())

    def remove_server(self, server_id: str) -> bool:
        return self._servers.pop(server_id, None) is not None

    # -- resources ----------------------------------------------------------
    def register_resource(self, resource: Resource) -> None:
        self._resources[resource.resource_id] = resource

    def get_resource(self, resource_id: str) -> Resource | None:
        return self._resources.get(resource_id)

    def list_resources(self) -> list[Resource]:
        return list(self._resources.values())

    def remove_resource(self, resource_id: str) -> bool:
        return self._resources.pop(resource_id, None) is not None

    # -- containers / images -------------------------------------------------
    def register_container(self, container: Container) -> None:
        self._containers[container.container_id] = container

    def get_container(self, container_id: str) -> Container | None:
        return self._containers.get(container_id)

    def list_containers(self) -> list[Container]:
        return list(self._containers.values())

    def register_image(self, image: Image) -> None:
        self._images[image.image_id] = image

    def get_image(self, image_id: str) -> Image | None:
        return self._images.get(image_id)

    def list_images(self) -> list[Image]:
        return list(self._images.values())

    # -- kubernetes ----------------------------------------------------------
    def register_cluster(self, cluster: Cluster) -> None:
        self._clusters[cluster.cluster_id] = cluster

    def get_cluster(self, cluster_id: str) -> Cluster | None:
        return self._clusters.get(cluster_id)

    def list_clusters(self) -> list[Cluster]:
        return list(self._clusters.values())

    def register_pod(self, pod: Pod) -> None:
        self._pods[pod.pod_id] = pod

    def list_pods(self) -> list[Pod]:
        return list(self._pods.values())

    def register_deployment(self, deployment: Deployment) -> None:
        self._deployments[deployment.deployment_id] = deployment

    def get_deployment(self, deployment_id: str) -> Deployment | None:
        return self._deployments.get(deployment_id)

    def list_deployments(self) -> list[Deployment]:
        return list(self._deployments.values())

    def register_service(self, service: Service) -> None:
        self._services[service.service_id] = service

    def list_services(self) -> list[Service]:
        return list(self._services.values())

    # -- cicd ----------------------------------------------------------------
    def register_pipeline(self, pipeline: Pipeline) -> None:
        self._pipelines[pipeline.pipeline_id] = pipeline

    def get_pipeline(self, pipeline_id: str) -> Pipeline | None:
        return self._pipelines.get(pipeline_id)

    def list_pipelines(self) -> list[Pipeline]:
        return list(self._pipelines.values())

    def register_build(self, build: Build) -> None:
        self._builds[build.build_id] = build

    def list_builds(self) -> list[Build]:
        return list(self._builds.values())

    def register_release(self, release: Release) -> None:
        self._releases[release.release_id] = release

    def list_releases(self) -> list[Release]:
        return list(self._releases.values())

    # -- observability -------------------------------------------------------
    def register_health(self, result: HealthCheckResult) -> None:
        self._health[result.check_id] = result

    def list_health(self) -> list[HealthCheckResult]:
        return list(self._health.values())

    def register_metric(self, sample: MetricSample) -> None:
        self._metrics[sample.metric_id] = sample

    def list_metrics(self) -> list[MetricSample]:
        return list(self._metrics.values())

    def register_log(self, entry: LogEntry) -> None:
        self._logs[entry.log_id] = entry
        if len(self._logs) > 10000:
            oldest = next(iter(self._logs))
            del self._logs[oldest]

    def list_logs(self) -> list[LogEntry]:
        return list(self._logs.values())

    # -- backup / recovery ---------------------------------------------------
    def register_backup(self, backup: BackupJob) -> None:
        self._backups[backup.backup_id] = backup

    def get_backup(self, backup_id: str) -> BackupJob | None:
        return self._backups.get(backup_id)

    def list_backups(self) -> list[BackupJob]:
        return list(self._backups.values())

    def register_snapshot(self, snapshot: Snapshot) -> None:
        self._snapshots[snapshot.snapshot_id] = snapshot

    def list_snapshots(self) -> list[Snapshot]:
        return list(self._snapshots.values())

    def register_restore(self, restore: RestoreJob) -> None:
        self._restores[restore.restore_id] = restore

    def list_restores(self) -> list[RestoreJob]:
        return list(self._restores.values())

    def register_incident(self, incident: Incident) -> None:
        self._incidents[incident.incident_id] = incident

    def get_incident(self, incident_id: str) -> Incident | None:
        return self._incidents.get(incident_id)

    def list_incidents(self) -> list[Incident]:
        return list(self._incidents.values())

    def open_incidents(self) -> list[Incident]:
        return [incident for incident in self._incidents.values()
                if incident.status.value != "resolved"]

    # -- scaling / cost ------------------------------------------------------
    def register_policy(self, policy: AutoscalePolicy) -> None:
        self._policies[policy.policy_id] = policy

    def list_policies(self) -> list[AutoscalePolicy]:
        return list(self._policies.values())

    def register_cost(self, cost: CostRecord) -> None:
        self._costs[cost.cost_id] = cost

    def list_costs(self) -> list[CostRecord]:
        return list(self._costs.values())

    def register_recommendation(self, recommendation: CostRecommendation
                                ) -> None:
        self._recommendations[recommendation.recommendation_id] = \
            recommendation

    def list_recommendations(self) -> list[CostRecommendation]:
        return list(self._recommendations.values())

    # -- stats ---------------------------------------------------------------
    def stats(self) -> dict[str, Any]:
        return {
            "servers": len(self._servers),
            "resources": len(self._resources),
            "containers": len(self._containers),
            "images": len(self._images),
            "clusters": len(self._clusters),
            "deployments": len(self._deployments),
            "pipelines": len(self._pipelines),
            "builds": len(self._builds),
            "releases": len(self._releases),
            "health_checks": len(self._health),
            "metrics": len(self._metrics),
            "logs": len(self._logs),
            "backups": len(self._backups),
            "snapshots": len(self._snapshots),
            "restores": len(self._restores),
            "incidents": len(self._incidents),
            "policies": len(self._policies),
            "costs": len(self._costs),
            "recommendations": len(self._recommendations),
        }
