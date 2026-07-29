from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class EngineState(Enum):
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    READY = "ready"
    PROCESSING = "processing"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class EngineConfig:
    model_path: str = "models/vision/default"
    device: str = "cpu"
    batch_size: int = 1
    confidence_threshold: float = 0.5
    max_image_size: int = 1920
    enable_gpu: bool = False
    num_workers: int = 2
    cache_enabled: bool = True
    log_level: str = "INFO"
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class EngineMetrics:
    total_images_processed: int = 0
    total_objects_detected: int = 0
    total_inspections: int = 0
    total_errors: int = 0
    average_processing_time_ms: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    uptime_seconds: float = 0.0
    last_processed_timestamp: str | None = None


class VisionEngine:
    def __init__(self, config: EngineConfig | None = None) -> None:
        self.config = config or EngineConfig()
        self.state = EngineState.UNINITIALIZED
        self.metrics = EngineMetrics()
        self._start_time: float = 0.0
        self._analyzer: ImageAnalyzer | None = None
        self._detector: ObjectDetector | None = None
        self._inspector: QualityInspector | None = None
        self._understanding: ImageUnderstanding | None = None
        self._processing_lock = asyncio.Lock()

    async def initialize(self) -> None:
        self.state = EngineState.INITIALIZING
        logger.info("Initializing VisionEngine...")
        try:
            from .image_analyzer import ImageAnalyzer
            from .object_detection import ObjectDetector
            from .quality_inspection import QualityInspector
            from .image_understanding import ImageUnderstanding

            await asyncio.sleep(0.05)
            self._analyzer = ImageAnalyzer()
            self._detector = ObjectDetector()
            self._inspector = QualityInspector()
            self._understanding = ImageUnderstanding()
            self._start_time = asyncio.get_event_loop().time()
            self.state = EngineState.READY
            logger.info("VisionEngine initialized successfully")
        except Exception as e:
            self.state = EngineState.ERROR
            logger.exception("Failed to initialize VisionEngine")
            raise RuntimeError(f"VisionEngine initialization failed: {e}") from e

    async def stop(self) -> None:
        self.state = EngineState.STOPPING
        logger.info("Stopping VisionEngine...")
        await asyncio.sleep(0.02)
        self._analyzer = None
        self._detector = None
        self._inspector = None
        self._understanding = None
        self.metrics.uptime_seconds = asyncio.get_event_loop().time() - self._start_time
        self.state = EngineState.STOPPED
        logger.info("VisionEngine stopped")

    async def process_image(self, image_data: bytes | str, options: dict[str, Any] | None = None) -> dict[str, Any]:
        if self.state not in (EngineState.READY, EngineState.PROCESSING):
            raise RuntimeError(f"Engine is not ready (state={self.state.value})")
        self.state = EngineState.PROCESSING
        opts = options or {}
        try:
            start = asyncio.get_event_loop().time()
            result: dict[str, Any] = {"image_id": id(image_data), "status": "processed"}
            if self._analyzer:
                result["analysis"] = await self._analyzer.analyze_image(image_data)
            if opts.get("detect_objects", True) and self._detector:
                result["objects"] = await self._detector.detect_objects(image_data)
            if opts.get("inspect_quality", False) and self._inspector:
                result["quality"] = await self._inspector.inspect_product(image_data)
            elapsed = (asyncio.get_event_loop().time() - start) * 1000
            self.metrics.total_images_processed += 1
            self.metrics.average_processing_time_ms = (
                self.metrics.average_processing_time_ms * (self.metrics.total_images_processed - 1) + elapsed
            ) / self.metrics.total_images_processed
            self.state = EngineState.READY
            return result
        except Exception as e:
            self.metrics.total_errors += 1
            self.state = EngineState.READY
            return {"image_id": id(image_data), "status": "error", "error": str(e)}

    async def analyze(self, image_data: bytes | str) -> dict[str, Any]:
        if self._analyzer is None:
            raise RuntimeError("Engine not initialized")
        self.metrics.total_images_processed += 1
        return await self._analyzer.analyze_image(image_data)

    async def detect_objects(self, image_data: bytes | str) -> list[dict[str, Any]]:
        if self._detector is None:
            raise RuntimeError("Engine not initialized")
        result = await self._detector.detect_objects(image_data)
        self.metrics.total_objects_detected += len(result)
        return result

    async def inspect_quality(self, image_data: bytes | str) -> dict[str, Any]:
        if self._inspector is None:
            raise RuntimeError("Engine not initialized")
        self.metrics.total_inspections += 1
        return await self._inspector.inspect_product(image_data)

    async def get_metrics(self) -> EngineMetrics:
        if self.state != EngineState.STOPPED:
            self.metrics.uptime_seconds = asyncio.get_event_loop().time() - self._start_time
        return self.metrics
