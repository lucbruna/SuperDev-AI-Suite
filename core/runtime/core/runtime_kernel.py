import asyncio
import logging
from datetime import datetime

from runtime_engine.core.configuration import RuntimeConfig
from runtime_engine.core.bootstrap import Bootstrap
from runtime_engine.core.registry import RuntimeRegistry
from runtime_engine.runtime.runtime_session import RuntimeSessionManager
from runtime_engine.sandbox.sandbox_manager import SandboxManager
from runtime_engine.process.process_manager import ProcessManager
from runtime_engine.logs.runtime_logs import RuntimeLogs
from runtime_engine.monitoring.runtime_monitor import RuntimeMonitor

logger = logging.getLogger(__name__)


class RuntimeKernel:
    def __init__(self, config: RuntimeConfig | None = None) -> None:
        self.config = config or RuntimeConfig()
        self.registry = RuntimeRegistry()
        self.session_manager = RuntimeSessionManager()
        self.sandbox_manager = SandboxManager()
        self.process_manager = ProcessManager()
        self.logs = RuntimeLogs()
        self.monitor = RuntimeMonitor(self)
        self.bootstrap = Bootstrap(self.config)
        self._started_at: datetime | None = None
        self._running = False

    async def bootstrap(self) -> dict[str, bool]:
        deps = await self.bootstrap.run()
        self._started_at = datetime.utcnow()
        self._running = True
        logger.info("RuntimeKernel bootstrapped successfully")
        return deps

    async def shutdown(self) -> None:
        self._running = False
        await self.session_manager.shutdown_all()
        await self.sandbox_manager.destroy_all()
        await self.process_manager.shutdown_all()
        logger.info("RuntimeKernel shut down")

    async def health(self) -> dict:
        deps = await self.bootstrap.check_dependencies()
        uptime = None
        if self._started_at:
            uptime = (datetime.utcnow() - self._started_at).total_seconds()
        return {
            "status": "healthy" if self._running else "unhealthy",
            "uptime_seconds": uptime,
            "dependencies": deps,
            "active_sessions": len(self.session_manager),
            "active_sandboxes": self.sandbox_manager.active_count(),
            "active_processes": self.process_manager.active_count(),
        }
