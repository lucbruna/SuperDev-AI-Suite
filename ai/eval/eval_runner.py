from __future__ import annotations

import asyncio
import time
from typing import Any

from ai_platform.providers import get_provider


class EvalRunner:
    def __init__(self):
        self._results: list[dict[str, Any]] = []

    async def run_single(
        self, prompt: str, model_a: str, model_b: str, system_prompt: str = "", temperature: float = 0.7
    ) -> dict[str, Any]:
        provider_a = get_provider(model_a)
        provider_b = get_provider(model_b)

        start_a = time.time()
        result_a = await provider_a.chat(prompt, system_prompt=system_prompt, temperature=temperature)
        duration_a = (time.time() - start_a) * 1000

        start_b = time.time()
        result_b = await provider_b.chat(prompt, system_prompt=system_prompt, temperature=temperature)
        duration_b = (time.time() - start_b) * 1000

        eval_result = {
            "prompt": prompt,
            "model_a": {
                "name": model_a,
                "response": result_a.get("content", ""),
                "duration_ms": round(duration_a, 2),
                "tokens": result_a.get("usage", {}).get("total_tokens", 0),
            },
            "model_b": {
                "name": model_b,
                "response": result_b.get("content", ""),
                "duration_ms": round(duration_b, 2),
                "tokens": result_b.get("usage", {}).get("total_tokens", 0),
            },
            "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
        }
        self._results.append(eval_result)
        return eval_result

    async def run_batch(self, prompts: list[str], model_a: str, model_b: str) -> list[dict[str, Any]]:
        tasks = [self.run_single(p, model_a, model_b) for p in prompts]
        return await asyncio.gather(*tasks)

    async def run_with_variations(self, prompts: list[str], models: list[str]) -> list[dict[str, Any]]:
        if len(models) < 2:
            raise ValueError("At least 2 models required")
        results = []
        for prompt in prompts:
            for i in range(len(models)):
                for j in range(i + 1, len(models)):
                    result = await self.run_single(prompt, models[i], models[j])
                    results.append(result)
        return results

    def get_history(self) -> list[dict[str, Any]]:
        return self._results

    def clear(self) -> None:
        self._results.clear()
