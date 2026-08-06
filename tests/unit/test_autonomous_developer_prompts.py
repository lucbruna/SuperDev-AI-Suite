"""Tests for the deterministic prompt library (Phase F)."""
from __future__ import annotations

import pytest

from modules.autonomous_developer.prompts import PromptError, PromptLibrary


class TestPromptLibrary:
    def test_names(self):
        assert PromptLibrary().names() == [
            "system",
            "plan",
            "implement",
            "review",
            "test",
        ]

    def test_template_lookup(self):
        tmpl = PromptLibrary().template("plan")
        assert tmpl.name == "plan"
        assert tmpl.variables == ("goal",)

    def test_render_system(self):
        assert (
            PromptLibrary().render("system", role="coder")
            == "You are the coder. Stay deterministic and precise."
        )

    def test_render_plan(self):
        assert (
            PromptLibrary().render("plan", goal="Build X")
            == "Decompose the goal into small, verifiable tasks.\nGoal: Build X"
        )

    def test_render_implement(self):
        assert (
            PromptLibrary().render("implement", title="Fix bug")
            == "Implement the task titled 'Fix bug'."
        )

    def test_render_review(self):
        assert (
            PromptLibrary().render("review", count=3)
            == "Review 3 file change(s) and return a verdict."
        )

    def test_render_test(self):
        assert (
            PromptLibrary().render("test", module="app")
            == "Generate a pytest module for 'app'."
        )

    def test_extra_kwargs_ignored(self):
        assert PromptLibrary().render("plan", goal="G", extra=1) == (
            "Decompose the goal into small, verifiable tasks.\nGoal: G"
        )

    def test_missing_variable_raises(self):
        with pytest.raises(PromptError):
            PromptLibrary().render("plan")

    def test_unknown_template_raises(self):
        with pytest.raises(PromptError):
            PromptLibrary().render("nope", goal="x")

    def test_prompt_error_is_value_error(self):
        assert issubclass(PromptError, ValueError)
