from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from .inference import InferenceEngine
from .hypothesis_builder import HypothesisBuilder
from .conclusion_engine import ConclusionEngine

logger = logging.getLogger(__name__)


class EngineState(Enum):
    STOPPED = "stopped"
    INITIALIZING = "initializing"
    RUNNING = "running"
    ERROR = "error"


@dataclass
class EngineConfig:
    max_reasoning_depth: int = 10
    confidence_threshold: float = 0.6
    enable_abductive_reasoning: bool = True
    enable_inductive_reasoning: bool = True
    hypothesis_limit: int = 5


@dataclass
class EngineMetrics:
    total_reasoning_chains: int = 0
    active_chains: int = 0
    completed_chains: int = 0
    failed_chains: int = 0
    average_confidence: float = 0.0
    total_inferences: int = 0


class ReasoningChain:
    def __init__(self, chain_id: str, premises: list[str]) -> None:
        self.chain_id = chain_id
        self.premises = premises
        self.steps: list[dict[str, Any]] = []
        self.conclusion: Optional[str] = None
        self.confidence: float = 0.0
        self.completed: bool = False

    def add_step(self, step: dict[str, Any]) -> None:
        self.steps.append(step)

    def to_dict(self) -> dict[str, Any]:
        return {
            "chain_id": self.chain_id,
            "premises": self.premises,
            "steps": self.steps,
            "conclusion": self.conclusion,
            "confidence": self.confidence,
            "completed": self.completed,
        }


class ReasoningEngine:
    def __init__(self, config: Optional[EngineConfig] = None) -> None:
        self.config = config or EngineConfig()
        self.state = EngineState.STOPPED
        self.metrics = EngineMetrics()
        self.inference_engine = InferenceEngine()
        self.hypothesis_builder = HypothesisBuilder()
        self.conclusion_engine = ConclusionEngine()
        self._chains: dict[str, ReasoningChain] = {}

    async def initialize(self) -> None:
        self.state = EngineState.INITIALIZING
        await self.inference_engine.initialize()
        await self.hypothesis_builder.initialize()
        await self.conclusion_engine.initialize()
        self.state = EngineState.RUNNING
        logger.info("ReasoningEngine initialized")

    async def stop(self) -> None:
        self.state = EngineState.STOPPED
        self._chains.clear()
        await self.inference_engine.stop()
        await self.hypothesis_builder.stop()
        await self.conclusion_engine.stop()
        logger.info("ReasoningEngine stopped")

    async def reason(self, premises: list[str], depth: int = 3) -> ReasoningChain:
        if self.state != EngineState.RUNNING:
            raise RuntimeError("ReasoningEngine is not running")

        chain_id = str(uuid.uuid4())
        chain = ReasoningChain(chain_id=chain_id, premises=premises)

        current_depth = min(depth, self.config.max_reasoning_depth)
        for d in range(current_depth):
            if not premises:
                break
            inference_result = await self.inference_engine.infer(premises)
            chain.add_step({
                "depth": d,
                "inference": inference_result,
            })
            premises = inference_result.get("conclusions", [])

        hypothesis = await self.hypothesis_builder.build_hypothesis(premises or chain.premises)
        chain.add_step({"hypothesis": hypothesis})

        conclusion = await self.conclusion_engine.draw_conclusion(
            premises or chain.premises, hypothesis
        )
        chain.conclusion = conclusion.get("conclusion")
        chain.confidence = conclusion.get("confidence", 0.0)
        chain.completed = True

        self._chains[chain_id] = chain
        self.metrics.total_reasoning_chains += 1
        self.metrics.completed_chains += 1
        self._update_average_confidence(chain.confidence)

        return chain

    async def analyze(self, data: dict[str, Any]) -> dict[str, Any]:
        premises = data.get("premises", [])
        chain = await self.reason(premises)
        return {
            "chain_id": chain.chain_id,
            "analysis": chain.to_dict(),
        }

    async def compare(self, items: list[Any], criteria: list[str]) -> list[dict[str, Any]]:
        results = []
        for item in items:
            premises = [f"{c}: {item.get(c, 'unknown')}" for c in criteria]
            chain = await self.reason(premises, depth=2)
            results.append({
                "item": item,
                "assessment": chain.conclusion,
                "confidence": chain.confidence,
            })
        return sorted(results, key=lambda r: r["confidence"], reverse=True)

    async def evaluate(self, statement: str, evidence: list[str]) -> dict[str, Any]:
        premises = [statement] + evidence
        chain = await self.reason(premises, depth=3)
        return {
            "statement": statement,
            "verdict": chain.conclusion,
            "confidence": chain.confidence,
            "reasoning_steps": len(chain.steps),
        }

    async def get_reasoning_chain(self, chain_id: str) -> Optional[ReasoningChain]:
        return self._chains.get(chain_id)

    def _update_average_confidence(self, confidence: float) -> None:
        total = self.metrics.total_reasoning_chains
        if total > 1:
            prev_avg = self.metrics.average_confidence
            self.metrics.average_confidence = prev_avg + (confidence - prev_avg) / total
        else:
            self.metrics.average_confidence = confidence
