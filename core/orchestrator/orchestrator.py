"""System Orchestrator — the brain of the SuperDev platform.

This is the single most important file in the entire codebase. It controls:
- System initialization and boot sequence
- Service lifecycle and dependency resolution
- Event distribution across all modules
- Agent and AI engine coordination
- Workflow execution and scheduling
- Failure detection and automatic recovery
- Graceful shutdown and cleanup
- Real-time metrics and monitoring
"""

from __future__ import annotations

import asyncio
import contextlib
import signal
import time
from datetime import datetime, timezone
from typing import Any

from .agent_manager import AgentManager
from .boot_manager import BootManager
from .configuration_loader import ConfigurationLoader, OrchestratorConfig
from .event_bus import EventBus
from .exceptions import OrchestratorError, ShutdownError, ShutdownTimeoutError
from .health_monitor import HealthMonitor
from .logger_manager import LoggerManager
from .metrics_collector import MetricsCollector
from .plugin_bridge import PluginBridge
from .recovery_manager import RecoveryManager
from .service_registry import ServiceRegistry
from .state_manager import StateManager
from .task_scheduler import TaskScheduler
from .types import (
    BootConfig,
    ServiceCategory,
    ServiceStatus,
    SystemEvent,
    SystemMetrics,
    SystemStatus,
    now_iso,
)
from .workflow_bridge import WorkflowBridge


