"""
Interaction Manager - High-level multimodal interaction operations manager.
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from .multimodal_config import MultimodalConfig
from .multimodal_models import (
    InputType, OutputType, InteractionStatus,
    MultimodalInput, MultimodalOutput, InteractionSession,
)
from ._engine_types import EngineConfig, EngineState, EngineMetrics
from .multimodal_engine import MultimodalEngine
from .multimodal_security import MultimodalSecurityManager
from .context_manager import ContextManager

logger = logging.getLogger(__name__)


@dataclass
class ManagerConfig:
    engine_config: EngineConfig
    max_history_per_session: int = 100
    enable_auto_session_cleanup: bool = True
    cleanup_interval_seconds: int = 300


class InteractionManager:
    def __init__(self, config: ManagerConfig):
        self.config = config
        self.engine = MultimodalEngine(config.engine_config)
        self.security = config.engine_config.security
        self.context = self.engine.context
        self._initialized = False
        self._cleanup_task: Optional[asyncio.Task] = None

    async def initialize(self) -> None:
        if self._initialized:
            return
        await self.engine.initialize()
        await self.engine.start()
        if self.config.enable_auto_session_cleanup:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        self._initialized = True
        logger.info("Interaction Manager initialized")

    async def shutdown(self) -> None:
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        await self.engine.stop()
        self._initialized = False
        logger.info("Interaction Manager shutdown")

    async def process_input(
        self,
        data: Any,
        input_type: Optional[InputType] = None,
        source: str = "",
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        language: Optional[str] = None,
        raw_bytes: Optional[bytes] = None,
        mime_type: Optional[str] = None,
    ) -> MultimodalOutput:
        if not self._initialized:
            raise RuntimeError("Interaction Manager not initialized")
        if input_type is None:
            input_type = self._detect_type(data, mime_type)
        inp = MultimodalInput(
            id=str(uuid.uuid4()),
            type=input_type,
            data=data,
            source=source,
            session_id=session_id,
            user_id=user_id,
            metadata=metadata or {},
            language=language,
            raw_bytes=raw_bytes,
            mime_type=mime_type,
        )
        if not self.security.verify_access(user_id or "anonymous", input_type.value, "write"):
            raise PermissionError(f"Access denied for modality: {input_type.value}")
        return await self.engine.process_input(inp)

    async def create_session(self, user_id: Optional[str] = None) -> InteractionSession:
        return await self.engine.create_session(user_id)

    async def get_session(self, session_id: str) -> Optional[InteractionSession]:
        return await self.engine.get_session(session_id)

    async def close_session(self, session_id: str) -> None:
        await self.engine.close_session(session_id)

    async def get_interaction_history(
        self, session_id: str, limit: int = 50
    ) -> List[Dict[str, Any]]:
        session = await self.context.get_session(session_id)
        if not session:
            return []
        history = []
        for inp, out in zip(session.inputs[-limit:], session.outputs[-limit:]):
            history.append({
                "input_id": inp.id,
                "input_type": inp.type.value,
                "input_data": inp.data,
                "input_timestamp": inp.timestamp.isoformat(),
                "output_id": out.id,
                "output_type": out.type.value,
                "output_content": out.content,
                "output_timestamp": out.timestamp.isoformat(),
                "processing_time_ms": out.processing_time_ms,
            })
        return history

    async def get_conversation_history(self, session_id: str) -> List[Dict[str, str]]:
        return await self.context.get_conversation_history(session_id)

    async def get_modality_stats(self) -> Dict[str, int]:
        return dict(self.engine.metrics.modality_counts)

    async def get_engine_status(self) -> Dict[str, Any]:
        return self.engine.get_status()

    def is_healthy(self) -> bool:
        return self.engine.metrics.state == EngineState.RUNNING

    def _detect_type(self, data: Any, mime_type: Optional[str] = None) -> InputType:
        if mime_type:
            if mime_type.startswith("text/"):
                return InputType.TEXT
            if mime_type.startswith("audio/"):
                return InputType.VOICE
            if mime_type.startswith("image/"):
                return InputType.IMAGE
            if mime_type.startswith("video/"):
                return InputType.VIDEO
            if mime_type in ("application/pdf", "application/msword",
                             "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                             "text/plain", "text/html", "text/markdown",
                             "application/vnd.ms-excel", "text/csv"):
                return InputType.DOCUMENT
        if isinstance(data, str):
            return InputType.TEXT
        if isinstance(data, bytes):
            if mime_type:
                return self._detect_type(data, mime_type)
            return InputType.DOCUMENT
        if isinstance(data, dict) and any(k in data for k in ("temperature", "humidity", "pressure", "motion")):
            return InputType.SENSOR
        return InputType.TEXT

    async def _cleanup_loop(self) -> None:
        while self._initialized:
            try:
                await self.context.cleanup_expired()
                await asyncio.sleep(self.config.cleanup_interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")
                await asyncio.sleep(60)
