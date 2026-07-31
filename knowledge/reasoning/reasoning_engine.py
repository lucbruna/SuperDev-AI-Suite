from __future__ import annotations

import logging
from typing import Any

from ..knowledge_config import KnowledgeConfig
from ..knowledge_events import KnowledgeEvents, KnowledgeEventType
from ..knowledge_metrics import KnowledgeMetrics
from .chain_of_thought import ChainOfThought
from .inference import Inference
from .reasoning_tracer import ReasoningTracer
from .rules import Rule, RuleSet


class ReasoningEngine:
    """Composes rule-based inference, chain-of-thought, and tracing."""

    def __init__(
        self,
        config: KnowledgeConfig | None = None,
        events: KnowledgeEvents | None = None,
        metrics: KnowledgeMetrics | None = None,
    ) -> None:
        self._log = logging.getLogger("superdev.knowledge.reasoning.engine")
        self.config = config or KnowledgeConfig()
        self.events = events or KnowledgeEvents()
        self.metrics = metrics or KnowledgeMetrics()
        self.rules = RuleSet()
        self.inference = Inference(self.rules)
        self.chain = ChainOfThought()
        self.tracer = ReasoningTracer()

    def add_rule(self, rule: Rule) -> None:
        self.rules.add(rule)
        self.tracer.trace("rule_added", rule_id=rule.id)

    def add_fact(self, fact: str) -> None:
        self.inference.add_fact(fact)

    def add_facts(self, facts: list[str]) -> None:
        self.inference.add_facts(facts)

    def reason(self, query: str, facts: list[str] | None = None,
               use_chain_of_thought: bool = True) -> dict[str, Any]:
        if facts is not None:
            self.inference.add_facts(facts)
        derived = self.inference.infer()
        all_facts = self.inference.facts()
        conclusion = self._conclude(query, all_facts)
        steps = self.chain.reason(query, all_facts, conclusion) if use_chain_of_thought else []
        result = {
            "query": query,
            "conclusion": conclusion,
            "derived_facts": derived,
            "steps": steps,
            "confidence": self._confidence(all_facts),
        }
        self.tracer.trace("reasoned", query=query, conclusion=conclusion)
        self.metrics.increment("reasoning.executed")
        self.events.emit(KnowledgeEventType.SEARCH_EXECUTED, {"reasoning": query})
        return result

    def _conclude(self, query: str, facts: list[str]) -> str:
        if not facts:
            return "No facts available to reason about."
        query_tokens = set(query.lower().split())
        if not query_tokens:
            return facts[-1]
        best = max(facts, key=lambda fact: self.chain._overlap(fact, query_tokens))
        return best

    def _confidence(self, facts: list[str]) -> float:
        if not facts:
            return 0.0
        return min(1.0, len(facts) / 10.0)

    def stats(self) -> dict[str, Any]:
        return {
            "rules": self.rules.count(),
            "facts": len(self.inference.facts()),
            "traces": self.tracer.count(),
        }
