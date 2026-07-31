from __future__ import annotations

import logging
import time
import uuid
from pathlib import Path
from typing import Any

from ..devops_context import DevOpsContext
from ..devops_events import DevOpsEvents
from ..devops_interfaces import IDeploymentStrategy
from ..devops_metrics import DevOpsMetrics
from ..devops_store import load_json, save_json
from .blue_green_deployment import BlueGreenDeployment
from .canary_deployment import CanaryDeployment
from .deployment_health import DeploymentHealth
from .deployment_history import DeploymentHistory
from .deployment_spec import DeploymentSpec
from .rolling_deployment import RollingDeployment

# Statuses that allow rollback.
_ROLLBACKABLE = {"healthy", "deployed", "deploying", "prepared", "canary", "failed"}


class DeploymentEngine:
    """Coordinates application deployments using pluggable strategies.

    Real in-memory implementation:

        engine = DeploymentEngine()
        record = engine.deploy("billing-api", "v2.3.0", strategy="canary")
        engine.advance(record["deployment_id"])     # canary-only
        engine.switch(record["deployment_id"])      # blue-green-only
        engine.status(record["deployment_id"])
        engine.rollback(record["deployment_id"])
    """

    def __init__(
        self,
        context: DevOpsContext | None = None,
        events: DevOpsEvents | None = None,
        metrics: DevOpsMetrics | None = None,
        store_path: str | Path | None = None,
    ) -> None:
        self._log = logging.getLogger("superdev.devops.deployment")
        self._context = context or DevOpsContext()
        self._events = events or DevOpsEvents()
        self._metrics = metrics or DevOpsMetrics()
        self._strategies: dict[str, IDeploymentStrategy] = {}
        self._deployments: dict[str, dict[str, Any]] = {}
        self._history = DeploymentHistory()
        self._health = DeploymentHealth(engine=self)
        self._store = Path(store_path) if store_path else None

        # Register the built-in strategies by default.
        self.register_strategy("rolling", RollingDeployment())
        self.register_strategy("canary", CanaryDeployment())
        self.register_strategy("blue_green", BlueGreenDeployment())

        # Restore persisted state (deployments + audit trail) when a store is configured.
        self._load_state()

    # -- strategy management -------------------------------------------------

    def register_strategy(self, name: str, strategy: IDeploymentStrategy) -> None:
        self._strategies[name] = strategy

    def unregister_strategy(self, name: str) -> bool:
        return self._strategies.pop(name, None) is not None

    def list_strategies(self) -> list[str]:
        return list(self._strategies)

    # -- deployment lifecycle --------------------------------------------------

    def deploy(
        self,
        service: str,
        version: str,
        strategy: str | None = None,
        environment: str = "development",
        config: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Deploy a service version using the given (or default) strategy."""
        strategy_name = strategy or "rolling"
        strat = self._strategies.get(strategy_name)
        if strat is None:
            raise ValueError(f"unknown deployment strategy: {strategy_name}")

        spec = DeploymentSpec(service, version)
        for key, value in (config or {}).items():
            spec.set(key, value)
        errors = spec.validate()
        if errors:
            raise ValueError(f"invalid deployment spec: {', '.join(errors)}")

        deployment_id = self._new_id()
        self._context.set("deployment_id", deployment_id)
        self._context.set("service", service)
        self._context.set("environment", environment)

        record: dict[str, Any] = {
            "deployment_id": deployment_id,
            "service": service,
            "version": version,
            "environment": environment,
            "strategy": strategy_name,
            "status": "deploying",
            "config": spec.to_dict(),
            "created_at": time.time(),
            "updated_at": time.time(),
            "error": None,
        }
        self._deployments[deployment_id] = record
        self._emit("deployment.started", deployment_id=deployment_id, service=service, version=version)

        try:
            result = strat.deploy(service, environment, {**spec.to_dict(), "deployment_id": deployment_id})
            ok = bool(result.get("ok", True))
            status = str(result.get("status", "healthy"))
            record["status"] = status if ok else "failed"
            if not ok:
                record["error"] = result.get("error") or result.get("message") or "deployment failed"
            record["result"] = result
            record["updated_at"] = time.time()
        except Exception as exc:  # pragma: no cover - defensive
            record["status"] = "failed"
            record["error"] = str(exc)
            record["updated_at"] = time.time()

        self._history.record(
            deployment_id,
            service,
            version,
            environment=environment,
            strategy=strategy_name,
            status=record["status"],
        )
        self._metrics.increment("devops.deploys")
        if record["status"] == "failed":
            self._metrics.increment("devops.deploys_failed")
        self._emit(
            "deployment.completed",
            deployment_id=deployment_id,
            service=service,
            status=record["status"],
        )
        self._persist()
        return dict(record)

    def rollback(self, deployment_id: str) -> dict[str, Any]:
        """Roll back a deployment via its strategy."""
        record = self._deployments.get(deployment_id)
        if record is None:
            raise KeyError(f"deployment not found: {deployment_id}")
        if record["status"] not in _ROLLBACKABLE:
            return dict(record)
        strat = self._strategies.get(record["strategy"])
        try:
            result = strat.rollback(deployment_id) if strat is not None else {"ok": True, "status": "rolled_back"}
            ok = bool(result.get("ok", True))
            record["status"] = "rolled_back" if ok else "failed"
            if not ok:
                record["error"] = result.get("error") or "rollback failed"
            record["result"] = result
        except Exception as exc:  # pragma: no cover - defensive
            record["status"] = "failed"
            record["error"] = str(exc)
        record["updated_at"] = time.time()
        self._history.record(
            record["deployment_id"],
            record["service"],
            record["version"],
            environment=record["environment"],
            strategy=record["strategy"],
            status=record["status"],
        )
        self._metrics.increment("devops.rollbacks")
        self._emit("deployment.rolled_back", deployment_id=deployment_id, status=record["status"])
        self._persist()
        return dict(record)

    def cancel(self, deployment_id: str) -> bool:
        """Cancel an in-flight deployment. Returns True when cancelled."""
        record = self._deployments.get(deployment_id)
        if record is None or record["status"] not in ("deploying", "prepared", "canary"):
            return False
        record["status"] = "cancelled"
        record["updated_at"] = time.time()
        self._metrics.increment("devops.deploys_cancelled")
        self._emit("deployment.cancelled", deployment_id=deployment_id)
        self._persist()
        return True

    def advance(self, deployment_id: str) -> dict[str, Any]:
        """Advance a canary deployment to the next traffic step."""
        record = self._require(deployment_id)
        strat = self._strategies.get(record["strategy"])
        advance = getattr(strat, "advance", None)
        if advance is None:
            raise ValueError(f"strategy '{record['strategy']}' does not support advance()")
        result = advance(deployment_id)
        record["status"] = str(result.get("status", record["status"]))
        record["result"] = result
        record["updated_at"] = time.time()
        self._persist()
        return self.status(deployment_id)

    def switch(self, deployment_id: str) -> dict[str, Any]:
        """Switch traffic for a blue-green deployment."""
        record = self._require(deployment_id)
        strat = self._strategies.get(record["strategy"])
        switch = getattr(strat, "switch", None)
        if switch is None:
            raise ValueError(f"strategy '{record['strategy']}' does not support switch()")
        result = switch(deployment_id)
        record["status"] = str(result.get("status", record["status"]))
        record["result"] = result
        record["updated_at"] = time.time()
        self._persist()
        return self.status(deployment_id)

    # -- status & queries ------------------------------------------------------

    def status(self, deployment_id: str) -> dict[str, Any]:
        """Return the current record for a deployment (raises KeyError if unknown)."""
        record = self._require(deployment_id)
        result = dict(record)
        strat = self._strategies.get(record["strategy"])
        if strat is not None and hasattr(strat, "status"):
            result["strategy_status"] = strat.status(deployment_id)
        return result

    def list(self, service: str | None = None) -> list[dict[str, Any]]:
        """List deployment records, optionally filtered by service."""
        records = list(self._deployments.values())
        if service is not None:
            records = [r for r in records if r["service"] == service]
        return [dict(r) for r in records]

    def history(self, service: str | None = None) -> list[dict[str, Any]]:
        """Return the deployment audit trail."""
        return self._history.list(service)

    def health(self) -> dict[str, Any]:
        return {
            "deployments": len(self._deployments),
            "active": sum(
                1 for r in self._deployments.values() if r["status"] in ("deploying", "prepared", "canary")
            ),
            "strategies": list(self._strategies),
        }

    @property
    def deployments(self) -> dict[str, dict[str, Any]]:
        return dict(self._deployments)

    @property
    def metrics(self) -> DevOpsMetrics:
        return self._metrics

    # -- internals --------------------------------------------------------------

    def _require(self, deployment_id: str) -> dict[str, Any]:
        record = self._deployments.get(deployment_id)
        if record is None:
            raise KeyError(f"deployment not found: {deployment_id}")
        return record

    def _new_id(self) -> str:
        return f"dep-{uuid.uuid4().hex[:12]}"

    def _emit(self, event: str, **data: Any) -> None:
        self._events.emit(event, **data)

    # -- persistence ---------------------------------------------------------

    def _load_state(self) -> None:
        if self._store is None:
            return
        deployments = load_json(self._store / "deployments.json", default={})
        if isinstance(deployments, dict):
            self._deployments = deployments
        history = load_json(self._store / "history.json", default=[])
        if isinstance(history, list):
            self._history.load(history)
        strategy_state = load_json(self._store / "strategy_state.json", default={})
        if isinstance(strategy_state, dict):
            self._restore_strategy_state(strategy_state)

    def _persist(self) -> None:
        if self._store is None:
            return
        save_json(self._store / "deployments.json", self._deployments)
        save_json(self._store / "history.json", self._history.entries())
        save_json(self._store / "strategy_state.json", self._snapshot_strategy_state())

    def _snapshot_strategy_state(self) -> dict[str, Any]:
        return {
            name: strategy.snapshot_state()
            for name, strategy in self._strategies.items()
            if hasattr(strategy, "snapshot_state")
        }

    def _restore_strategy_state(self, state: dict[str, Any]) -> None:
        for name, strategy in self._strategies.items():
            restore = getattr(strategy, "restore_state", None)
            if restore is not None and name in state:
                restore(state[name])

    def save_state(self) -> None:
        """Persist current state to disk (no-op without store_path)."""
        self._persist()

    def reload_state(self) -> None:
        """Reload state from disk, discarding in-memory changes."""
        self._load_state()
