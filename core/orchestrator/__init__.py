"""System Orchestrator — the brain of the SuperDev platform.

Modules:
    orchestrator         — Main orchestrator class (singleton brain)
    configuration_loader — Config loading from files, env, and overrides
    event_bus            — Typed pub/sub event bus for inter-module communication
    service_registry     — Central register of all platform services
    state_manager        — Persistent global state with namespaces
    boot_manager         — Ordered boot sequence with dependency resolution
    recovery_manager     — Automatic failure recovery with circuit breaker
    metrics_collector    — System-wide metrics (counters, gauges, histograms)
    logger_manager       — Centralized logging with audit trail
    task_scheduler       — Scheduled and recurring task management
    workflow_bridge      — Integration between Orchestrator and Workflow Engine
    agent_manager        — Orchestrator-level AI agent management
    plugin_bridge        — Integration between Orchestrator and Plugin Manager
    health_monitor       — Dedicated service health monitoring
    types                — Shared type definitions (enums, dataclasses, protocols)
    exceptions           — Exception hierarchy for the orchestrator
"""

from .agent_manager import AgentManager
from .boot_manager import BootManager
from .configuration_loader import ConfigurationLoader, OrchestratorConfig
from .event_bus import EventBus
from .exceptions import (
    BootError, BootTimeoutError, EventBusError, EventDeliveryError,
    OrchestratorError, RecoveryError, ServiceAlreadyRegisteredError,
    ServiceDependencyError, ServiceNotFoundError, ShutdownError,
    ShutdownTimeoutError, StateError, StatePersistenceError,
)
from .health_monitor import HealthMonitor
from .logger_manager import LoggerManager
from .metrics_collector import MetricsCollector
from .orchestrator import Orchestrator
from .plugin_bridge import PluginBridge
from .recovery_manager import RecoveryManager
from .service_registry import ServiceRegistry
from .state_manager import StateManager
from .task_scheduler import TaskScheduler
from .types import (
    BootConfig, EventPriority, HealthReport, ServiceCategory,
    ServiceInfo, ServiceStatus, SystemEvent, SystemMetrics, SystemStatus,
)
from .workflow_bridge import WorkflowBridge

__all__ = [
    "Orchestrator", "ConfigurationLoader", "OrchestratorConfig",
    "EventBus", "ServiceRegistry", "StateManager", "BootManager",
    "RecoveryManager", "MetricsCollector", "LoggerManager",
    "TaskScheduler", "WorkflowBridge", "AgentManager",
    "PluginBridge", "HealthMonitor",
    # Exceptions
    "OrchestratorError", "BootError", "BootTimeoutError",
    "ServiceNotFoundError", "ServiceAlreadyRegisteredError",
    "ServiceDependencyError", "EventBusError", "EventDeliveryError",
    "RecoveryError", "ShutdownError", "ShutdownTimeoutError",
    "StateError", "StatePersistenceError",
    # Types
    "ServiceStatus", "SystemStatus", "ServiceCategory", "EventPriority",
    "BootConfig", "HealthReport", "ServiceInfo", "SystemEvent", "SystemMetrics",
]
