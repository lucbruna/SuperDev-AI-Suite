"""Tests for the executable ``examples/llm-navigation`` example.

Valida o fluxo completo: understand (SymbolIndex + DependencyGraph) -> busca
de símbolos -> BFS por dependência -> prompt montado. O diretório do exemplo
contém hífen ('llm-navigation'), logo não é um pacote importável — carregamos
o ``main.py`` por caminho via ``importlib``.
"""

from __future__ import annotations

import asyncio
import importlib.util
from pathlib import Path

import pytest

_EXAMPLE_MAIN = Path(__file__).resolve().parents[2] / "examples" / "llm-navigation" / "main.py"
_spec = importlib.util.spec_from_file_location("llm_navigation_example_main", _EXAMPLE_MAIN)
if _spec is None or _spec.loader is None:  # pragma: no cover - file always exists
    raise ImportError(f"could not load example: {_EXAMPLE_MAIN}")
_example = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_example)
main = _example.main
DEMO_PROJECT = _example.DEMO_PROJECT
SEED = _example.SEED


class TestCodeEngineNavigation:
    def test_understand_builds_index_and_graph(self) -> None:
        engine_result = asyncio.run(
            _example.CodeEngine().understand(str(DEMO_PROJECT))
        )
        assert engine_result["files"] >= 6
        assert engine_result["symbol_count"] >= 5
        assert "graph_summary" in engine_result
        assert engine_result["graph_summary"]["errors"] == []

    def test_find_symbols_returns_order(self) -> None:
        engine = _example.CodeEngine()
        found = asyncio.run(engine.find_symbols(str(DEMO_PROJECT), "order"))
        names = {m["name"] for m in found["matches"]}
        assert "Order" in names
        assert any(loc["kind"] == "class"
                   for m in found["matches"]
                   for loc in m["locations"])

    def test_find_symbols_matches_sorted_by_relevance(self) -> None:
        """``find_symbols`` reuses ``SymbolIndex.rank``: matches come back
        sorted by descending ``relevance`` (sum of per-location kind
        weights — a class in two files outranks a single function)."""
        engine = _example.CodeEngine()
        found = asyncio.run(engine.find_symbols(str(DEMO_PROJECT), "order"))
        relevances = [m["relevance"] for m in found["matches"]]
        assert all(isinstance(r, int) and r > 0 for r in relevances)
        assert relevances == sorted(relevances, reverse=True)  # rank() contract
        # top match defines a class (weight 3); trailing match is a plain import.
        assert any(loc["kind"] == "class"
                   for loc in found["matches"][0]["locations"])
        assert all(loc["kind"] == "import"
                   for loc in found["matches"][-1]["locations"])

    def test_bfs_context_includes_seed_deps_and_dependents(self) -> None:
        engine = _example.CodeEngine()
        ctx = asyncio.run(engine.build_llm_context(
            str(DEMO_PROJECT),
            seed_files=[SEED],
            max_depth=3,
            max_files=8,
        ))
        paths = [e["path"] for e in ctx["selection"]["selected"]]
        assert SEED in paths  # seed always kept
        # dependencies of main.py (direct + transitive)
        assert any(p.endswith("order_service.py") for p in paths)
        assert any(p.endswith("helpers.py") for p in paths)
        # reverse edge: sales_report.py imports order_service
        assert any(p.endswith("sales_report.py") for p in paths)
        assert ctx["prompt_tokens"] > 0
        assert ctx["fits_budget"] is True

    @staticmethod
    def _has_suffix(path: str, *parts: str) -> bool:
        return tuple(Path(path).parts[-len(parts):]) == parts

    def test_query_ranking_prioritizes_relevant_files(self) -> None:
        engine = _example.CodeEngine()
        ctx = asyncio.run(engine.build_llm_context(
            str(DEMO_PROJECT),
            seed_files=[SEED],
            instruction="Explain the order flow.",
            query="Order",
            max_depth=3,
            max_files=8,
        ))
        selected = ctx["selection"]["selected"]
        assert ctx["query"] == "Order"
        # seed stays first; the file defining Order/OrderItem classes ranks
        # above files that only import the symbol.
        order_model = next(e for e in selected
                           if self._has_suffix(e["path"], "models", "order.py"))
        assert order_model["relevance"] >= 6  # Order + OrderItem classes
        assert order_model["matched_symbols"] == ["Order", "OrderItem"]
        order_service = next(e for e in selected
                             if self._has_suffix(e["path"], "services",
                                                 "order_service.py"))
        assert order_service["relevance"] >= 3  # OrderService class
        positions = {e["path"]: i for i, e in enumerate(selected)}
        assert positions[order_model["path"]] < positions[order_service["path"]]

    def test_relative_imports_resolve_to_real_files(self) -> None:
        engine = _example.CodeEngine()
        ctx = asyncio.run(engine.build_llm_context(
            str(DEMO_PROJECT),
            seed_files=[SEED],
            max_depth=4,
            max_files=12,
        ))
        paths = [e["path"] for e in ctx["selection"]["selected"]]
        # level-1 relative: models/order.py -> models/base.py via ``from .base``
        assert any(self._has_suffix(p, "models", "base.py") for p in paths)
        # level-2 relative: services/order_service.py -> models/order.py
        assert any(self._has_suffix(p, "models", "order.py") for p in paths)
        # ``from . import helpers`` in services/__init__.py -> sibling module
        assert any(self._has_suffix(p, "services", "helpers.py") for p in paths)
        # level-2 relative: reporting/sales_report.py -> services/order_service.py
        assert any(self._has_suffix(p, "services", "order_service.py") for p in paths)
        # reverse edge preserved: sales_report.py still in the selection
        assert any(self._has_suffix(p, "reporting", "sales_report.py") for p in paths)

    def test_prompt_contains_fenced_files(self) -> None:
        engine = _example.CodeEngine()
        ctx = asyncio.run(engine.build_llm_context(
            str(DEMO_PROJECT),
            seed_files=[SEED],
            instruction="Explain the order flow.",
            max_files=4,
        ))
        assert ctx["prompt"].startswith("Explain the order flow.")
        assert "### FILE:" in ctx["prompt"]
        assert SEED in ctx["prompt"]  # fence lines carry absolute paths
        assert "```" in ctx["prompt"]

    def test_tight_budget_truncates_files_in_middle(self) -> None:
        """``max_file_tokens`` truncates oversized files mid-block so the
        ranked selection survives tight overall budgets."""
        engine = _example.CodeEngine()
        ctx = asyncio.run(engine.build_llm_context(
            str(DEMO_PROJECT),
            seed_files=[SEED],
            instruction="Explain the order flow.",
            query="Order",
            max_depth=3,
            max_files=8,
            max_tokens=600,
            max_file_tokens=30,
        ))
        assert ctx["max_file_tokens"] == 30
        assert ctx["truncated_files"] >= 1
        assert ctx["fits_budget"] is True
        # the prompt still contains fenced file blocks and the truncation marker
        assert "### FILE:" in ctx["prompt"]
        assert "truncated" in ctx["prompt"]
        assert ctx["prompt_tokens"] <= 600

    def test_global_budget_without_max_file_tokens(self) -> None:
        """``max_tokens`` alone caps the whole prompt: even with per-file
        truncation disabled, trailing (least relevant) files are truncated
        further in the middle — and dropped entirely when even a minimal
        slice cannot fit — until the assembled prompt fits the budget."""
        engine = _example.CodeEngine()
        ctx = asyncio.run(engine.build_llm_context(
            str(DEMO_PROJECT),
            seed_files=[SEED],
            instruction="Explain the order flow.",
            query="Order",
            max_depth=3,
            max_files=8,
            max_tokens=150,
        ))
        assert ctx["max_file_tokens"] is None      # global budget alone
        assert ctx["fits_budget"] is True
        assert ctx["prompt_tokens"] <= 150
        # the global pass kicked in: something was truncated or dropped, and
        # the dropped/truncated counts are reported back.
        assert ctx["truncated_files"] >= 1 or ctx["dropped_files"] >= 1
        assert ctx["dropped_files"] >= 0
        # the head of the ranked selection (the seed) still survives.
        assert SEED in ctx["prompt"]


