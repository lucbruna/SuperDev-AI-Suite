from __future__ import annotations

from datetime import datetime
from typing import Any

from .eval_runner import EvalRunner
from .metrics import EvalMetrics


class EvalReport:
    def __init__(self, runner: EvalRunner | None = None):
        self._runner = runner or EvalRunner()
        self._metrics = EvalMetrics()

    async def generate_report(self, prompts: list[str], model_a: str, model_b: str) -> dict[str, Any]:
        results = await self._runner.run_batch(prompts, model_a, model_b)
        summary = self._metrics.compare(results)
        costs = self._metrics.cost_estimate(model_a, model_b, summary["model_a"]["total_tokens"], summary["model_b"]["total_tokens"])

        winner = "tie"
        if summary["model_a"]["wins"] > summary["model_b"]["wins"]:
            winner = model_a
        elif summary["model_b"]["wins"] > summary["model_a"]["wins"]:
            winner = model_b

        return {
            "report_id": f"eval_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "generated_at": datetime.utcnow().isoformat(),
            "model_a": model_a,
            "model_b": model_b,
            "prompts_count": len(prompts),
            "summary": {**summary, **costs},
            "winner": winner,
            "recommendation": self._generate_recommendation(winner, summary, costs),
            "details": results,
        }

    def _generate_recommendation(self, winner: str, summary: dict[str, Any], costs: dict[str, float]) -> str:
        if winner == "tie":
            "model_a" if costs["model_a_cost"] < costs["model_b_cost"] else "model_b"
            return "Models performed equally. Recommend using the more cost-effective option."
        return f"Recommend: {winner} — {summary['model_a']['wins'] if winner != 'tie' else 'N/A'} wins vs {summary['model_b']['wins']}"

    def format_markdown(self, report: dict[str, Any]) -> str:
        lines = [
            f"# Eval Report: {report['model_a']} vs {report['model_b']}",
            f"**Generated**: {report['generated_at']}",
            f"**Prompts**: {report['prompts_count']}",
            f"**Winner**: {report['winner']}",
            "",
            "## Summary",
            f"| Metric | {report['model_a']} | {report['model_b']} |",
            "|--------|------|------|",
            f"| Wins | {report['summary']['model_a']['wins']} ({report['summary']['model_a']['win_rate']}%) | {report['summary']['model_b']['wins']} ({report['summary']['model_b']['win_rate']}%) |",
            f"| Avg Duration | {report['summary']['model_a']['avg_duration_ms']}ms | {report['summary']['model_b']['avg_duration_ms']}ms |",
            f"| Total Tokens | {report['summary']['model_a']['total_tokens']} | {report['summary']['model_b']['total_tokens']} |",
            f"| Cost | ${report['summary']['model_a_cost']} | ${report['summary']['model_b_cost']} |",
            "",
            f"**Ties**: {report['summary']['ties']} ({report['summary']['tie_rate']}%)",
            "",
            "## Recommendation",
            report.get("recommendation", ""),
        ]
        return "\n".join(lines)
