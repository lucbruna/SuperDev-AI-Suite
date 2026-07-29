from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .pdf_analyzer import PDFAnalyzer
from .document_parser import DocumentParser
from .summary_generator import SummaryGenerator
from .information_extractor import InformationExtractor


class EngineState(Enum):
    IDLE = "idle"
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass
class EngineConfig:
    max_file_size_mb: int = 50
    supported_formats: tuple[str, ...] = ("pdf", "txt", "docx", "html", "md", "json")
    extract_metadata: bool = True
    generate_summary: bool = True
    ocr_enabled: bool = False


@dataclass
class EngineMetrics:
    total_documents_processed: int = 0
    successful_analyses: int = 0
    failed_analyses: int = 0
    total_pages_processed: int = 0
    average_processing_time_ms: float = 0.0
    active_analyses: int = 0


class DocumentEngine:
    def __init__(self, config: EngineConfig | None = None) -> None:
        self.config = config or EngineConfig()
        self.state = EngineState.IDLE
        self.metrics = EngineMetrics()
        self.pdf_analyzer = PDFAnalyzer()
        self.parser = DocumentParser()
        self.summary_generator = SummaryGenerator()
        self.extractor = InformationExtractor()
        self._lock = asyncio.Lock()

    async def initialize(self) -> None:
        self.state = EngineState.INITIALIZING
        await asyncio.sleep(0.01)
        self.state = EngineState.READY

    async def stop(self) -> None:
        self.state = EngineState.STOPPING
        await asyncio.sleep(0.01)
        self.state = EngineState.IDLE

    async def analyze_document(self, content: str, format: str = "txt") -> dict[str, Any]:
        if self.state != EngineState.READY:
            raise RuntimeError(f"Engine not ready, current state: {self.state.value}")

        async with self._lock:
            self.state = EngineState.RUNNING
            self.metrics.active_analyses += 1

        try:
            start = asyncio.get_event_loop().time()

            parsed = await self.parser.parse(content, format)
            extracted = await self.extractor.extract_entities(parsed["content"])
            summary = await self.summary_generator.generate_summary(parsed["content"])

            elapsed = (asyncio.get_event_loop().time() - start) * 1000
            self.metrics.total_documents_processed += 1
            self.metrics.successful_analyses += 1
            self.metrics.total_pages_processed += 1
            prev = self.metrics.average_processing_time_ms
            count = self.metrics.total_documents_processed
            self.metrics.average_processing_time_ms = prev + (elapsed - prev) / count

            return {
                "parsed": parsed,
                "extracted": extracted,
                "summary": summary,
                "elapsed_ms": elapsed,
            }
        except Exception:
            self.metrics.failed_analyses += 1
            raise
        finally:
            async with self._lock:
                self.metrics.active_analyses -= 1
                self.state = EngineState.READY

    async def process(self, content: str, format: str = "txt") -> dict[str, Any]:
        return await self.analyze_document(content, format)

    async def extract_information(self, content: str) -> dict[str, Any]:
        parsed = await self.parser.parse(content, "txt")
        return await self.extractor.extract_entities(parsed["content"])

    async def generate_summary(self, content: str, style: str = "standard") -> dict[str, Any]:
        parsed = await self.parser.parse(content, "txt")
        return await self.summary_generator.generate_summary(parsed["content"])