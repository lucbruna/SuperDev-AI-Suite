from __future__ import annotations

import time
from collections.abc import AsyncIterator
from typing import Any

from .ai_config import AIConfig, get_ai_config
from .ai_context import AIContext
from .ai_events import AIEvents
from .ai_factory import AIFactory
from .ai_health import AIHealth
from .ai_logger import AILogger
from .ai_manager import AIManager
from .ai_metrics import AIMetrics
from .ai_registry import AIRegistry
from .ai_runtime import AIRuntime
from .ai_state import AIState
from .core.platform import AIPlatform


class AIEngine:
    """Central AI Engine that initializes and coordinates all AI infrastructure."""

    def __init__(self, config: AIConfig | None = None):
        self.config = config or get_ai_config()
        self._start_time: float = 0.0
        self._initialized = False

        # Core subsystems
        self.platform = AIPlatform()
        self.manager = AIManager()
        self.factory = AIFactory()
        self.registry = AIRegistry()
        self.runtime = AIRuntime()
        self.state = AIState()
        self.health = AIHealth()
        self.metrics = AIMetrics()
        self.events = AIEvents()
        self.logger = AILogger()
        self.context = AIContext()

    async def initialize(self) -> None:
        """Initialize the AI engine and all subsystems."""
        if self._initialized:
            self.logger.warn("AI Engine already initialized")
            return

        self._start_time = time.time()
        self.logger.info("Initializing AI Engine", extra={"version": "2.0.0"})

        # Bootstrap platform
        await self.platform.initialize()

        # Register core modules
        self.manager.register_module("platform", self.platform)
        self.manager.register_module("factory", self.factory)
        self.manager.register_module("registry", self.registry)
        self.manager.register_module("runtime", self.runtime)
        self.manager.register_module("state", self.state)
        self.manager.register_module("health", self.health)
        self.manager.register_module("metrics", self.metrics)
        self.manager.register_module("events", self.events)

        self._initialized = True
        self.events.emit("engine_initialized", {"version": "2.0.0"})
        self.logger.info("AI Engine initialized successfully")

    async def shutdown(self) -> None:
        """Shutdown the AI engine gracefully."""
        if not self._initialized:
            return

        self.logger.info("Shutting down AI Engine")
        self.events.emit("engine_shutting_down", {})

        await self.platform.shutdown()
        self.state.reset()
        self.metrics.reset()
        self.runtime.cancel_all()
        self._initialized = False

        self.logger.info("AI Engine shutdown complete")

    async def chat(self, messages: list[dict[str, Any]], **kwargs: Any) -> dict[str, Any]:
        """Send a chat completion through the engine."""
        self.metrics.increment("chat_requests")
        try:
            result = await self.platform.chat(messages, **kwargs)
            self.metrics.increment("chat_completions")
            return result
        except Exception as e:
            self.metrics.increment("chat_errors")
            self.events.emit("error_occurred", {"error": str(e)})
            raise

    async def stream(self, messages: list[dict[str, Any]], **kwargs: Any) -> AsyncIterator[dict[str, Any]]:
        """Stream a chat completion."""
        self.metrics.increment("stream_requests")
        try:
            async for chunk in self.platform.stream(messages, **kwargs):
                self.metrics.increment("stream_chunks")
                yield chunk
        except Exception as e:
            self.metrics.increment("stream_errors")
            self.events.emit("error_occurred", {"error": str(e)})
            raise

    async def embeddings(self, texts: list[str], **kwargs: Any) -> list[list[float]]:
        """Generate embeddings."""
        self.metrics.increment("embedding_requests")
        return await self.platform.embeddings(texts, **kwargs)

    @property
    def is_initialized(self) -> bool:
        return self._initialized

    @property
    def uptime(self) -> float:
        if not self._initialized or self._start_time == 0:
            return 0.0
        return time.time() - self._start_time

    async def __aenter__(self) -> AIEngine:
        await self.initialize()
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.shutdown()
