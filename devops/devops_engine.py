from __future__ import annotations

import contextlib
import logging
import time
import uuid
from pathlib import Path
from typing import Any

from .devops_config import DevOpsConfig
from .devops_context import DevOpsContext
from .devops_events import DevOpsEvents
from .devops_factory import DevOpsFactory
from .devops_logger import DevOpsLogger
from .devops_manager import DevOpsManager
from .devops_metrics import DevOpsMetrics
from .devops_models import DevOpsService
from .devops_protocols import DevOpsProtocols
from .devops_registry import DevOpsRegistry
from .devops_runtime import DevOpsRuntime
from .devops_security import DevOpsSecurity
from .devops_store import load_json, save_json

# Deployment statuses that mean the deploy failed.
_FAILED_STATUSES = {"failed", "cancelled", "rolled_back"}


class DevOpsEngine:
    """Central orchestration engine for DevOps & Cloud operations."""

    def __init__(self, store_path: str | Path | None = None) -> None:
        self._log = logging.getLogger("superdev.devops")
        self._quality_gate: Any | None = None
        self._deployment: Any | None = None
        self._docker: Any | None = None
        self._cloud: Any | None = None
        self._environments: dict[str, dict[str, Any]] = {}
        self._builds: dict[str, dict[str, Any]] = {}
        self._environments_engine: Any | None = None
        self._terraform: Any | None = None
        self._cicd: Any | None = None
        self._store = Path(store_path) if store_path else None
        self.config = DevOpsConfig()
        self.context = DevOpsContext()
        self.events = DevOpsEvents()
        self.factory = DevOpsFactory(self)
        self.logger = DevOpsLogger()
        self.manager = DevOpsManager(self)
        self.metrics = DevOpsMetrics()
        self.protocols = DevOpsProtocols()
        self.registry = DevOpsRegistry()
        self.runtime = DevOpsRuntime()
        self.security = DevOpsSecurity()
        # Restore persisted builds + environments when a store is configured.
        self._load_state()

    # -- subsystem engines (lazy) ---------------------------------------------

    @property
    def docker(self) -> Any:
        """Lazily instantiate the DockerEngine."""
        if self._docker is None:
            from .docker.docker_engine import DockerEngine

            self._docker = DockerEngine(store_path=self._store)
        return self._docker

    @property
    def cloud(self) -> Any:
        """Lazily instantiate the CloudEngine with the built-in providers."""
        if self._cloud is None:
            from .cloud.cloud_engine import CloudEngine
            from .cloud.providers import AWSProvider, AzureProvider, LocalCloudProvider

            engine = CloudEngine()
            engine.providers.register("local", LocalCloudProvider())
            engine.providers.register("aws", AWSProvider())
            engine.providers.register("azure", AzureProvider())
            self._cloud = engine
        return self._cloud

    @property
    def terraform(self) -> Any:
        """Lazily instantiate the TerraformEngine."""
        if self._terraform is None:
            from .terraform.terraform_engine import TerraformEngine

            self._terraform = TerraformEngine(context=self.context, store_path=self._store)
        return self._terraform

    @property
    def cicd(self) -> Any:
        """Lazily instantiate the CICDEngine."""
        if self._cicd is None:
            from .cicd.cicd_engine import CICDEngine

            self._cicd = CICDEngine(store_path=self._store)
        return self._cicd

    @property
    def services(self) -> list[DevOpsService]:
        return list(self.registry.list_services().values())

    @property
    def deployment(self) -> Any:
        """Lazily instantiate the DeploymentEngine (wired to events/metrics/store)."""
        if self._deployment is None:
            from .deployment.deployment_engine import DeploymentEngine

            self._deployment = DeploymentEngine(
                context=self.context,
                events=self.events,
                metrics=self.metrics,
                store_path=self._store,
            )
        return self._deployment

    # -- quality gate (Volume 15 integration) --------------------------------

    @property
    def quality_gate(self) -> Any:
        """Lazily instantiate the DevOpsQualityGate (imports quality on use)."""
        if self._quality_gate is None:
            from .deployment.quality_gate import DevOpsQualityGate

            self._quality_gate = DevOpsQualityGate()
        return self._quality_gate

    def deploy_with_quality(
        self,
        service: str,
        environment: str,
        signals: dict[str, Any] | None = None,
        version: str = "latest",
        strategy: str | None = None,
        config: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Deploy gated by the QualityEngine production gate.

        Avalia o production gate (Volume 15) antes do deploy:
        - approved   -> executa o deploy REAL via DeploymentEngine;
        - blocked    -> o deploy é bloqueado com os motivos (nada é executado);
        - unavailable -> módulo quality indisponível — prossegue sem bloqueio.
        """
        gate = self.quality_gate.guard_deploy(service, signals or {})
        blocked = gate.get("decision") == "blocked"
        if blocked:
            self.metrics.increment("devops.deploys_blocked")
            return {
                "service": service,
                "environment": environment,
                "status": "blocked",
                "deployed": False,
                "gate": gate,
                "deployment_id": None,
                "deployment": None,
            }
        deployment = self.deployment.deploy(
            service,
            version,
            strategy=strategy,
            environment=environment,
            config=config,
        )
        # O engine já registra a métrica devops.deploys; aqui apenas
        # tratamos o estado terminal do deploy executado.
        return {
            "service": service,
            "environment": environment,
            "status": deployment["status"],
            "deployed": deployment["status"] not in _FAILED_STATUSES,
            "gate": gate,
            "deployment_id": deployment["deployment_id"],
            "deployment": deployment,
        }

    def deploy(self, service: str, environment: str, **kwargs: Any) -> dict[str, Any]:
        """Execute a real deployment via the DeploymentEngine."""
        return self.deployment.deploy(
            service,
            kwargs.pop("version", "latest"),
            environment=environment,
            **kwargs,
        )

    def rollback(self, deployment_id: str) -> dict[str, Any]:
        """Roll back a previously executed deployment."""
        return self.deployment.rollback(deployment_id)

    def build(self, service: str, **kwargs: Any) -> dict[str, Any]:
        """Build a service artifact, delegating to the docker/cicd subsystems.

        Fluxo real: registra o build no engine (métrica ``devops.builds`` +
        evento ``devops.build.completed``), delega ao ``DockerEngine`` (imagem)
        e, quando um pipeline CICD é informado, roda o pipeline correspondente.
        """
        version = kwargs.pop("version", "latest")
        environment = kwargs.pop("environment", None)
        tag = kwargs.get("tag") or f"{service}:{version}"
        build_id = f"build-{uuid.uuid4().hex[:8]}"
        record = {
            "build_id": build_id,
            "service": service,
            "version": version,
            "tag": tag,
            "environment": environment,
            "status": "built",
            "created_at": time.time(),
            "config": dict(kwargs),
        }
        self._builds[build_id] = record
        self._persist()
        existing = self.registry.get_service(service)
        if existing is None:
            self.registry.register_service(
                service,
                DevOpsService(
                    name=service,
                    service_type=kwargs.get("service_type", "service"),
                    version=version,
                    environment=environment or self.config.environment,
                    status="built",
                ),
            )
        else:
            existing.version = version
            existing.status = "built"

        # Delegate the artifact/image build to the DockerEngine.
        image = self.docker.build(kwargs.get("path", "."), tag)
        record["image"] = image["image"]

        # Optionally run a CI/CD pipeline for this build.
        pipeline_name = kwargs.pop("pipeline", None)
        if pipeline_name is not None:
            self.cicd.builder.create(
                pipeline_name,
                stages=[
                    {"name": "build", "type": "build", "config": {"project": service}},
                    {"name": "test", "type": "test", "config": {"total": 10, "failed": 0}},
                    {"name": "security", "type": "security", "config": {"project": service}},
                    {"name": "artifact", "type": "artifact", "config": {"name": service, "version": version}},
                ],
            )
            record["pipeline_run"] = self.cicd.run_pipeline(pipeline_name)

        self.metrics.increment("devops.builds")
        self.events.emit("devops.build.completed", build_id=build_id, service=service, version=version)
        return dict(record)

    def provision(self, environment: str, **kwargs: Any) -> dict[str, Any]:
        """Provision an environment, delegating to cloud/environments/terraform.

        Cria os recursos no engine (métrica ``devops.provisions`` + evento),
        delega ao ``CloudEngine`` (recursos multi-provider) e ao
        ``EnvironmentsEngine`` (lifecycle do ambiente).
        """
        provider = kwargs.get("provider", self.config.provider)
        region = kwargs.get("region", self.config.region)
        resource_types = kwargs.get("resource_types") or ["compute", "storage", "network"]
        resources = []
        for rtype in resource_types:
            resource_id = f"{environment}-{rtype}-{uuid.uuid4().hex[:6]}"
            resource = {
                "resource_id": resource_id,
                "type": rtype,
                "provider": provider,
                "region": region,
                "environment": environment,
                "status": "active",
            }
            resources.append(resource)
            self.registry.register_resource(resource_id, resource)
        self._environments[environment] = {
            "name": environment,
            "status": "provisioned",
            "provider": provider,
            "region": region,
            "resources": resources,
            "created_at": time.time(),
        }
        self._persist()
        self.metrics.increment("devops.provisions")
        self.events.emit("devops.provision.completed", environment=environment, resources=len(resources))

        # Delegate to the subsystem engines (best-effort, additive results).
        cloud_resources = []
        for rtype in resource_types:
            if provider in self.cloud.providers.list():
                cloud_resources.append(
                    self.cloud.provision(provider, rtype, f"{environment}-{rtype}", region=region)
                )
        with contextlib.suppress(ValueError):
            # Environment already exists — reuse it.
            self.environments.create(
                environment, "staging" if environment != "production" else "production"
            )
        return {
            "environment": environment,
            "status": "provisioned",
            "resources": resources,
            "cloud_resources": cloud_resources,
        }

    def destroy(self, environment: str, **_kwargs: Any) -> dict[str, Any]:
        """Destroy an environment, delegating to cloud/environments/terraform."""
        env = self._environments.pop(environment, None)
        if env is None:
            return {"environment": environment, "status": "not_found", "destroyed": False}
        for resource in env["resources"]:
            self.registry.unregister_resource(resource["resource_id"])
            self.cloud.destroy(resource["provider"], resource["resource_id"])
        self.environments.destroy(environment)
        self.terraform.destroy(f"./terraform/{environment}")
        self._persist()
        self.metrics.increment("devops.destroys")
        self.events.emit("devops.destroy.completed", environment=environment)
        return {
            "environment": environment,
            "status": "destroyed",
            "destroyed": True,
            "resources": env["resources"],
        }

    @property
    def environments(self) -> Any:
        """Lazily instantiate the EnvironmentsEngine."""
        if self._environments_engine is None:
            from .environments.environments_engine import EnvironmentsEngine

            self._environments_engine = EnvironmentsEngine(context=self.context, store_path=self._store)
        return self._environments_engine

    def status(self, environment: str | None = None) -> dict[str, Any]:
        """Return aggregated status (deployments, builds, environments, services)."""
        deployments = self.deployment.list()
        if environment is not None:
            deployments = [d for d in deployments if d["environment"] == environment]
            environments = (
                {environment: self._environments[environment]}
                if environment in self._environments
                else {}
            )
            builds = [b for b in self._builds.values() if b.get("environment") == environment]
        else:
            environments = dict(self._environments)
            builds = list(self._builds.values())
        return {
            "environment": environment or "all",
            "deployments": deployments,
            "count": len(deployments),
            "builds": builds,
            "build_count": len(builds),
            "environments": environments,
            "environment_count": len(environments),
            "services": [s.name for s in self.services],
        }

    # -- persistence ---------------------------------------------------------

    def _load_state(self) -> None:
        if self._store is None:
            return
        builds = load_json(self._store / "builds.json", default={})
        if isinstance(builds, dict):
            self._builds = builds
        environments = load_json(self._store / "environments.json", default={})
        if isinstance(environments, dict):
            self._environments = environments
        # Restore the volatile registry from the persisted state so
        # status()["services"] and resource lookups keep working after reload.
        for record in self._builds.values():
            service_name = record.get("service")
            if not service_name or self.registry.get_service(service_name) is not None:
                continue
            config = record.get("config")
            service_type = config.get("service_type", "service") if isinstance(config, dict) else "service"
            self.registry.register_service(
                service_name,
                DevOpsService(
                    name=service_name,
                    service_type=service_type,
                    version=record.get("version", "latest"),
                    environment=record.get("environment") or self.config.environment,
                    status=record.get("status", "built"),
                ),
            )
        for env in self._environments.values():
            if not isinstance(env, dict):
                continue
            resources = env.get("resources") or []
            for resource in resources:
                resource_id = resource.get("resource_id") if isinstance(resource, dict) else None
                if resource_id:
                    self.registry.register_resource(resource_id, resource)

    def _persist(self) -> None:
        if self._store is None:
            return
        save_json(self._store / "builds.json", self._builds)
        save_json(self._store / "environments.json", self._environments)

    def save_state(self) -> None:
        """Persist builds/environments/deployments + all subsystem engines to disk."""
        self._persist()
        self.deployment.save_state()
        self.docker.save_state()
        self.environments.save_state()
        self.terraform.save_state()
        self.cicd.save_state()

    def reload_state(self) -> None:
        """Reload builds/environments/deployments + all subsystem engines from disk."""
        self._load_state()
        self.deployment.reload_state()
        self.docker.reload_state()
        self.environments.reload_state()
        self.terraform.reload_state()
        self.cicd.reload_state()