class TestCodeEngineAskLLM:
    """Tests for ``CodeEngine.ask_llm`` — anchored prompt sent to the LLM."""

    def test_mock_fallback_without_provider(self,
                                            monkeypatch: pytest.MonkeyPatch) -> None:
        from unittest.mock import AsyncMock

        from ai.llm import LLMEngine

        # Deterministic: no env providers are registered, so the mock
        # fallback must be used regardless of the host environment.
        llm = LLMEngine()
        monkeypatch.setattr(
            llm.manager, "auto_register_providers",
            AsyncMock(return_value=[]),
        )
        engine = _example.CodeEngine()
        result = asyncio.run(engine.ask_llm(
            str(DEMO_PROJECT),
            seed_files=[SEED],
            instruction="Explain the order flow.",
            llm=llm,
        ))
        assert result["mode"] == "mock"
        assert result["response"]["provider"] == "mock"
        assert isinstance(result["response"]["content"], str)
        assert len(result["response"]["content"]) > 0
        assert result["prompt"].startswith("Explain the order flow.")
        assert any(e["path"].endswith("order_service.py")
                   for e in result["anchored_files"])

    def test_injected_llm_engine_is_used(self) -> None:
        from ai.llm import LLMEngine, MockProvider

        engine = _example.CodeEngine()
        llm = LLMEngine()
        llm.manager.registry.register(MockProvider("Anchored engine reply"))
        result = asyncio.run(engine.ask_llm(
            str(DEMO_PROJECT),
            seed_files=[SEED],
            instruction="Explain the order flow.",
            llm=llm,
        ))
        assert result["mode"] == "real"
        assert result["response"]["content"] == "Anchored engine reply"
        assert result["response"]["provider"] == "mock"

    def test_explicit_provider_passthrough(self) -> None:
        from ai.llm import LLMEngine, MockProvider

        engine = _example.CodeEngine()
        llm = LLMEngine()
        llm.manager.registry.register(MockProvider("Explicit provider reply"))
        result = asyncio.run(engine.ask_llm(
            str(DEMO_PROJECT),
            seed_files=[SEED],
            instruction="Explain the order flow.",
            provider="mock",
            llm=llm,
        ))
        assert result["response"]["provider"] == "mock"
        assert result["response"]["content"] == "Explicit provider reply"
        assert result["focus"] is None  # no query -> no focus section

    def test_focus_section_added_to_instruction(self) -> None:
        from ai.llm import LLMEngine, MockProvider

        engine = _example.CodeEngine()
        llm = LLMEngine()
        llm.manager.registry.register(MockProvider(
            "Order and OrderItem are the core entities."))
        result = asyncio.run(engine.ask_llm(
            str(DEMO_PROJECT),
            seed_files=[SEED],
            instruction="Explain the order flow.",
            query="Order",
            llm=llm,
        ))
        focus = result["focus"]
        assert focus is not None
        # the most relevant DEFINED symbols (pure imports skipped — no module
        # names with dots); order follows the scan/parse order, so assert
        # membership instead of exact positions.
        assert {"Order", "OrderItem"} <= set(focus["symbols"])
        assert all("." not in symbol for symbol in focus["symbols"])
        assert focus["section"].startswith("Foco: ")
        assert "Order" in focus["section"] and "OrderItem" in focus["section"]
        assert focus["overhead_tokens"] >= 1
        assert "Foco: Order" in result["prompt"]
        # the reply mentions Order and OrderItem -> measurable coverage
        assert 0 < focus["coverage"] <= 1.0

    def test_focus_disabled_leaves_prompt_unchanged(self) -> None:
        from ai.llm import LLMEngine, MockProvider

        engine = _example.CodeEngine()
        llm = LLMEngine()
        llm.manager.registry.register(MockProvider("Plain reply"))
        result = asyncio.run(engine.ask_llm(
            str(DEMO_PROJECT),
            seed_files=[SEED],
            instruction="Explain the order flow.",
            query="Order",
            focus=False,
            llm=llm,
        ))
        assert result["focus"] is None
        assert "Foco:" not in result["prompt"]

    def test_focus_coverage_full_with_echo_provider(self) -> None:
        from ai.llm import LLMEngine, MockProvider

        engine = _example.CodeEngine()

        class EchoProvider(MockProvider):
            async def generate(self, prompt: str, **kwargs: object) -> dict:
                for line in prompt.splitlines():
                    if line.startswith("Foco:"):
                        self._response = line
                        break
                else:
                    self._response = "No Foco section in the prompt."
                return await super().generate(prompt, **kwargs)

        llm = LLMEngine()
        llm.manager.registry.register(EchoProvider())
        result = asyncio.run(engine.ask_llm(
            str(DEMO_PROJECT),
            seed_files=[SEED],
            instruction="Explain the order flow.",
            query="Order",
            llm=llm,
        ))
        # the echo provider repeats the focus line -> every symbol is covered
        assert result["focus"] is not None
        assert result["focus"]["coverage"] == 1.0


class TestLlmNavigationExample:
    def test_main_entrypoint_runs(self) -> None:
        result = asyncio.run(main())
        assert result["files"] >= 6
        assert result["symbols"] >= 5
        assert result["found_symbols"] >= 1
        assert result["fits_budget"] is True
        assert result["prompt_tokens"] > 0
        # global budget step (no max_file_tokens): fits and drops/truncates
        assert result["global_budget_fits"] is True
        assert result["global_budget_tokens"] <= 150
        assert (result["global_budget_truncated"] >= 1
                or result["global_budget_dropped"] >= 1)
        # env-dependent: a real provider may answer (mode "real") when an
        # API key is set; otherwise the mock fallback guarantees a reply.
        assert result["llm_mode"] in ("mock", "real")
        assert result["anchored_files"] >= 3
        assert result["response_chars"] > 0
        # focus: the example sends query='Order' so the Foco section exists,
        # and the echo provider measures baseline (0%) vs focused (100%).
        assert "Order" in result["focus_symbols"]
        assert result["focus_section"].startswith("Foco: ")
        assert result["focus_coverage"] >= 0.0
        assert result["measure_focused_coverage"] == 1.0
        assert result["measure_overhead_tokens"] >= 1
