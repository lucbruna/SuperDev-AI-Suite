from __future__ import annotations

from typing import Any


class EvalMetrics:
    @staticmethod
    def compare(results: list[dict[str, Any]]) -> dict[str, Any]:
        if not results:
            return {}
        wins_a = wins_b = ties = 0
        total_duration_a = total_duration_b = 0
        total_tokens_a = total_tokens_b = 0

        for r in results:
            a = r.get("model_a", {})
            b = r.get("model_b", {})
            score_a = len(a.get("response", ""))
            score_b = len(b.get("response", ""))
            if score_a > score_b:
                wins_a += 1
            elif score_b > score_a:
                wins_b += 1
            else:
                ties += 1
            total_duration_a += a.get("duration_ms", 0)
            total_duration_b += b.get("duration_ms", 0)
            total_tokens_a += a.get("tokens", 0)
            total_tokens_b += b.get("tokens", 0)

        n = len(results)
        return {
            "total_comparisons": n,
            "model_a": {"wins": wins_a, "win_rate": round(wins_a / n * 100, 1) if n else 0, "avg_duration_ms": round(total_duration_a / n, 1) if n else 0, "total_tokens": total_tokens_a},
            "model_b": {"wins": wins_b, "win_rate": round(wins_b / n * 100, 1) if n else 0, "avg_duration_ms": round(total_duration_b / n, 1) if n else 0, "total_tokens": total_tokens_b},
            "ties": ties,
            "tie_rate": round(ties / n * 100, 1) if n else 0,
        }

    @staticmethod
    def cost_estimate(model_a: str, model_b: str, tokens_a: int, tokens_b: int) -> dict[str, float]:
        rates = {
            "gpt-4o": {"input": 2.5e-6, "output": 1e-5},
            "gpt-4o-mini": {"input": 1.5e-7, "output": 6e-7},
            "claude-3-5-sonnet": {"input": 3e-6, "output": 1.5e-5},
            "claude-3-haiku": {"input": 2.5e-7, "output": 1.25e-6},
            "gemini-1.5-pro": {"input": 1.25e-6, "output": 5e-6},
            "gemini-1.5-flash": {"input": 7.5e-8, "output": 3e-7},
        }
        rate_a = rates.get(model_a, rates["gpt-4o"])
        rate_b = rates.get(model_b, rates["gpt-4o"])
        cost_a = tokens_a * rate_a["output"]
        cost_b = tokens_b * rate_b["output"]
        return {"model_a_cost": round(cost_a, 6), "model_b_cost": round(cost_b, 6), "savings": round(cost_a - cost_b, 6)}
