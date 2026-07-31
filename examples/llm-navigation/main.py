"""
LLM Code Navigation — executable example (CodeEngine + SymbolIndex +
DependencyGraph + ContextBuilder BFS + PromptBuilder).

Navigates a real demo project by dependency: scans the files, indexes the
symbols, builds the dependency graph from imports, walks BFS from the entry
point (dependencies AND dependents) and assembles the context that would be
injected into an LLM prompt.

Run:
    cd SuperDev
    python examples/llm-navigation/main.py
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from typing import Any

# Ensure the SuperDev repo root is importable when run as a script.
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from code import CodeEngine  # noqa: E402

DEMO_PROJECT = Path(__file__).resolve().parent / "demo_project"
SEED = str(DEMO_PROJECT / "main.py")


def _short(path: str) -> str:
    """Relative path for readable output."""
    return str(Path(path).relative_to(DEMO_PROJECT))


def _print_graph(graph: dict[str, Any]) -> None:
    for src, deps in sorted(graph.items()):
        for dep in deps:
            print(f"    {_short(src)}  ->  {dep}")


async def main() -> dict[str, Any]:
    engine = CodeEngine()

    print("=== 1) ENTENDIMENTO — scan + SymbolIndex + DependencyGraph ===")
    understood = await engine.understand(str(DEMO_PROJECT))
    print(f"arquivos escaneados: {understood['files']}")
    print(f"símbolos indexados: {understood['symbol_count']}")
    print(f"nós no grafo: {len(understood['graph'])}")
    print("arestas (arquivo -> módulo importado):")
    _print_graph(understood["graph"])

    print("\n=== 2) BUSCA DE SÍMBOLOS — 'Order' ===")
    found = await engine.find_symbols(str(DEMO_PROJECT), "order")
    print(f"{len(found['matches'])} símbolo(s) contendo 'order':")
    for match in found["matches"]:
        for loc in match["locations"]:
            print(f"    {match['name']} ({loc['kind']})  em  {_short(loc['path'])}")

    print("\n=== 3) NAVEGAÇÃO POR DEPENDÊNCIA — BFS a partir de main.py ===")
    instruction = (
        "You are a senior engineer reviewing this demo project. "
        "Explain how an order flows from the entry point to persistence."
    )
    context = await engine.build_llm_context(
        str(DEMO_PROJECT),
        seed_files=[SEED],
        instruction=instruction,
        query="Order",
        max_depth=3,
        max_files=6,
        max_tokens=8000,
    )
    print("arquivos selecionados — ordenados por RELEVÂNCIA ao query 'Order':")
    for entry in context["selection"]["selected"]:
        marker = "SEED" if entry["path"] == SEED else f"depth {entry['depth']}"
        rank = entry["relevance"]
        symbols = ",".join(entry["matched_symbols"]) or "-"
        print(f"    [{marker:>8}] rel={rank} ~{entry['tokens']:>4} tok  "
              f"{_short(entry['path'])}  ({symbols})")
    print(f"total tokens do contexto: {context['selection']['total_tokens']}")

    print("\n=== 4) PROMPT MONTADO PARA O MODELO ===")
    prompt = context["prompt"]
    print(f"tokens estimados do prompt: {context['prompt_tokens']} | "
          f"dentro do orçamento: {context['fits_budget']}")
    print(f"tamanho: {len(prompt)} caracteres")
    print("\n--- início do prompt ---")
    print(prompt[:700])

    print("\n=== 5) BUDGET APERTADO — truncamento por arquivo ===")
    tight = await engine.build_llm_context(
        str(DEMO_PROJECT),
        seed_files=[SEED],
        instruction=instruction,
        query="Order",
        max_depth=3,
        max_files=8,
        max_tokens=600,
        max_file_tokens=30,
    )
    print(f"max_tokens=600 | max_file_tokens=30 | "
          f"arquivos truncados: {tight['truncated_files']} | "
          f"prompt_tokens: {tight['prompt_tokens']} | "
          f"fits_budget: {tight['fits_budget']}")
    print(f"prompt contém marcador de truncamento: "
          f"{'# ...' in tight['prompt']}")

    print("\n=== 5b) BUDGET GLOBAL — sem max_file_tokens ===")
    global_budget = await engine.build_llm_context(
        str(DEMO_PROJECT),
        seed_files=[SEED],
        instruction=instruction,
        query="Order",
        max_depth=3,
        max_files=8,
        max_tokens=150,
    )
    print(f"max_tokens=150 (sem max_file_tokens) | "
          f"arquivos truncados: {global_budget['truncated_files']} | "
          f"arquivos descartados: {global_budget['dropped_files']} | "
          f"prompt_tokens: {global_budget['prompt_tokens']} | "
          f"fits_budget: {global_budget['fits_budget']}")
    print(f"prompt ainda contém blocos FILE: "
          f"{'### FILE:' in global_budget['prompt']}")

    print("\n=== 6) ENVIO AO LLM — resposta ancorada + FOCO nos símbolos ===")
    answer = await engine.ask_llm(
        str(DEMO_PROJECT),
        seed_files=[SEED],
        instruction=instruction,
        query="Order",
    )
    focus = answer["focus"]
    print(f"provider: {answer['response']['provider']} | "
          f"modo: {answer['mode']} | "
          f"tokens: {answer['response']['tokens_prompt']}+{answer['response']['tokens_completion']}")
    print(f"arquivos ancorados: {len(answer['anchored_files'])}")
    if focus:
        print(f"símbolos em foco: {', '.join(focus['symbols'])}")
        print(f"seção adicionada: '{focus['section']}' (+{focus['overhead_tokens']} tokens)")
        print(f"cobertura dos símbolos na resposta: {focus['coverage']:.0%}")
    print(f"resposta ({len(answer['response']['content'])} chars):")
    print(answer["response"]["content"][:300])

    print("\n=== 7) MEDINDO A MELHORA — baseline vs. com foco ===")
    from ai.llm import LLMEngine, MockProvider

    # Provider determinístico que ecoa a seção 'Foco:' do prompt na resposta,
    # para que a cobertura de símbolos seja mensurável (0% sem foco, 100% com).
    class FocusEchoProvider(MockProvider):
        async def generate(self, prompt: str, **kwargs: Any) -> dict[str, Any]:
            for line in prompt.splitlines():
                if line.startswith("Foco:"):
                    self._response = line
                    break
            else:
                self._response = "No Foco section in the prompt."
            return await super().generate(prompt, **kwargs)

    measure_llm = LLMEngine()
    measure_llm.manager.registry.register(FocusEchoProvider())
    baseline = await engine.ask_llm(
        str(DEMO_PROJECT), seed_files=[SEED], instruction=instruction,
        query="Order", focus=False, llm=measure_llm,
    )
    focused = await engine.ask_llm(
        str(DEMO_PROJECT), seed_files=[SEED], instruction=instruction,
        query="Order", focus=True, llm=measure_llm,
    )
    print(f"baseline (sem foco): resposta {baseline['response']['content'][:36]!r}...")
    if focused["focus"]:
        print(f"com foco: {focused['focus']['section']!r}")
        print(f"  resposta ecoada: {focused['response']['content'][:36]!r}...")
        print(f"  cobertura: baseline 0% -> com foco "
              f"{focused['focus']['coverage']:.0%} "
              f"(overhead +{focused['focus']['overhead_tokens']} tokens)")

    return {
        "files": understood["files"],
        "symbols": understood["symbol_count"],
        "graph_nodes": len(understood["graph"]),
        "found_symbols": len(found["matches"]),
        "selected_files": [entry["path"] for entry in
                           context["selection"]["selected"]],
        "context_tokens": context["selection"]["total_tokens"],
        "prompt_tokens": context["prompt_tokens"],
        "fits_budget": context["fits_budget"],
        "tight_truncated_files": tight["truncated_files"],
        "tight_prompt_tokens": tight["prompt_tokens"],
        "tight_fits_budget": tight["fits_budget"],
        "global_budget_truncated": global_budget["truncated_files"],
        "global_budget_dropped": global_budget["dropped_files"],
        "global_budget_tokens": global_budget["prompt_tokens"],
        "global_budget_fits": global_budget["fits_budget"],
        "llm_provider": answer["response"]["provider"],
        "llm_mode": answer["mode"],
        "anchored_files": len(answer["anchored_files"]),
        "response_chars": len(answer["response"]["content"]),
        "focus_symbols": (focus["symbols"] if focus else []),
        "focus_section": (focus["section"] if focus else ""),
        "focus_coverage": (focus["coverage"] if focus else 0.0),
        "focus_overhead_tokens": (focus["overhead_tokens"] if focus else 0),
        "measure_baseline_chars": len(baseline["response"]["content"]),
        "measure_focused_coverage": (
            focused["focus"]["coverage"] if focused["focus"] else 0.0),
        "measure_overhead_tokens": (
            focused["focus"]["overhead_tokens"] if focused["focus"] else 0),
    }


if __name__ == "__main__":
    result = asyncio.run(main())
    print("\n=== RESUMO ===")
    print(json.dumps(result, indent=2, ensure_ascii=False))
