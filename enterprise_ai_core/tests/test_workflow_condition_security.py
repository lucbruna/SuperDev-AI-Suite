"""Security regression tests: workflow step conditions are evaluated without eval().

Cobre OWASP A03 (Injection) — o evaluator AST-safe bloqueia chamadas,
imports, atributos e escapes de sandbox clássicos do Python.
"""

from __future__ import annotations

from types import SimpleNamespace

from enterprise_ai_core.workflow_engine import WorkflowEngine


def _engine() -> WorkflowEngine:
    return WorkflowEngine(SimpleNamespace(config=None))


class TestSafeConditionEvaluation:
    def test_arithmetic_and_comparison(self) -> None:
        engine = _engine()
        assert engine._evaluate_condition("score > 5", {"score": 10}) is True
        assert engine._evaluate_condition("score > 5", {"score": 3}) is False
        assert engine._evaluate_condition("score * 2 == 20", {"score": 10}) is True

    def test_boolean_and_strings(self) -> None:
        engine = _engine()
        assert (
            engine._evaluate_condition(
                "status == 'completed' and score >= 0.9",
                {"status": "completed", "score": 0.95},
            )
            is True
        )
        assert engine._evaluate_condition("role == 'admin'", {"role": "user"}) is False

    def test_membership_in_constant_list(self) -> None:
        engine = _engine()
        assert (
            engine._evaluate_condition("role in ['admin', 'superuser']", {"role": "admin"})
            is True
        )
        assert (
            engine._evaluate_condition("role in ['admin', 'superuser']", {"role": "user"})
            is False
        )
        assert (
            engine._evaluate_condition("status not in ('failed', 'cancelled')", {"status": "ok"})
            is True
        )

    def test_unknown_name_returns_false(self) -> None:
        engine = _engine()
        assert engine._evaluate_condition("missing > 1", {}) is False

    def test_code_injection_blocked(self) -> None:
        engine = _engine()
        assert engine._evaluate_condition("__import__('os').system('echo pwned')", {}) is False
        assert engine._evaluate_condition("exec('import os')", {}) is False
        assert engine._evaluate_condition("eval('1+1')", {}) is False

    def test_sandbox_escape_blocked(self) -> None:
        engine = _engine()
        assert engine._evaluate_condition("().__class__.__bases__[0].__subclasses__()", {}) is False
        assert engine._evaluate_condition("getattr(open, '__call__')", {}) is False
