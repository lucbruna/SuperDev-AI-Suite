"""Agent lifecycle management subsystem."""
from __future__ import annotations

from .lifecycle_engine import LifecycleEngine
from .startup import StartupManager
from .shutdown import ShutdownManager
from .activation import ActivationManager
from .suspension import SuspensionManager
from .versioning import VersionManager
from .health import HealthMonitor

__all__ = [
    "LifecycleEngine",
    "StartupManager",
    "ShutdownManager",
    "ActivationManager",
    "SuspensionManager",
    "VersionManager",
    "HealthMonitor",
]
