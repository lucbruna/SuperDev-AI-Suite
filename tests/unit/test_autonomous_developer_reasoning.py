"""Unit tests for the Autonomous Developer reasoning engine (Phase E)."""
from __future__ import annotations

import pytest

from modules.autonomous_developer.config.developer_config import DeveloperConfig
from modules.autonomous_developer.core.context import DeveloperContext
from modules.autonomous_developer.core.exceptions import GenerationError
from modules.autonomous_developer.core.registry import DeveloperRegistry
from modules.autonomous_developer.reasoning import ReasoningEngine, decompose, score_options


class TestDecompose:
    def test_single_goal(self) -> None:
        assert decompose("Add login") == ["Add login"]

    def test_sentence_split(self) -> None:
        assert decompose("Add auth. Add dashboard") == ["Add auth", "Add dashboard"]

    def test_line_split(self) -> None:
        assert decompose("one\ntwo\nthree") == ["one", "two", "three"]

    def test_whitespace_cleaned(self) -> None:
        assert decompose("  spaced  ") == ["spaced"]

    def test_empty_goal(self) -> None:
        assert decompose("") == []

    def test_blank_goal(self) -> None:
        assert decompose("   ") == []


class TestScoreOptions:
    def test_scores_by_matched_criteria(self) -> None:
        scores = score_options(
            ["fast and safe", "slow", "fast"],
            {"fast": 2.0, "safe": 1.0},
        )
        assert [entry["option"] for entry in scores] == ["fast and safe", "fast", "slow"]
        assert scores[0]["score"] == 3.0
        assert scores[0]["matched"] == ["fast", "safe"]
        assert scores[2]["score"] == 0.0

    def test_stable_ties_keep_original_order(self) -> None:
        scores = score_options(["fast", "also fast"], {"fast": 1.0})
        assert [entry["option"] for entry in scores] == ["fast", "also fast"]

    def test_empty_options(self) -> None:
        assert score_options([], {"fast": 1.0}) == []

    def test_empty_criteria(self) -> None:
        scores = score_options(["a", "b"], {})
        assert [entry["score"] for entry in scores] == [0.0, 0.0]


class TestReason:
    def test_reason_with_options(self) -> None:
        result = ReasoningEngine().reason(
            "Choose an approach",
            options=["fast path", "safe path"],
            criteria={"fast": 1.0},
        )
        assert result.selected == "fast path"
        assert "score 1.0" in result.rationale
        assert result.steps == ["Choose an approach"]

    def test_reason_without_options(self) -> None:
        result = ReasoningEngine().reason("Just do it")
        assert result.selected == ""
        assert result.rationale == "No options were provided to choose from."

    def test_reason_decomposes_goal(self) -> None:
        result = ReasoningEngine().reason("Plan. Build. Ship.")
        assert result.steps == ["Plan", "Build", "Ship"]


class TestRun:
    def _context(self, tmp_path) -> DeveloperContext:
        config = DeveloperConfig(project_root=str(tmp_path))
        return DeveloperContext(config=config, registry=DeveloperRegistry())

    def test_run_without_goal_raises(self, tmp_path) -> None:
        ctx = self._context(tmp_path)
        with pytest.raises(GenerationError, match="A goal is required"):
            ReasoningEngine().run(ctx, "")

    def test_run_records_and_publishes(self, tmp_path) -> None:
        ctx = self._context(tmp_path)
        result = ReasoningEngine().run(
            ctx,
            "Choose an approach",
            options=["fast path", "safe path"],
            criteria={"fast": 1.0},
        )
        assert result.selected == "fast path"
        assert ctx.stats["reasoning_steps"] == 1
        assert ctx.stats["reasoning_options"] == 2
        assert ctx.stats["reasoning_selected"] == "fast path"
        events = [e.type for e in ctx.bus.history(event_type="reasoning.completed")]
        assert events == ["reasoning.completed"]
