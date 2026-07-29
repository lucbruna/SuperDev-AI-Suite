from __future__ import annotations

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from .knowledge_config import KnowledgeConfig
from .knowledge_context import KnowledgeContext
from .knowledge_events import KnowledgeEventBus, KnowledgeEvent, EventType
from .knowledge_factory import KnowledgeFactory
from .knowledge_interfaces import (
    ConcreteKnowledgeSource, ConcreteKnowledgeProcessor,
    ConcreteKnowledgeStorage, ConcreteKnowledgeValidator,
)
from .knowledge_logger import KnowledgeLogger, LogLevel
from .knowledge_metrics import KnowledgeMetrics, MetricsCollector
from .knowledge_models import (
    KnowledgeEntry, KnowledgeState, KnowledgeType,
    ResearchQuery, ResearchResult, DocumentAnalysis,
    ValidationResult, ReasoningResult, KnowledgeSummary,
    LearningFeedback, ConfidenceScore, ConfidenceLevel,
)
from .knowledge_protocols import KnowledgeProtocol, ResearchProtocol, ValidationProtocol
from .knowledge_registry import KnowledgeRegistry
from .knowledge_runtime import KnowledgeRuntime, RuntimeState
from .knowledge_security import KnowledgeSecurityManager
from .research_engine import ResearchEngine, EngineConfig as ResearchEngineConfig

logger = logging.getLogger(__name__)


class KnowledgeEngineState(Enum):
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class KnowledgeEngineConfig:
    config: KnowledgeConfig
    event_bus: KnowledgeEventBus
    context: KnowledgeContext
    security: KnowledgeSecurityManager
    logger: KnowledgeLogger
    registry: KnowledgeRegistry
    metrics_collector: MetricsCollector
    auto_start: bool = True
    enable_research: bool = True
    enable_reasoning: bool = True
    enable_learning: bool = True
    max_concurrent_tasks: int = 50


@dataclass
class KnowledgeEngineMetrics:
    state: KnowledgeEngineState = KnowledgeEngineState.INITIALIZING
    start_time: Optional[datetime] = None
    entries_stored: int = 0
    searches_performed: int = 0
    validations_run: int = 0
    reasoning_ops: int = 0
    research_ops: int = 0
    learning_ops: int = 0
    errors: int = 0
    last_action_time: Optional[datetime] = None
    subsystem_status: Dict[str, str] = field(default_factory=dict)


