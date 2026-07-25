"""Benchmark runner para todos os módulos do SuperDev."""

import asyncio
import time
import statistics
from typing import Callable


async def benchmark(name: str, func: Callable, iterations: int = 100) -> dict:
    """Executa um benchmark e retorna métricas."""
    times = []

    for _ in range(iterations):
        start = time.perf_counter()
        await func()
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    return {
        "name": name,
        "iterations": iterations,
        "avg_ms": statistics.mean(times) * 1000,
        "median_ms": statistics.median(times) * 1000,
        "min_ms": min(times) * 1000,
        "max_ms": max(times) * 1000,
        "p95_ms": sorted(times)[int(len(times) * 0.95)] * 1000,
        "p99_ms": sorted(times)[int(len(times) * 0.99)] * 1000,
    }


async def bench_condition_node():
    from workflow_engine.nodes.condition_node import safe_condition_eval
    safe_condition_eval("x > 5 and y < 10", {"x": 7, "y": 3})


async def bench_planner():
    from agents.planner.planner import Planner
    planner = Planner()
    await planner.plan("Criar um sistema completo com backend, frontend e testes")


async def bench_sandbox():
    from runtime_engine.sandbox.sandbox import DefaultSandbox
    sandbox = DefaultSandbox()
    await sandbox.create()
    await sandbox.execute(["echo", "benchmark"])
    await sandbox.destroy()


async def bench_vector_store():
    """Benchmark de busca vetorial (requer pgvector)."""
    try:
        from backend.knowledge_base.vector_store import VectorStore
        # Este teste requer banco de dados ativo
        pass
    except Exception:
        pass


async def main():
    benchmarks = [
        ("ConditionNode - safe_eval", bench_condition_node),
        ("Planner - decomposição", bench_planner),
        ("Sandbox - criação/execução", bench_sandbox),
    ]

    print("=" * 60)
    print("SuperDev Benchmarks")
    print("=" * 60)

    results = []
    for name, func in benchmarks:
        print(f"\nBenchmarking: {name}...")
        result = await benchmark(name, func, iterations=50)
        results.append(result)
        print(f"  Média: {result['avg_ms']:.2f}ms")
        print(f"  P95: {result['p95_ms']:.2f}ms")
        print(f"  P99: {result['p99_ms']:.2f}ms")

    print("\n" + "=" * 60)
    print("Resumo")
    print("=" * 60)
    for r in results:
        print(f"{r['name']:40} {r['avg_ms']:8.2f}ms (P95: {r['p95_ms']:.2f}ms)")


if __name__ == "__main__":
    asyncio.run(main())
