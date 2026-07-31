"""Analyzer for code complexity metrics."""

from .models import QualityMetric


class ComplexityAnalyzer:
    """Analyzes code complexity and quality metrics."""

    def __init__(self):
        self._thresholds = {
            "max_functions": 50,
            "max_classes": 10,
            "max_line_length": 100,
        }

    def analyze(self, content: str) -> list[QualityMetric]:
        metrics = []
        lines = content.split("\n")
        code_lines = [l for l in lines if l.strip() and not l.strip().startswith("#")]
        blank_lines = [l for l in lines if not l.strip()]
        comment_lines = [l for l in lines if l.strip().startswith("#")]

        metrics.append(QualityMetric(name="total_lines", value=len(lines), unit="lines"))
        metrics.append(QualityMetric(name="code_lines", value=len(code_lines), unit="lines"))
        metrics.append(QualityMetric(name="blank_lines", value=len(blank_lines), unit="lines"))
        metrics.append(QualityMetric(name="comment_lines", value=len(comment_lines), unit="lines"))

        func_count = sum(1 for l in code_lines if l.strip().startswith("def "))
        class_count = sum(1 for l in code_lines if l.strip().startswith("class "))
        metrics.append(QualityMetric(name="functions", value=func_count, threshold=1, unit="count"))
        metrics.append(QualityMetric(name="classes", value=class_count, threshold=0, unit="count"))

        avg_line_length = sum(len(l) for l in code_lines) / len(code_lines) if code_lines else 0
        metrics.append(QualityMetric(name="avg_line_length", value=avg_line_length, threshold=0, unit="chars"))

        return metrics

    def cyclomatic_complexity(self, content: str) -> int:
        """Estimate cyclomatic complexity."""
        complexity = 1
        keywords = ["if ", "elif ", "for ", "while ", "except ", "with "]
        for line in content.split("\n"):
            stripped = line.strip()
            for kw in keywords:
                if stripped.startswith(kw) or (" " + kw) in stripped:
                    complexity += 1
        return complexity

    def maintainability_index(self, content: str) -> float:
        """Compute a maintainability index (0-100)."""
        lines = content.split("\n")
        total_lines = len(lines)
        if total_lines == 0:
            return 100.0

        complexity = self.cyclomatic_complexity(content)
        comment_ratio = sum(1 for l in lines if l.strip().startswith("#")) / total_lines

        score = 100.0
        score -= min(20, complexity * 2)
        score -= min(20, max(0, total_lines - 100) * 0.1)
        score += comment_ratio * 10
        return max(0.0, min(100.0, score))
