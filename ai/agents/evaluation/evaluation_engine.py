"""Evaluation engine for assessing agent performance and output quality."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from .performance_evaluator import PerformanceEvaluator
from .quality_scorer import QualityScorer
from .benchmark_manager import BenchmarkManager
from .report_generator import ReportGenerator
from .metric_analyzer import MetricAnalyzer


class EvaluationEngine:
    """Central engine for evaluating agent performance and output quality."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self._config = config or {}
        self._performance = PerformanceEvaluator()
        self._quality = QualityScorer()
        self._benchmarks = BenchmarkManager()
        self._reports = ReportGenerator()
        self._metrics = MetricAnalyzer()
        self._evaluation_count: int = 0

    def evaluate_agent(self, agent_id: str, metrics: Dict[str, Any]) -> Dict[str, Any]:
        self._evaluation_count += 1
        perf = self._performance.evaluate(metrics)
        quality = self._quality.score(metrics)
        return {
            "agent_id": agent_id,
            "performance": perf,
            "quality": quality,
            "overall": round((perf.get("score", 0.5) + quality.get("score", 0.5)) / 2, 2),
        }

    def evaluate_output(self, output: Dict[str, Any], criteria: Optional[List[str]] = None) -> Dict[str, Any]:
        self._evaluation_count += 1
        return self._quality.score_output(output, criteria)

    def compare_to_benchmark(self, agent_id: str, metrics: Dict[str, Any]) -> Dict[str, Any]:
        return self._benchmarks.compare(agent_id, metrics)

    def generate_report(self, evaluation_data: Dict[str, Any]) -> Dict[str, Any]:
        return self._reports.generate(evaluation_data)

    def analyze_trends(self, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        return self._metrics.analyze_trends(historical_data)

    def get_metrics(self) -> Dict[str, Any]:
        return {"total_evaluations": self._evaluation_count}
