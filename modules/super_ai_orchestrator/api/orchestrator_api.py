"""OrchestratorAPI — the deterministic facade of the Super AI Orchestrator.

The facade wires every component together: kernel, decision engine,
governance, planner/executor, monitor, analytics, memory, telemetry and
connectors. It is the single entry point used by the FastAPI router, the
CLI and the frontend dashboard payload.

Everything remains deterministic: the facade never touches the clock, the
network or an LLM directly. ``require_approval`` is honoured only for tasks
that actually reach the governance gate (when the kernel's
``governance_required`` is enabled); otherwise tasks flow straight to the
queue, exactly as the kernel config dictates.
"""
from __future__ import annotations

from typing import Any

from modules.super_ai_orchestrator.agents import AgentRegistry
from modules.super_ai_orchestrator.analytics import OrchestratorAnalytics
from modules.super_ai_orchestrator.config import KernelConfig, OrchestratorConfig
from modules.super_ai_orchestrator.core.request import TaskRequest
from modules.super_ai_orchestrator.core.status import TaskStatus
from modules.super_ai_orchestrator.core.task import Task
from modules.super_ai_orchestrator.decision import DecisionEngine
from modules.super_ai_orchestrator.events.bus import EventBus
from modules.super_ai_orchestrator.execution import TaskExecutor
from modules.super_ai_orchestrator.governance import GovernanceEngine, GovernancePolicy
from modules.super_ai_orchestrator.integrations import ConnectorRegistry
from modules.super_ai_orchestrator.kernel import OrchestrationKernel
from modules.super_ai_orchestrator.memory import MemoryStore
from modules.super_ai_orchestrator.monitoring import OrchestratorMonitor
from modules.super_ai_orchestrator.planning import Planner
from modules.super_ai_orchestrator.routing import Router
from modules.super_ai_orchestrator.telemetry import Telemetry
from modules.super_ai_orchestrator.version import VERSION


