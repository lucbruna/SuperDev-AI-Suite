"""Security regression tests: AgentInspector.evaluate_watch is sandboxed (read-only).

Cobre OWASP A03 (Injection) — o evaluator AST-safe permite nomes, constantes,
operadores, caminhos de atributo não-underscore e índices constantes, e bloqueia
chamadas, imports e acesso a dunders/atributos privados.
"""

from __future__ import annotations

import asyncio
from types import SimpleNamespace

from ai.debugger.inspector import AgentInspector


def _evaluate(expression: str, variables: dict) -> str:
    return asyncio.run(AgentInspector().evaluate_watch(expression, variables))


class TestSafeWatchEvaluation:
    def test_arithmetic_and_comparison(self) -> None:
        assert _evaluate("score > 5", {"score": 10}) == "True"
        assert _evaluate("score * 2", {"score": 3}) == "6"

    def test_attribute_path(self) -> None:
        agent = SimpleNamespace(status="running", name="billing")
        assert _evaluate("agent.status", {"agent": agent}) == "running"
        assert _evaluate("agent.name == 'billing'", {"agent": agent}) == "True"

    def test_constant_index(self) -> None:
        assert _evaluate("rows[0]", {"rows": ["a", "b"]}) == "a"

    def test_membership_in_constant_list(self) -> None:
        assert _evaluate("role in ['admin', 'superuser']", {"role": "admin"}) == "True"
        assert _evaluate("role in ['admin', 'superuser']", {"role": "user"}) == "False"

    def test_code_injection_blocked(self) -> None:
        assert _evaluate("__import__('os').system('echo pwned')", {}).startswith("<error:")

    def test_dunder_and_private_access_blocked(self) -> None:
        assert _evaluate("().__class__", {}).startswith("<error:")
        assert _evaluate("x.__dict__", {"x": SimpleNamespace(a=1)}).startswith("<error:")
