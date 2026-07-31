"""Tests for the knowledge reasoning subsystem."""

from __future__ import annotations

import pytest

from knowledge.reasoning import (
    ChainOfThought,
    Inference,
    ReasoningEngine,
    ReasoningTracer,
    Rule,
    RuleSet,
)


class TestRuleSet:
    def test_add_remove_get(self) -> None:
        rules = RuleSet()
        rule = Rule(id="r1", antecedents=["a"], consequent="b")
        rules.add(rule)
        assert rules.get("r1") is rule
        assert rules.count() == 1
        assert rules.remove("r1") is True
        assert rules.remove("r1") is False
        assert rules.count() == 0

    def test_matching(self) -> None:
        rules = RuleSet()
        rules.add(Rule(id="r1", antecedents=["login"], consequent="needs_auth"))
        rules.add(Rule(id="r2", antecedents=["admin"], consequent="full_access"))
        matched = rules.matching({"user login failed"})
        assert [rule.id for rule in matched] == ["r1"]

    def test_clear(self) -> None:
        rules = RuleSet()
        rules.add(Rule(id="r1", antecedents=["a"], consequent="b"))
        rules.clear()
        assert rules.count() == 0


class TestInference:
    def test_forward_chaining(self) -> None:
        inference = Inference()
        inference.add_fact("servidor ativo")
        inference.add_rule(Rule(id="r1", antecedents=["servidor"], consequent="pode_receber_trafego"))
        inference.add_rule(
            Rule(id="r2", antecedents=["pode_receber_trafego"], consequent="saudavel")
        )
        derived = inference.infer()
        assert "pode_receber_trafego" in derived
        assert "saudavel" in derived

    def test_add_facts_and_reset(self) -> None:
        inference = Inference()
        inference.add_facts(["alpha", "beta"])
        assert inference.facts() == ["alpha", "beta"]
        inference.reset()
        assert inference.facts() == []


class TestChainOfThought:
    def test_reason_steps(self) -> None:
        chain = ChainOfThought(max_steps=3)
        steps = chain.reason("deploy automatico", ["deploy automatico", "manual guiado"], conclusion="usar automatico")
        assert len(steps) >= 2
        assert steps[0]["output"] == "deploy automatico"
        assert steps[-1]["output"] == "usar automatico"

    def test_reason_orders_by_relevance(self) -> None:
        chain = ChainOfThought(max_steps=3)
        steps = chain.reason("deploy rapido", ["deploy manual", "deploy automatico"])
        # both facts share "deploy"; stable sort keeps original order on ties
        assert [step["output"] for step in steps] == ["deploy manual", "deploy automatico"]

    def test_reason_without_conclusion(self) -> None:
        chain = ChainOfThought(max_steps=2)
        steps = chain.reason("query", ["fato um", "fato dois"])
        assert len(steps) == 2
        assert all("step" in step for step in steps)


class TestReasoningTracer:
    def test_trace_and_list(self) -> None:
        tracer = ReasoningTracer()
        tracer.trace("rule_added", rule_id="r1")
        tracer.trace("reasoned", query="q")
        assert tracer.count() == 2
        assert len(tracer.list("reasoned")) == 1
        assert tracer.list("missing") == []

    def test_max_traces(self) -> None:
        tracer = ReasoningTracer(max_traces=2)
        for index in range(5):
            tracer.trace("op", index=index)
        assert tracer.count() == 2
        tracer.clear()
        assert tracer.count() == 0


class TestReasoningEngine:
    def test_reason_with_rules_and_facts(self) -> None:
        engine = ReasoningEngine()
        engine.add_rule(Rule(id="r1", antecedents=["usuario"], consequent="logado"))
        engine.add_fact("usuario autenticado")
        result = engine.reason("usuario", use_chain_of_thought=True)
        assert result["query"] == "usuario"
        assert result["conclusion"]
        assert result["confidence"] > 0.0

    def test_reason_without_chain(self) -> None:
        engine = ReasoningEngine()
        engine.add_facts(["fato relevante"])
        result = engine.reason("fato", use_chain_of_thought=False)
        assert result["steps"] == []

    def test_stats(self) -> None:
        engine = ReasoningEngine()
        engine.add_rule(Rule(id="r1", antecedents=["a"], consequent="b"))
        engine.add_fact("alpha")
        stats = engine.stats()
        assert stats["rules"] == 1
        assert stats["facts"] == 1
        assert stats["traces"] >= 1