class OrchestratorAPI:
    """Facade exposing the whole orchestrator as one deterministic object.

    Attributes:
        config: top-level orchestrator configuration.
        kernel: the scheduling/control kernel.
        decision: owner/LLM/tools selection engine.
        governance: approval gate engine.
        planner: deterministic step planner.
        executor: kind-handler dispatcher.
        monitor: health/metrics reader.
        analytics: execution analytics.
        memory: namespaced long-term memory.
        telemetry: counters/gauges.
        connectors: sibling + toolchain connector registry.
    """

    def __init__(
        self,
        config: OrchestratorConfig | None = None,
        kernel_config: KernelConfig | None = None,
        governance_policy: GovernancePolicy | None = None,
    ) -> None:
        self.config = config or OrchestratorConfig()
        self.kernel = OrchestrationKernel(kernel_config)
        self.event_bus: EventBus = self.kernel.event_bus

        self.agents = AgentRegistry()
        self.llm_registry = self._make_llm_registry()
        self.decision = DecisionEngine(
            router=Router(),
            llm_registry=self.llm_registry,
            agents=self.agents,
        )
        self.planner = Planner()
        self.executor = TaskExecutor()
        self.governance = GovernanceEngine(governance_policy)
        self.monitor = OrchestratorMonitor()
        self.analytics = OrchestratorAnalytics()
        self.memory = MemoryStore()
        self.telemetry = Telemetry()
        self.connectors = ConnectorRegistry()

        # Wire the pipeline into the kernel.
        self.kernel.set_planner(self.planner.plan)
        self.kernel.set_executor(self.executor.execute)

    def _make_llm_registry(self):  # pragma: no cover - import indirection
        from modules.super_ai_orchestrator.llm import LLMRegistry

        return LLMRegistry()

    # ------------------------------------------------------------------ #
    # Submission
    # ------------------------------------------------------------------ #
    def submit(
        self,
        kind: str,
        title: str,
        payload: dict[str, Any] | None = None,
        priority: int | None = None,
        owner_hint: str | None = None,
        require_approval: bool | None = None,
    ) -> dict[str, Any]:
        """Submit a task: decide, gate, queue. Returns the task as a dict."""
        request = TaskRequest(
            kind=kind,
            title=title,
            payload=payload or {},
            priority=priority,
            owner_hint=owner_hint,
            require_approval=require_approval,
        )
        return self.submit_request(request).to_dict()

    def submit_request(self, request: TaskRequest) -> Task:
        """Submit a ``TaskRequest``; runs the full decision + gate pipeline."""
        task = request.to_task(self.config.default_priority)
        if request.owner_hint:
            task.payload.setdefault("owner_hint", request.owner_hint)
        self.decision.decide(self.kernel, task)

        submitted = self.kernel.submit(task)
        self.telemetry.inc("tasks_submitted")

        # Governance gate: auto-approve tasks the policy does not require
        # approval for, unless the caller explicitly asked otherwise.
        if submitted.status == TaskStatus.WAITING_APPROVAL:
            if request.require_approval is True:
                needs, reason = True, "explicit approval requested"
            elif request.require_approval is False:
                needs, reason = False, "explicit approval waived"
            else:
                needs, reason = self.governance.needs_approval(submitted, self.kernel)
            if not needs:
                self.governance.approve(self.kernel, submitted)
                self.telemetry.inc("tasks_auto_approved")
        return submitted

    # ------------------------------------------------------------------ #
    # Scheduling
    # ------------------------------------------------------------------ #
    def tick(self, slices: int | None = None) -> dict[str, Any]:
        """Advance the kernel; returns the number of slices processed."""
        processed = self.kernel.tick(slices)
        self.telemetry.inc("ticks")
        return {"processed": processed}

    # ------------------------------------------------------------------ #
    # Governance hand-off
    # ------------------------------------------------------------------ #
    def approve(self, seq: int) -> dict[str, Any]:
        task = self._require(seq)
        self.governance.approve(self.kernel, task)
        self.telemetry.inc("tasks_approved")
        return task.to_dict()

    def reject(self, seq: int, reason: str) -> dict[str, Any]:
        task = self._require(seq)
        self.governance.reject(self.kernel, task, reason)
        self.telemetry.inc("tasks_rejected")
        return task.to_dict()

    # ------------------------------------------------------------------ #
    # Control
    # ------------------------------------------------------------------ #
    def cancel(self, seq: int) -> dict[str, Any]:
        task = self.kernel.cancel(self._require(seq))
        self.telemetry.inc("tasks_cancelled")
        return task.to_dict()

    def pause(self, seq: int) -> dict[str, Any]:
        task = self.kernel.pause(self._require(seq))
        return task.to_dict()

    def resume(self, seq: int) -> dict[str, Any]:
        task = self.kernel.resume(self._require(seq))
        return task.to_dict()

    def rollback(self, seq: int) -> dict[str, Any]:
        task = self.kernel.rollback(self._require(seq))
        return task.to_dict()

    # ------------------------------------------------------------------ #
    # Introspection
    # ------------------------------------------------------------------ #
    def get(self, seq: int) -> dict[str, Any]:
        return self._require(seq).to_dict()

    def tasks(self, status: str | None = None) -> list[dict[str, Any]]:
        if status is None:
            return [t.to_dict() for t in self.kernel.tasks()]
        try:
            wanted = TaskStatus(status)
        except ValueError as exc:
            raise ValueError(
                f"unknown status '{status}'; valid: "
                + ", ".join(s.value for s in TaskStatus)
            ) from exc
        return [t.to_dict() for t in self.kernel.by_status(wanted)]

    def stats(self) -> dict[str, Any]:
        return self.kernel.stats()

    def health(self) -> dict[str, Any]:
        return self.monitor.health(self.kernel)

    def metrics(self) -> dict[str, Any]:
        return self.monitor.metrics(self.kernel)

    def analytics_report(self) -> dict[str, Any]:
        return self.analytics.analyze(self.kernel)

    def audit(self) -> list[dict[str, Any]]:
        return [r.to_dict() for r in self.kernel.audit.records]

    def events(self, event_type: str | None = None) -> list[dict[str, Any]]:
        return [e.to_dict() for e in self.event_bus.history(event_type)]

    # ------------------------------------------------------------------ #
    # Memory
    # ------------------------------------------------------------------ #
    def memory_namespaces(self) -> list[str]:
        return list(self.memory.namespaces())

    def memory_keys(self, namespace: str) -> list[str]:
        return list(self.memory.keys(namespace))

    def memory_remember(self, namespace: str, key: str, value: Any) -> dict[str, Any]:
        entry = self.memory.remember(namespace, key, value)
        return {"namespace": namespace, "key": key, "version": entry.version}

    def memory_recall(self, namespace: str, key: str) -> Any:
        return self.memory.recall(namespace, key)

    def memory_forget(self, namespace: str, key: str) -> dict[str, Any]:
        removed = self.memory.forget(namespace, key)
        return {"namespace": namespace, "key": key, "removed": removed}

    def memory_snapshot(self) -> dict[str, Any]:
        return self.memory.snapshot()

    # ------------------------------------------------------------------ #
    # Integrations
    # ------------------------------------------------------------------ #
    def integrations(self) -> dict[str, Any]:
        return self.connectors.to_dict()

    def connectors_summary(self) -> list[dict[str, Any]]:
        return [c.to_dict() for c in self.connectors.all()]

    def invoke(self, name: str, action: str = "invoke", **kwargs: Any) -> dict[str, Any]:
        return self.connectors.invoke(name, action, **kwargs)

    # ------------------------------------------------------------------ #
    # Configuration & status
    # ------------------------------------------------------------------ #
    def governance_policy(self) -> dict[str, Any]:
        return self._json_safe(self.governance.policy.to_dict())

    def config_dict(self) -> dict[str, Any]:
        return {
            "orchestrator": self.config.to_dict(),
            "kernel": self.kernel.config.to_dict(),
        }

    def version(self) -> str:
        return VERSION

    def status(self) -> dict[str, Any]:
        """Aggregated status used by dashboards and health probes."""
        return {
            "version": VERSION,
            "ok": self.monitor.health(self.kernel)["status"] != "error",
            "health": self.monitor.health(self.kernel),
            "metrics": self.monitor.metrics(self.kernel),
            "stats": self.kernel.stats(),
        }

    def dashboard(self) -> dict[str, Any]:
        """Full dashboard payload (status + analytics + integrations).

        Guaranteed JSON-serializable: set/frozenset/tuple values (e.g. the
        governance policy) are converted to sorted lists.
        """
        return self._json_safe({
            "version": VERSION,
            "health": self.monitor.health(self.kernel),
            "metrics": self.monitor.metrics(self.kernel),
            "stats": self.kernel.stats(),
            "analytics": self.analytics.analyze(self.kernel),
            "governance": self.governance.policy.to_dict(),
            "connectors": {
                "available": [c.name for c in self.connectors.available()],
                "total": len(self.connectors.all()),
            },
            "telemetry": self.telemetry.snapshot(),
            "memory_namespaces": list(self.memory.namespaces()),
            "recent_tasks": [t.to_dict() for t in self.kernel.tasks()[-10:]],
            "recent_events": [
                e.to_dict() for e in self.event_bus.log[-20:]
            ],
        })

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _require(self, seq: int) -> Task:
        task = self.kernel.get(seq)
        if task is None:
            raise KeyError(f"no task with seq {seq}")
        return task

    @staticmethod
    def _json_safe(value: Any) -> Any:
        """Make a value JSON-serializable (sets/frozensets/tuples → lists)."""
        if isinstance(value, dict):
            return {str(k): OrchestratorAPI._json_safe(v) for k, v in value.items()}
        if isinstance(value, (set, frozenset, tuple)):
            try:
                return [OrchestratorAPI._json_safe(v) for v in sorted(value)]
            except TypeError:  # mixed-type collection: keep insertion order
                return [OrchestratorAPI._json_safe(v) for v in value]
        if isinstance(value, list):
            return [OrchestratorAPI._json_safe(v) for v in value]
        return value
