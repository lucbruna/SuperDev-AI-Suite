"""Deep-dive complexity analysis — cyclomatic complexity, nesting depth, risk.

Complementa o ``AnalyzerEngine.complexity`` com uma análise mais precisa:

- conta ramos (`if`/`elif`/`for`/`while`/`except`/`case`/`assert`) usando o
  tokenizador padrão do Python, ignorando comentários, docstrings e strings;
- mede profundidade máxima de aninhamento (indentação);
- conta funções e classes;
- classifica risco (low/medium/high/critical) com score 0..1.
"""

from __future__ import annotations

import io
import tokenize
from typing import Any

# Palavras-chave que adicionam +1 à complexidade ciclomática (contadas como
# tokens NAME exatos — `elif` não vaza como `if`).
_BRANCH_KEYWORDS = frozenset(
    {"if", "elif", "for", "while", "except", "case", "assert"}
)

class ComplexityAnalyzer:
    """Cyclomatic complexity, nesting depth and risk classification.

    Uso:
        analyzer = ComplexityAnalyzer()
        result = analyzer.analyze(source)
        # {"complexity": 3, "depth": 1, "functions": 2, "score": 1.0, "risk": "low"}
    """

    def __init__(self, engine: Any | None = None) -> None:
        self.engine = engine
        self._analyses: dict[str, dict[str, Any]] = {}

    # -- tokenizer -----------------------------------------------------------

    @staticmethod
    def _name_tokens(source: str) -> list[str]:
        """Tokenize source and return the NAME tokens (comments/strings skipped)."""
        try:
            tokens = tokenize.generate_tokens(io.StringIO(source).readline)
            return [token.string for token in tokens if token.type == tokenize.NAME]
        except (tokenize.TokenError, IndentationError, SyntaxError):
            return []

    @staticmethod
    def _code_lines(source: str) -> list[str]:
        """Source lines with comments stripped and blank lines removed."""
        lines: list[str] = []
        for raw_line in source.splitlines():
            stripped = raw_line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            # Remove trailing inline comment (naive but sufficient here).
            code = stripped.split(" #", 1)[0].strip()
            if code:
                lines.append(code)
        return lines

    # -- metrics -------------------------------------------------------------

    def cyclomatic_complexity(self, source: str) -> int:
        """Cyclomatic complexity = 1 + number of branch keywords in code."""
        if not source:
            return 1
        names = self._name_tokens(source)
        return 1 + sum(1 for name in names if name in _BRANCH_KEYWORDS)

    def nesting_depth(self, source: str) -> int:
        """Maximum indentation depth (code lines only, ignoring blank/comment)."""
        if not source:
            return 0
        max_depth = 0
        for raw_line in source.splitlines():
            stripped = raw_line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            indent = len(raw_line) - len(raw_line.lstrip(" "))
            max_depth = max(max_depth, indent // 4)
        return max_depth

    def branch_count(self, source: str) -> int:
        """Number of branching lines (if/for/while/except/case/assert/else)."""
        count = 0
        for code_line in self._code_lines(source):
            if any(
                code_line.startswith(kw) or f" {kw}" in f" {code_line}"
                for kw in ("if ", "elif ", "for ", "while ", "except ", "case ", "assert ")
            ):
                count += 1
        return count

    def function_count(self, source: str) -> int:
        """Number of `def` function definitions (excludes ``async def``)."""
        return sum(1 for line in self._code_lines(source) if line.startswith("def "))

    # -- classification ------------------------------------------------------

    @staticmethod
    def classify(complexity: int) -> tuple[str, float]:
        """Map complexity to (risk, score 0..1)."""
        if complexity <= 5:
            return "low", 1.0
        if complexity <= 10:
            return "medium", 0.8
        if complexity <= 20:
            return "high", 0.6
        return "critical", 0.4

    # -- aggregate -----------------------------------------------------------

    def analyze(self, source: str, target: str = "") -> dict[str, Any]:
        """Full analysis with cached results and engine metrics."""
        complexity = self.cyclomatic_complexity(source)
        depth = self.nesting_depth(source)
        functions = self.function_count(source)
        risk, score = self.classify(complexity)
        result = {
            "target": target,
            "complexity": complexity,
            "branches": self.branch_count(source),
            "depth": depth,
            "functions": functions,
            "risk": risk,
            "score": score,
        }
        if target:
            self._analyses[target] = result
        if self.engine is not None:
            self.engine.metrics.gauge(
                "analysis.complexity", complexity, labels={"target": target or "?"}
            )
            self.engine.metrics.increment("analysis.complexity_runs")
        return result

    def get(self, target: str) -> dict[str, Any] | None:
        return self._analyses.get(target)

    def history(self) -> list[dict[str, Any]]:
        return list(self._analyses.values())


__all__ = ["ComplexityAnalyzer"]
