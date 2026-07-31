from __future__ import annotations

from typing import Any

from ..quality_models import QualityScore
from .complexity import ComplexityAnalyzer


class AnalyzerEngine:
    """Intelligent analysis — code quality, complexity, maintainability, duplication, architecture, dependencies."""

    def __init__(self, engine: Any) -> None:
        self.engine = engine
        self.config = engine.config.analysis
        self.complexity_analyzer = ComplexityAnalyzer(engine=engine)
        self._scores: dict[str, QualityScore] = {}
        self._analyses: dict[str, dict[str, Any]] = {}
        self._initialized = False

    async def initialize(self) -> None:
        self._initialized = True

    async def shutdown(self) -> None:
        self._initialized = False

    # -- complexity ----------------------------------------------------------

    def complexity(self, source: str) -> dict[str, Any]:
        """Heuristic cyclomatic complexity from structural keywords."""
        if not source:
            return {"score": 1.0, "complexity": 0, "note": "empty"}
        branches = sum(
            source.count(kw) for kw in ("if ", "elif ", "for ", "while ", "except ", "case ")
        )
        complexity = 1 + branches
        if complexity <= 5:
            score = 1.0
        elif complexity <= 10:
            score = 0.8
        elif complexity <= 20:
            score = 0.6
        else:
            score = 0.4
        return {"complexity": complexity, "score": score}

    # -- duplication ---------------------------------------------------------

    def duplication(self, source: str) -> float:
        """Estimate duplication ratio (0.0 none → 1.0 all duplicated)."""
        if not source:
            return 0.0
        lines = [ln.strip() for ln in source.splitlines() if ln.strip()]
        if not lines:
            return 0.0
        unique = len(set(lines))
        return round(1 - unique / len(lines), 4)

    # -- maintainability -----------------------------------------------------

    def maintainability(self, source: str) -> float:
        """0..1 heuristic: docstrings + type hints + line length discipline."""
        if not source:
            return 1.0
        score = 0.5
        if '"""' in source or "'''" in source:
            score += 0.2
        if ": " in source and "->" in source:
            score += 0.15
        long_lines = sum(1 for ln in source.splitlines() if len(ln) > 120)
        if long_lines == 0:
            score += 0.15
        return round(min(1.0, score), 4)

    # -- architecture / dependency checks ------------------------------------

    def architecture_check(self, source: str, allowed_imports: list[str] | None = None) -> dict[str, Any]:
        imports = [ln for ln in source.splitlines() if ln.strip().startswith(("import ", "from "))]
        if allowed_imports is None:
            allowed_imports = []
        violations = [
            imp for imp in imports
            if allowed_imports and not any(a in imp for a in allowed_imports)
        ]
        return {"imports": imports, "violations": violations, "clean": not violations}

    def dependency_check(self, dependencies: dict[str, Any]) -> dict[str, Any]:
        """Classify dependencies by risk using a heuristic."""
        risky = [
            name for name, info in dependencies.items()
            if info.get("risk") in ("high", "medium")
        ]
        return {
            "total": len(dependencies),
            "risky": len(risky),
            "risky_names": risky,
            "healthy": len(risky) == 0,
        }

    # -- code quality --------------------------------------------------------

    def analyze_code(self, target: str, source: str) -> dict[str, Any]:
        """Composite heuristic analysis of a code sample."""
        complexity = self.complexity(source)
        maintainability = self.maintainability(source)
        duplication = self.duplication(source)
        quality = round(
            (complexity["score"] * 0.4 + maintainability * 0.4 + (1 - duplication) * 0.2),
            4,
        )
        analysis = {
            "target": target,
            "quality": quality,
            "complexity": complexity,
            "maintainability": maintainability,
            "duplication": duplication,
        }
        self._analyses[target] = analysis
        self.engine.metrics.gauge("analysis.quality", quality, labels={"target": target})
        return analysis

    # -- quality score -------------------------------------------------------

    def score(
        self,
        target: str,
        code: float = 0.0,
        tests: float = 0.0,
        security: float = 0.0,
        performance: float = 0.0,
        documentation: float = 0.0,
    ) -> QualityScore:
        """Build the composite QualityScore (weighted overall in the model)."""
        score = QualityScore(
            target=target,
            code=round(code, 4),
            tests=round(tests, 4),
            security=round(security, 4),
            performance=round(performance, 4),
            documentation=round(documentation, 4),
        )
        self._scores[score.score_id] = score
        self.engine.registry.register_score(score)
        self.engine.metrics.increment("analysis.scores", labels={"target": target})
        return score

    def get_scores(self) -> list[QualityScore]:
        return list(self._scores.values())

    def status(self) -> dict[str, Any]:
        return {
            "initialized": self._initialized,
            "scores": len(self._scores),
            "analyses": len(self._analyses),
        }


__all__ = ["AnalyzerEngine"]
