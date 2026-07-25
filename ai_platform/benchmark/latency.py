from __future__ import annotations

import asyncio
import statistics
import time

from ..providers.base_provider import BaseProvider

TEST_PROMPTS = [
    [{"role": "user", "content": "Hello, how are you?"}],
    [{"role": "user", "content": "What is the capital of France?"}],
    [{"role": "user", "content": "Explain quantum computing in one paragraph."}],
    [{"role": "user", "content": "Write a Python function to sort a list."}],
    [{"role": "user", "content": "What is the meaning of life?"}],
]


class LatencyBenchmark:
    @staticmethod
    async def benchmark_provider(
        provider: BaseProvider,
        test_prompts: list[list[dict]] | None = None,
        iterations: int = 3,
    ) -> dict:
        prompts = test_prompts or TEST_PROMPTS
        config = {"max_tokens": 50, "temperature": 0.0}
        latencies: list[float] = []

        for prompt in prompts:
            for _ in range(iterations):
                start = time.monotonic()
                try:
                    await provider.chat(prompt, config)
                    elapsed = (time.monotonic() - start) * 1000
                    latencies.append(elapsed)
                except Exception:
                    elapsed = (time.monotonic() - start) * 1000
                    latencies.append(elapsed)
                await asyncio.sleep(0.1)

        if not latencies:
            return {"error": "no measurements", "avg_latency": 0, "p50": 0, "p95": 0, "p99": 0}

        sorted_lat = sorted(latencies)
        n = len(sorted_lat)

        return {
            "avg_latency": round(statistics.mean(latencies), 2),
            "p50": round(sorted_lat[n // 2], 2),
            "p95": round(sorted_lat[int(n * 0.95)], 2),
            "p99": round(sorted_lat[int(n * 0.99)], 2),
            "min": round(sorted_lat[0], 2),
            "max": round(sorted_lat[-1], 2),
            "std_dev": round(statistics.stdev(latencies), 2) if n > 1 else 0.0,
            "measurements": n,
            "all_latencies": [round(l, 2) for l in latencies],
        }

    @staticmethod
    async def benchmark_stream(
        provider: BaseProvider,
        test_prompts: list[list[dict]] | None = None,
        iterations: int = 2,
    ) -> dict:
        prompts = test_prompts or TEST_PROMPTS[:2]
        config = {"max_tokens": 100, "temperature": 0.0}
        ttfb_list: list[float] = []
        total_times: list[float] = []

        for prompt in prompts:
            for _ in range(iterations):
                start = time.monotonic()
                first_chunk = True
                try:
                    async for _chunk in provider.stream(prompt, config):
                        if first_chunk:
                            ttfb = (time.monotonic() - start) * 1000
                            ttfb_list.append(ttfb)
                            first_chunk = False
                    elapsed = (time.monotonic() - start) * 1000
                    total_times.append(elapsed)
                except Exception:
                    pass
                await asyncio.sleep(0.1)

        return {
            "avg_ttfb_ms": round(statistics.mean(ttfb_list), 2) if ttfb_list else 0,
            "avg_total_ms": round(statistics.mean(total_times), 2) if total_times else 0,
            "ttfb_measurements": len(ttfb_list),
            "total_measurements": len(total_times),
        }
