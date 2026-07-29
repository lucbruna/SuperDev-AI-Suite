"""
Multimodal Engine - Core orchestration engine for multimodal AI processing.
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

from .multimodal_config import MultimodalConfig
from ._engine_types import EngineConfig, EngineState, EngineMetrics
from .multimodal_models import (
    InputType, OutputType, ModalityType, InteractionStatus,
    MultimodalInput, MultimodalOutput, ProcessedInput,
    UnderstandingResult, ResponsePlan, InteractionSession,
)
from .multimodal_security import MultimodalSecurityManager
from .input_processor import InputProcessor
from .output_generator import OutputGenerator
from .context_manager import ContextManager

logger = logging.getLogger(__name__)


class MultimodalEngine:
    def __init__(self, config: EngineConfig):
        self.config = config
        self.metrics = EngineMetrics()
        self.security = config.security
        self.context = ContextManager()
        self.input_processor = InputProcessor(self.config, self.security)
        self.output_generator = OutputGenerator(self.config, self.security)
        self._subsystems: Dict[str, Any] = {}
        self._running = False
        self._main_task: Optional[asyncio.Task] = None
        self._processing_queue: asyncio.Queue = asyncio.Queue()
        self._active_tasks: Set[asyncio.Task] = set()

    async def initialize(self) -> None:
        logger.info("Initializing Multimodal AI Engine...")
        self.metrics.state = EngineState.INITIALIZING
        self.metrics.start_time = datetime.utcnow()
        await self._initialize_subsystems()
        self.metrics.state = EngineState.RUNNING
        logger.info("Multimodal AI Engine initialized")

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._main_task = asyncio.create_task(self._processing_loop())
        logger.info("Multimodal AI Engine started")

    async def stop(self) -> None:
        logger.info("Stopping Multimodal AI Engine...")
        self._running = False
        if self._main_task:
            self._main_task.cancel()
            try:
                await self._main_task
            except asyncio.CancelledError:
                pass
        for task in self._active_tasks:
            task.cancel()
        await self._shutdown_subsystems()
        self.metrics.state = EngineState.STOPPED
        logger.info("Multimodal AI Engine stopped")

    async def pause(self) -> None:
        self._running = False
        self.metrics.state = EngineState.PAUSED

    async def resume(self) -> None:
        if not self._running:
            self._running = True
            self._main_task = asyncio.create_task(self._processing_loop())
            self.metrics.state = EngineState.RUNNING

    async def _initialize_subsystems(self) -> None:
        subsystems: Dict[str, Any] = {}
        if self.config.enable_text:
            subsystems["text"] = TextSubsystem(self.config)
        if self.config.enable_voice:
            subsystems["voice"] = VoiceSubsystem(self.config)
        if self.config.enable_vision:
            subsystems["vision"] = VisionSubsystem(self.config)
        if self.config.enable_video:
            subsystems["video"] = VideoSubsystem(self.config)
        if self.config.enable_documents:
            subsystems["documents"] = DocumentSubsystem(self.config)
        if self.config.enable_sensors:
            subsystems["sensors"] = SensorSubsystem(self.config)
        if self.config.enable_conversation:
            subsystems["conversation"] = ConversationSubsystem(self.config)
        if self.config.enable_translation:
            subsystems["translation"] = TranslationSubsystem(self.config)
        self._subsystems = subsystems
        for name, sub in subsystems.items():
            await sub.initialize()
            self.metrics.subsystem_status[name] = "initialized"

    async def _shutdown_subsystems(self) -> None:
        for name, sub in self._subsystems.items():
            try:
                await sub.shutdown()
                self.metrics.subsystem_status[name] = "stopped"
            except Exception as e:
                logger.error(f"Error shutting down {name}: {e}")

    async def _processing_loop(self) -> None:
        while self._running:
            try:
                inp = await self._processing_queue.get()
                task = asyncio.create_task(self._process_single(inp))
                self._active_tasks.add(task)
                task.add_done_callback(self._active_tasks.discard)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Processing loop error: {e}")
                self.metrics.errors += 1
                await asyncio.sleep(1)

    async def _process_single(self, inp: MultimodalInput) -> MultimodalOutput:
        start = datetime.utcnow()
        try:
            self.metrics.inputs_processed += 1
            self.metrics.modality_counts[inp.type.value] = self.metrics.modality_counts.get(inp.type.value, 0) + 1
            processed = await self.input_processor.process(inp)
            session = await self.context.get_session(inp.session_id) if inp.session_id else None
            if session:
                session.add_input(inp)
            output = await self.output_generator.generate(processed, session)
            self.metrics.outputs_generated += 1
            if session:
                session.add_output(output)
            elapsed = (datetime.utcnow() - start).total_seconds() * 1000
            self.metrics.total_processing_time_ms += elapsed
            self.metrics.last_action_time = datetime.utcnow()
            return output
        except Exception as e:
            logger.error(f"Error processing input {inp.id}: {e}")
            self.metrics.errors += 1
            return MultimodalOutput(
                id=str(uuid.uuid4()),
                input_id=inp.id,
                type=OutputType.TEXT,
                content=f"Error processing input: {e}",
                metadata={"error": str(e)},
                processing_time_ms=(datetime.utcnow() - start).total_seconds() * 1000,
            )

    async def process_input(self, inp: MultimodalInput) -> MultimodalOutput:
        if self.metrics.state == EngineState.STOPPED:
            raise RuntimeError("Engine is stopped")
        if self._running:
            await self._processing_queue.put(inp)
        return await self._process_single(inp)

    async def create_session(self, user_id: Optional[str] = None) -> InteractionSession:
        session = await self.context.create_session(user_id)
        self.metrics.sessions_created += 1
        return session

    async def get_session(self, session_id: str) -> Optional[InteractionSession]:
        return await self.context.get_session(session_id)

    async def close_session(self, session_id: str) -> None:
        await self.context.close_session(session_id)

    def get_subsystem(self, name: str):
        return self._subsystems.get(name)

    def get_metrics(self) -> EngineMetrics:
        return self.metrics

    def get_status(self) -> Dict[str, Any]:
        metrics = self.metrics
        avg_time = metrics.total_processing_time_ms / max(metrics.inputs_processed, 1)
        return {
            "state": metrics.state.value,
            "uptime_seconds": (datetime.utcnow() - metrics.start_time).total_seconds() if metrics.start_time else 0,
            "inputs_processed": metrics.inputs_processed,
            "outputs_generated": metrics.outputs_generated,
            "sessions": metrics.sessions_created,
            "errors": metrics.errors,
            "avg_processing_time_ms": round(avg_time, 2),
            "modality_counts": metrics.modality_counts,
            "subsystems": metrics.subsystem_status,
        }


class _BaseSubsystem:
    def __init__(self, config: EngineConfig):
        self._config = config
        self._initialized = False

    async def initialize(self) -> None:
        self._initialized = True

    async def shutdown(self) -> None:
        self._initialized = False

    @property
    def is_initialized(self) -> bool:
        return self._initialized


class TextSubsystem(_BaseSubsystem):
    async def process(self, text: str) -> ProcessedInput: ...


class VoiceSubsystem(_BaseSubsystem):
    async def transcribe(self, audio_data: bytes) -> str: ...


class VisionSubsystem(_BaseSubsystem):
    async def analyze_image(self, image_data: bytes) -> Dict[str, Any]: ...


class VideoSubsystem(_BaseSubsystem):
    async def analyze_video(self, video_data: bytes) -> Dict[str, Any]: ...


class DocumentSubsystem(_BaseSubsystem):
    async def parse_document(self, document_data: bytes, mime_type: str) -> Dict[str, Any]: ...


class SensorSubsystem(_BaseSubsystem):
    async def process_sensor_readings(self, readings: Dict[str, Any]) -> Dict[str, Any]: ...


class ConversationSubsystem(_BaseSubsystem):
    async def manage_conversation(self, session_id: str, message: str) -> str: ...


class TranslationSubsystem(_BaseSubsystem):
    async def translate(self, text: str, source_lang: str, target_lang: str) -> str: ...
