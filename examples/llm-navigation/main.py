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

    print("\n=== 5) ENVIO AO LLM — resposta ancorada nos arquivos ===")
    answer = await engine.ask_llm(
        str(DEMO_PROJECT),
        seed_files=[SEED],
        instruction=instruction,
    )
    print(f"provider: {answer['response']['provider']} | "
          f"modo: {answer['mode']} | "
          f"tokens: {answer['response']['tokens_prompt']}+{answer['response']['tokens_completion']}")
    print(f"arquivos ancorados: {len(answer['anchored_files'])}")
    print(f"resposta ({len(answer['response']['content'])} chars):")
    print(answer["response"]["content"][:300])

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
        "llm_provider": answer["response"]["provider"],
        "llm_mode": answer["mode"],
        "anchored_files": len(answer["anchored_files"]),
        "response_chars": len(answer["response"]["content"]),
    }


if __name__ == "__main__":
    result = asyncio.run(main())
    print("\n=== RESUMO ===")
    print(json.dumps(result, indent=2, ensure_ascii=False))
