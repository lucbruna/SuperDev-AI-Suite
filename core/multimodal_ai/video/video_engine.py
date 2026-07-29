from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class VideoEngineState(Enum):
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    READY = "ready"
    PROCESSING = "processing"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class VideoEngineConfig:
    model_path: str = "models/video/default"
    device: str = "cpu"
    batch_size: int = 4
    frame_sample_rate: int = 30
    max_duration_seconds: int = 3600
    enable_gpu: bool = False
    num_workers: int = 2
    cache_enabled: bool = True
    log_level: str = "INFO"
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class VideoEngineMetrics:
    total_videos_processed: int = 0
    total_frames_analyzed: int = 0
    total_activities_detected: int = 0
    total_events_recognized: int = 0
    total_errors: int = 0
    average_processing_time_ms: float = 0.0
    fps_processing: float = 0.0
    uptime_seconds: float = 0.0
    last_processed_timestamp: str | None = None


class VideoEngine:
    def __init__(self, config: VideoEngineConfig | None = None) -> None:
        self.config = config or VideoEngineConfig()
        self.state = VideoEngineState.UNINITIALIZED
        self.metrics = VideoEngineMetrics()
        self._start_time: float = 0.0
        self._frame_analyzer: FrameAnalyzer | None = None
        self._activity_detector: ActivityDetector | None = None
        self._event_recognizer: EventRecognizer | None = None
        self._summarizer: VideoSummarizer | None = None
        self._processing_lock = asyncio.Lock()

    async def initialize(self) -> None:
        self.state = VideoEngineState.INITIALIZING
        logger.info("Initializing VideoEngine...")
        try:
            from .frame_analyzer import FrameAnalyzer
            from .activity_detection import ActivityDetector
            from .event_recognition import EventRecognizer
            from .video_summary import VideoSummarizer

            await asyncio.sleep(0.05)
            self._frame_analyzer = FrameAnalyzer()
            self._activity_detector = ActivityDetector()
            self._event_recognizer = EventRecognizer()
            self._summarizer = VideoSummarizer()
            self._start_time = asyncio.get_event_loop().time()
            self.state = VideoEngineState.READY
            logger.info("VideoEngine initialized successfully")
        except Exception as e:
            self.state = VideoEngineState.ERROR
            logger.exception("Failed to initialize VideoEngine")
            raise RuntimeError(f"VideoEngine initialization failed: {e}") from e

    async def stop(self) -> None:
        self.state = VideoEngineState.STOPPING
        logger.info("Stopping VideoEngine...")
        await asyncio.sleep(0.02)
        self._frame_analyzer = None
        self._activity_detector = None
        self._event_recognizer = None
        self._summarizer = None
        self.metrics.uptime_seconds = asyncio.get_event_loop().time() - self._start_time
        self.state = VideoEngineState.STOPPED
        logger.info("VideoEngine stopped")

    async def process_video(self, video_data: bytes | str, options: dict[str, Any] | None = None) -> dict[str, Any]:
        if self.state not in (VideoEngineState.READY, VideoEngineState.PROCESSING):
            raise RuntimeError(f"Engine is not ready (state={self.state.value})")
        self.state = VideoEngineState.PROCESSING
        opts = options or {}
        try:
            start = asyncio.get_event_loop().time()
            result: dict[str, Any] = {"video_id": id(video_data), "status": "processed"}
            if self._frame_analyzer:
                result["frames"] = await self._frame_analyzer.extract_frames(video_data, count=10)
            if opts.get("detect_activity", True) and self._activity_detector:
                result["activities"] = await self._activity_detector.detect_activity(video_data)
            if opts.get("recognize_events", True) and self._event_recognizer:
                result["events"] = await self._event_recognizer.recognize_event(video_data)
            elapsed = (asyncio.get_event_loop().time() - start) * 1000
            self.metrics.total_videos_processed += 1
            self.metrics.average_processing_time_ms = (
                self.metrics.average_processing_time_ms * (self.metrics.total_videos_processed - 1) + elapsed
            ) / self.metrics.total_videos_processed
            self.state = VideoEngineState.READY
            return result
        except Exception as e:
            self.metrics.total_errors += 1
            self.state = VideoEngineState.READY
            return {"video_id": id(video_data), "status": "error", "error": str(e)}

    async def analyze_frames(self, video_data: bytes | str, frame_count: int = 10) -> list[dict[str, Any]]:
        if self._frame_analyzer is None:
            raise RuntimeError("Engine not initialized")
        result = await self._frame_analyzer.extract_frames(video_data, count=frame_count)
        self.metrics.total_frames_analyzed += len(result)
        return result

    async def detect_activity(self, video_data: bytes | str) -> list[dict[str, Any]]:
        if self._activity_detector is None:
            raise RuntimeError("Engine not initialized")
        result = await self._activity_detector.detect_activity(video_data)
        self.metrics.total_activities_detected += len(result)
        return result

    async def recognize_event(self, video_data: bytes | str) -> list[dict[str, Any]]:
        if self._event_recognizer is None:
            raise RuntimeError("Engine not initialized")
        result = await self._event_recognizer.recognize_event(video_data)
        self.metrics.total_events_recognized += len(result)
        return result

    async def get_metrics(self) -> VideoEngineMetrics:
        if self.state != VideoEngineState.STOPPED:
            self.metrics.uptime_seconds = asyncio.get_event_loop().time() - self._start_time
        return self.metrics