class Orchestrator:
    """Central orchestrator for the entire SuperDev platform.

    This class is the singleton brain of the system. It is initialized
    once at startup and controls every aspect of the platform lifecycle.

    Architecture (as specified):
        Orchestrator
        ├── BootManager        — system startup sequence
        ├── ServiceRegistry    — register of all platform services
        ├── AgentManager       — AI agent lifecycle
        ├── AIManager          — AI engine coordination
        ├── EventDispatcher    — EventBus for inter-module comms
        ├── TaskScheduler      — scheduled and recurring tasks
        ├── WorkflowEngine     — complex multi-step workflows
        ├── HealthMonitor      — periodic health checks
        ├── RecoveryManager    — automatic failure recovery
        ├── PluginLoader       — plugin system integration
        ├── MetricsCollector   — system-wide metrics
        ├── StateManager       — persistent global state
        ├── ConfigurationLoader — config management
        ├── LoggerManager      — centralized logging
        └── ShutdownManager    — graceful shutdown
    """

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self._config = config or {}
        self._status: SystemStatus = SystemStatus.OFFLINE
        self._started_at: float = 0.0
        self._running = False
        self._lock = asyncio.Lock()

        # ─── Core Components ──────────────────────────────────────────────
        self.event_bus = EventBus()
        self.service_registry = ServiceRegistry()
        self.state_manager = StateManager(
            persist_path=self._config.get("state_path", ""),
        )
        self.metrics_collector = MetricsCollector()
        self.recovery_manager = RecoveryManager(self)
        self.boot_manager = BootManager(self)

        # ─── Fase 2 Components ────────────────────────────────────────────
        self.config_loader = ConfigurationLoader()
        self.logger = LoggerManager()
        self.task_scheduler = TaskScheduler()
        self.workflow_bridge = WorkflowBridge(event_bus=self.event_bus)

        # ─── Fase 3 Components ────────────────────────────────────────────
        self.agent_manager = AgentManager(event_bus=self.event_bus)
        self.plugin_bridge = PluginBridge(event_bus=self.event_bus)
        self.health_monitor = HealthMonitor(event_bus=self.event_bus)

        # ─── Sub-Component References (set during boot) ───────────────────
        self._ai_manager_ref: Any = None
        self._scheduler_ref: Any = None

        # ─── Internal State ───────────────────────────────────────────────
        self._health_task: asyncio.Task[None] | None = None
        self._signal_handlers: list[asyncio.Task[None]] = []
        self._shutdown_hooks: list[Any] = []

    # ═══════════════════════════════════════════════════════════════════════
    # LIFECYCLE
    # ═══════════════════════════════════════════════════════════════════════

    async def boot(self, boot_config: BootConfig | None = None) -> dict[str, Any]:
        """Execute the full system boot sequence.

        Flow:
        1. Load configuration
        2. Initialize Logger
        3. Initialize Database
        4. Initialize Cache
        5. Initialize Queues
        6. Initialize API
        7. Initialize AI
        8. Initialize Plugins
        9. Initialize Dashboard
        10. Initialize Scheduler
        11. Initialize Monitoring
        12. System ONLINE
        """
        async with self._lock:
            if self._status != SystemStatus.OFFLINE:
                return {"success": False, "error": "System already running"}

            self._status = SystemStatus.STARTING
            self._started_at = time.time()

        cfg = boot_config or BootConfig()

        # Register system services
        self._register_core_services()

        # Fase 2: Initialize Logger and Configuration first
        await self.logger.initialize()
        self.logger.info("Logger initialized for system boot")

        try:
            platform_config = await self.config_loader.load(
                config_path=self._config.get("config_path", ""),
                overrides=self._config.get("overrides"),
            )
            self.logger.info(f"Configuration loaded from: {self.config_loader.get_loaded_from()}")
        except Exception as e:
            self.logger.error(f"Configuration load failed: {e}, using defaults")

        # Register Fase 2 + 3 services
        self.service_registry.register(
            "workflow.bridge", ServiceCategory.WORKFLOW,
            dependencies=["workflow.engine"],
        )
        self.service_registry.register(
            "agents.manager", ServiceCategory.AGENT,
            dependencies=["ai.engine"],
        )
        self.service_registry.register(
            "plugins.bridge", ServiceCategory.PLUGIN,
            dependencies=["plugins.loader"],
        )
        self.service_registry.register(
            "health.monitor", ServiceCategory.MONITORING,
            dependencies=["monitoring.health"],
            description="Health monitoring service",
        )

        # Fase 3: Initialize HealthMonitor
        self.health_monitor.configure(
            service_registry=self.service_registry,
            recovery_manager=self.recovery_manager,
            interval=cfg.health_check_seconds,
        )

        result = await self.boot_manager.execute_boot_sequence(cfg)

        if result["success"]:
            self._status = SystemStatus.ONLINE
            self._running = True
            await self.state_manager.record_boot()
            await self.state_manager.set_metadata(
                boot_time=now_iso(),
                version=self._config.get("version", "5.0.0"),
                mode=self._config.get("mode", "production"),
            )

            # Start background health monitoring
            if cfg.health_check_seconds > 0:
                self._health_task = asyncio.create_task(
                    self._health_loop(cfg.health_check_seconds)
                )

            # Start task scheduler
            await self.task_scheduler.start()
            self.logger.info("Task scheduler started")

            # Fase 3: Start HealthMonitor and AgentManager
            await self.health_monitor.start()
            self.logger.info("Health monitor started")

            try:
                await self.agent_manager.initialize()
                await self.agent_manager.start_all()
                self.logger.info(f"Agent manager initialized: {len(self.agent_manager.list_agents())} agents")
            except Exception as e:
                self.logger.warning(f"Agent manager init deferred: {e}")

            # Start event processing
            await self.event_bus.publish(
                "system.boot.completed",
                {"boot_time": result.get("total_time", 0)},
                source="orchestrator",
            )
        else:
            self._status = SystemStatus.CRASHED
            self.logger.error(f"System boot failed: {result.get('failed', [])}")

        return result

    def _register_core_services(self) -> None:
        """Register all core platform services in the registry."""
        services = [
            ("core.config", ServiceCategory.CORE, ["core.logger"]),
            ("core.logger", ServiceCategory.CORE, []),
            ("core.event_bus", ServiceCategory.CORE, []),
            ("core.service_registry", ServiceCategory.CORE, []),
            ("core.state_manager", ServiceCategory.CORE, []),
            ("core.scheduler", ServiceCategory.CORE, ["core.state_manager"]),
            ("database.postgres", ServiceCategory.DATABASE, []),
            ("cache.redis", ServiceCategory.CACHE, []),
            ("queue.rabbitmq", ServiceCategory.QUEUE, ["cache.redis"]),
            ("api.fastapi", ServiceCategory.API, ["database.postgres", "cache.redis"]),
            ("ai.engine", ServiceCategory.AI, ["api.fastapi"]),
            ("ai.agents", ServiceCategory.AGENT, ["ai.engine"]),
            ("plugins.loader", ServiceCategory.PLUGIN, ["core.service_registry"]),
            ("workflow.engine", ServiceCategory.WORKFLOW, ["core.scheduler"]),
            ("monitoring.health", ServiceCategory.MONITORING, ["core.event_bus"]),
            ("dashboard.web", ServiceCategory.DASHBOARD, ["api.fastapi"]),
        ]
        for name, category, deps in services:
            self.service_registry.register(
                name=name,
                category=category,
                dependencies=deps,
                description=f"{category.name.lower()}: {name}",
            )

    async def shutdown(self, timeout: float = 30.0) -> dict[str, Any]:
        """Gracefully shut down the entire platform in reverse start order."""
        async with self._lock:
            if self._status == SystemStatus.OFFLINE:
                return {"success": True, "message": "Already offline"}

            self._status = SystemStatus.OFFLINE
            self._running = False

        await self.event_bus.publish(
            "system.shutdown.starting",
            {"timeout": timeout},
            source="orchestrator",
        )

        results: dict[str, Any] = {"success": True, "services": {}}

        # Stop Fase 2 + 3 components
        await self.health_monitor.stop()
        await self.agent_manager.stop_all()
        await self.task_scheduler.stop()
        self.logger.info("All Fase 2/3 components stopped")
        await self.logger.shutdown()

        # Stop background tasks
        if self._health_task:
            self._health_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._health_task

        # Shut down services in reverse order
        start_order = self.service_registry.get_start_order()
        for service_name in reversed(start_order):
            try:
                result = await self._stop_service(service_name, timeout)
                results["services"][service_name] = result
            except Exception as e:
                results["services"][service_name] = {
                    "error": str(e), "success": False,
                }

        # Run shutdown hooks
        for hook in self._shutdown_hooks:
            with contextlib.suppress(Exception):
                await hook()

        await self.state_manager.persist()

        await self.event_bus.publish(
            "system.shutdown.completed",
            results,
            source="orchestrator",
        )

        return results

    async def _stop_service(self, name: str, timeout: float) -> dict[str, Any]:
        """Stop an individual service with timeout."""
        status = self.service_registry.get_status(name)
        if status in (ServiceStatus.STOPPED, ServiceStatus.CREATED):
            return {"status": "already_stopped"}

        try:
            self.service_registry.set_status(name, ServiceStatus.STOPPING)
            async with asyncio.timeout(timeout):
                await self.event_bus.send_to(name, "stop", {"graceful": True})
            self.service_registry.set_status(name, ServiceStatus.STOPPED)
            return {"status": "stopped"}
        except TimeoutError:
            self.service_registry.set_status(name, ServiceStatus.FAILED)
            raise ShutdownTimeoutError(name, timeout)
        except Exception as e:
            self.service_registry.set_status(name, ServiceStatus.FAILED)
            raise ShutdownError(name, str(e))

    # ═══════════════════════════════════════════════════════════════════════
    # RUNTIME
    # ═══════════════════════════════════════════════════════════════════════

    async def process_event(self, event: SystemEvent) -> None:
        """Receive and process a system event (runtime loop entry point).

        The orchestrator's runtime loop:
        1. Receive event
        2. Choose appropriate agent/service
        3. Execute task
        4. Monitor result
        5. Correct errors
        6. Update metrics
        7. Log
        """
        if not self._running:
            return

        await self.metrics_collector.increment("events_processed")

        try:
            # Route event to appropriate handler based on type
            if event.event_type.startswith("agent."):
                await self._handle_agent_event(event)
            elif event.event_type.startswith("workflow."):
                await self._handle_workflow_event(event)
            elif event.event_type.startswith("plugin."):
                await self._handle_plugin_event(event)
            elif event.event_type.startswith("system."):
                await self._handle_system_event(event)
            else:
                # Default: publish to event bus for any subscriber
                await self.event_bus.publish(
                    event.event_type, event.data, source="orchestrator"
                )

            await self.metrics_collector.increment("tasks_completed")

        except Exception as e:
            await self.metrics_collector.increment("tasks_failed")
            # Attempt recovery
            await self.recovery_manager.handle_failure(
                service=event.source,
                error=str(e),
                context={"event": event.event_type},
            )

    async def _handle_agent_event(self, event: SystemEvent) -> None:
        """Route events to the AI agent system."""
        await self.event_bus.publish(
            f"ai.{event.event_type}",
            event.data,
            source="orchestrator",
        )

    async def _handle_workflow_event(self, event: SystemEvent) -> None:
        """Route events to the workflow engine."""
        await self.event_bus.publish(
            f"workflow.{event.event_type}",
            event.data,
            source="orchestrator",
        )

    async def _handle_plugin_event(self, event: SystemEvent) -> None:
        """Route events to the plugin system."""
        await self.event_bus.publish(
            f"plugin.{event.event_type}",
            event.data,
            source="orchestrator",
        )

    async def _handle_system_event(self, event: SystemEvent) -> None:
        """Handle system-level events."""
        if event.event_type == "system.healthcheck.request":
            metrics = await self.collect_metrics()
            await self.event_bus.publish(
                "system.healthcheck.response",
                metrics.__dict__,
                source="orchestrator",
                correlation_id=event.correlation_id,
            )

    async def run_event_loop(self) -> None:
        """Main runtime event loop.

        After boot(), this runs indefinitely, processing events
        as they arrive through the EventBus subscription.
        Uses asyncio.Event() for efficient wake-up instead of busy-wait.
        """
        self._event_ready = asyncio.Event()

        async def event_handler(event: SystemEvent) -> None:
            if event.source == "orchestrator":
                return  # Prevent infinite loops from our own events
            await self.process_event(event)
            self._event_ready.set()

        self.event_bus.subscribe("*", event_handler)

        try:
            while self._running:
                self._event_ready.clear()
                await asyncio.wait_for(
                    self._event_ready.wait(), timeout=1.0
                )
        except (asyncio.TimeoutError, asyncio.CancelledError):
            pass

    # ═══════════════════════════════════════════════════════════════════════
    # HEALTH
    # ═══════════════════════════════════════════════════════════════════════

    async def _health_loop(self, interval: float) -> None:
        """Background task that periodically checks all service health."""
        while self._running:
            try:
                await asyncio.sleep(interval)

                # Perform health checks
                services = self.service_registry.list_services()
                for svc in services:
                    report = await self.boot_manager.check_service_health(svc["name"])
                    self.service_registry.record_health(svc["name"], report)

                    if not report.is_healthy:
                        await self.recovery_manager.handle_failure(
                            service=svc["name"],
                            error=report.message,
                            context={},
                        )

                # Check overall system health
                summary = self.service_registry.get_summary()
                total = summary["total_services"]
                by_status = summary["by_status"]
                failed_count = by_status.get(ServiceStatus.FAILED.value, 0)
                degraded_count = by_status.get(ServiceStatus.DEGRADED.value, 0)

                if failed_count > 0:
                    # System is degraded, not crashed
                    if self._status == SystemStatus.ONLINE:
                        self._status = SystemStatus.DEGRADED
                elif degraded_count == 0 and self._status == SystemStatus.DEGRADED:
                    self._status = SystemStatus.ONLINE

                await self.event_bus.publish(
                    "system.health.tick",
                    {
                        "status": self._status.value,
                        "total": total,
                        "failed": failed_count,
                        "degraded": degraded_count,
                    },
                    source="orchestrator",
                )

            except asyncio.CancelledError:
                break
            except Exception:
                pass

    # ═══════════════════════════════════════════════════════════════════════
    # METRICS
    # ═══════════════════════════════════════════════════════════════════════

    async def collect_metrics(self) -> SystemMetrics:
        """Collect a snapshot of system-wide metrics."""
        summary = self.service_registry.get_summary()
        by_status = summary["by_status"]
        total = summary["total_services"]

        return SystemMetrics(
            uptime_seconds=round(time.time() - self._started_at, 2) if self._started_at else 0,
            active_services=by_status.get(ServiceStatus.RUNNING.value, 0) if total else 0,
            total_services=total,
            healthy_services=by_status.get(ServiceStatus.RUNNING.value, 0),
            failed_services=by_status.get(ServiceStatus.FAILED.value, 0),
            events_processed=self.metrics_collector.get("events_processed", 0),
            tasks_completed=self.metrics_collector.get("tasks_completed", 0),
            tasks_failed=self.metrics_collector.get("tasks_failed", 0),
            timestamp=now_iso(),
        )

    # ═══════════════════════════════════════════════════════════════════════
    # REGISTRATION & HOOKS
    # ═══════════════════════════════════════════════════════════════════════

    def add_shutdown_hook(self, hook: Any) -> None:
        """Register a function to be called during shutdown."""
        self._shutdown_hooks.append(hook)

    def set_references(
        self,
        agent_manager: Any = None,
        ai_manager: Any = None,
        workflow_engine: Any = None,
        plugin_loader: Any = None,
        scheduler: Any = None,
    ) -> None:
        """Set references to sub-components after they are initialized."""
        if agent_manager:
            self._agent_manager_ref = agent_manager
            self.service_registry.set_status("ai.agents", ServiceStatus.RUNNING)
        if ai_manager:
            self._ai_manager_ref = ai_manager
            self.service_registry.set_status("ai.engine", ServiceStatus.RUNNING)
        if workflow_engine:
            self._workflow_engine_ref = workflow_engine
            self.service_registry.set_status("workflow.engine", ServiceStatus.RUNNING)
        if plugin_loader:
            self._plugin_loader_ref = plugin_loader
            self.service_registry.set_status("plugins.loader", ServiceStatus.RUNNING)
        if scheduler:
            self._scheduler_ref = scheduler
            self.service_registry.set_status("core.scheduler", ServiceStatus.RUNNING)

    # ═══════════════════════════════════════════════════════════════════════
    # STATUS & QUERIES
    # ═══════════════════════════════════════════════════════════════════════

    @property
    def status(self) -> SystemStatus:
        return self._status

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def uptime(self) -> float:
        return round(time.time() - self._started_at, 2) if self._started_at else 0.0

    async def get_system_info(self) -> dict[str, Any]:
        """Get complete system status information."""
        metrics = await self.collect_metrics()
        return {
            "status": self._status.value,
            "uptime_seconds": self.uptime,
            "version": self._config.get("version", "5.0.0"),
            "environment": self._config.get("environment", "production"),
            "boot_count": await self.state_manager.get_boot_count(),
            "metrics": metrics.__dict__,
            "services": self.service_registry.get_summary(),
            "event_bus": self.event_bus.get_statistics(),
        }