class KnowledgeEngine:
    def __init__(self, config: KnowledgeEngineConfig):
        self.config = config
        self.metrics = KnowledgeEngineMetrics()
        self.event_bus = config.event_bus
        self.context = config.context
        self.security = config.security
        self.logger = config.logger
        self.registry = config.registry
        self.metrics_collector = config.metrics_collector
        self._storage = ConcreteKnowledgeStorage()
        self._processor = ConcreteKnowledgeProcessor()
        self._validator = ConcreteKnowledgeValidator()
        self._source = ConcreteKnowledgeSource()
        self._knowledge_protocol = KnowledgeProtocol(
            self._source, self._processor, self._storage, self._validator
        )
        self._research_protocol = ResearchProtocol(self._source, self._validator)
        self._validation_protocol = ValidationProtocol(self._validator)
        self._research_engine = ResearchEngine(ResearchEngineConfig(
            config=config.config, event_bus=config.event_bus, security=config.security,
        ))
        self._runtime = KnowledgeRuntime(
            config.config, config.event_bus, config.context, config.security, config.registry, config.logger
        )
        self._subsystems: Dict[str, Any] = {}
        self._running = False

    async def initialize(self) -> None:
        self.logger.info("engine", "Initializing Knowledge AI Engine...")
        self.metrics.state = KnowledgeEngineState.INITIALIZING
        self.metrics.start_time = datetime.utcnow()
        await self._initialize_subsystems()
        self.registry.register("knowledge_engine", self, "engine", "core")
        self.metrics.state = KnowledgeEngineState.RUNNING
        self.logger.info("engine", "Knowledge AI Engine initialized")

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        await self._runtime.start()
        self.logger.info("engine", "Knowledge AI Engine started")

    async def stop(self) -> None:
        self.logger.info("engine", "Stopping Knowledge AI Engine...")
        self._running = False
        await self._runtime.stop()
        await self._shutdown_subsystems()
        self.metrics.state = KnowledgeEngineState.STOPPED
        self.logger.info("engine", "Knowledge AI Engine stopped")

    async def pause(self) -> None:
        self._running = False
        await self._runtime.pause()
        self.metrics.state = KnowledgeEngineState.PAUSED

    async def resume(self) -> None:
        self._running = True
        await self._runtime.resume()
        self.metrics.state = KnowledgeEngineState.RUNNING

    async def process_knowledge(self, entry: KnowledgeEntry) -> KnowledgeEntry:
        result = await self._knowledge_protocol.execute(entry)
        self.metrics.entries_stored += 1
        self.metrics_collector.increment_entries()
        await self.event_bus.publish(KnowledgeEvent(
            event_type=EventType.KNOWLEDGE_CREATED,
            payload={"entry_id": entry.id, "title": entry.title},
            source="engine",
        ))
        return result

    async def search(self, query: str, domain: str = "general",
                      limit: int = 10) -> List[KnowledgeEntry]:
        self.metrics.searches_performed += 1
        self.metrics_collector.metrics.queries_executed += 1
        results = await self._storage.query(query, limit)
        domain_filtered = [r for r in results if r.domain == domain or domain == "general"]
        return domain_filtered[:limit]

    async def store(self, entry: KnowledgeEntry) -> KnowledgeEntry:
        validated = await self._validator.validate(entry)
        if validated.valid:
            entry.state = KnowledgeState.ACTIVE
            entry.confidence = validated.confidence
        await self._storage.store(entry)
        self.metrics.entries_stored += 1
        self.metrics_collector.increment_entries()
        if entry.state == KnowledgeState.ACTIVE:
            self.metrics_collector.increment_active()
        self.metrics_collector.record_confidence(entry.confidence)
        await self.event_bus.publish(KnowledgeEvent(
            event_type=EventType.KNOWLEDGE_CREATED,
            payload={"entry_id": entry.id, "state": entry.state.value},
            source="engine",
        ))
        return entry

    async def retrieve(self, entry_id: str) -> Optional[KnowledgeEntry]:
        return await self._storage.retrieve(entry_id)

    async def learn(self, feedback: LearningFeedback) -> bool:
        self.metrics.learning_ops += 1
        self.metrics_collector.increment_learning()
        entry = await self._storage.retrieve(feedback.entry_id)
        if not entry:
            return False
        entry.metadata["last_feedback"] = feedback.score
        entry.metadata["feedback_count"] = entry.metadata.get("feedback_count", 0) + 1
        await self._storage.store(entry)
        await self.event_bus.publish(KnowledgeEvent(
            event_type=EventType.LEARNING_APPLIED,
            payload={"entry_id": entry.id, "score": feedback.score},
            source="engine",
        ))
        return True

    async def reason(self, query: str, context: Optional[Dict[str, Any]] = None) -> ReasoningResult:
        self.metrics.reasoning_ops += 1
        self.metrics_collector.increment_reasoning()
        result = ReasoningResult(
            id=str(uuid.uuid4()),
            query=query,
            conclusion=f"Reasoned conclusion for: {query}",
            confidence=0.7,
            reasoning_type="deductive",
        )
        await self.event_bus.publish(KnowledgeEvent(
            event_type=EventType.REASONING_COMPLETED,
            payload={"result_id": result.id, "query": query},
            source="engine",
        ))
        return result

    async def validate(self, entry: KnowledgeEntry) -> ValidationResult:
        self.metrics.validations_run += 1
        self.metrics_collector.increment_validations()
        result = await self._validator.validate(entry)
        await self.event_bus.publish(KnowledgeEvent(
            event_type=EventType.VALIDATION_COMPLETED,
            payload={"entry_id": entry.id, "valid": result.valid},
            source="engine",
        ))
        return result

    async def research(self, query: ResearchQuery) -> ResearchResult:
        self.metrics.research_ops += 1
        self.metrics_collector.increment_research()
        return await self._research_engine.conduct_research(query)

    async def analyze(self, document_id: str, content: str,
                       title: str = "") -> DocumentAnalysis:
        self.metrics_collector.increment_documents()
        analysis = DocumentAnalysis(
            id=str(uuid.uuid4()),
            document_id=document_id,
            title=title,
            content=content,
            word_count=len(content.split()),
            page_count=max(1, len(content) // 3000),
            confidence=0.7,
        )
        await self.event_bus.publish(KnowledgeEvent(
            event_type=EventType.DOCUMENT_ANALYZED,
            payload={"document_id": document_id, "analysis_id": analysis.id},
            source="engine",
        ))
        return analysis

    async def get_summary(self) -> KnowledgeSummary:
        entries = await self._storage.query("", 10000)
        active = [e for e in entries if e.state == KnowledgeState.ACTIVE]
        by_type: Dict[str, int] = {}
        by_domain: Dict[str, int] = {}
        by_state: Dict[str, int] = {}
        for e in entries:
            by_type[e.knowledge_type.value] = by_type.get(e.knowledge_type.value, 0) + 1
            by_domain[e.domain] = by_domain.get(e.domain, 0) + 1
            by_state[e.state.value] = by_state.get(e.state.value, 0) + 1
        confidences = [e.confidence for e in entries if e.confidence > 0]
        avg_conf = sum(confidences) / max(len(confidences), 1)
        return KnowledgeSummary(
            total_entries=len(entries),
            active_entries=len(active),
            by_type=by_type,
            by_domain=by_domain,
            by_state=by_state,
            avg_confidence=avg_conf,
            graph_nodes=self.metrics_collector.metrics.graph_nodes,
            graph_edges=self.metrics_collector.metrics.graph_edges,
        )

    def get_status(self) -> Dict[str, Any]:
        metrics = self.metrics
        return {
            "state": metrics.state.value,
            "uptime_seconds": (datetime.utcnow() - metrics.start_time).total_seconds() if metrics.start_time else 0,
            "entries_stored": metrics.entries_stored,
            "searches_performed": metrics.searches_performed,
            "validations_run": metrics.validations_run,
            "reasoning_ops": metrics.reasoning_ops,
            "research_ops": metrics.research_ops,
            "learning_ops": metrics.learning_ops,
            "errors": metrics.errors,
            "subsystems": metrics.subsystem_status,
        }

    def get_subsystem(self, name: str):
        return self._subsystems.get(name)

    async def _initialize_subsystems(self) -> None:
        self._subsystems = {
            "research": self._research_engine,
            "storage": self._storage,
            "processor": self._processor,
            "validator": self._validator,
            "source": self._source,
            "runtime": self._runtime,
        }
        for name, sub in self._subsystems.items():
            self.metrics.subsystem_status[name] = "initialized"
            self.registry.register(name, sub, "subsystem", "knowledge_engine")

    async def _shutdown_subsystems(self) -> None:
        for name, sub in self._subsystems.items():
            try:
                self.metrics.subsystem_status[name] = "stopped"
            except Exception as e:
                self.logger.error("engine", f"Error shutting down {name}: {e}")