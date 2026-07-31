"""Analyzer for test coverage metrics."""
from typing import Any

from .models import CoverageReport


class CoverageAnalyzer:
    """Analyzes test coverage across codebase."""

    def __init__(self):
        self._reports: list[CoverageReport] = []

    def create_report(self) -> CoverageReport:
        report = CoverageReport()
        self._reports.append(report)
        return report

    def add_file_coverage(self, report: CoverageReport, file_path: str,
                          total_lines: int, covered_lines: int,
                          total_functions: int, covered_functions: int) -> None:
        report.files[file_path] = {
            "total_lines": total_lines,
            "covered_lines": covered_lines,
            "total_functions": total_functions,
            "covered_functions": covered_functions,
        }
        report.total_lines += total_lines
        report.covered_lines += covered_lines
        report.total_functions += total_functions
        report.covered_functions += covered_functions

    def compute_gaps(self, report: CoverageReport, threshold: float = 0.8) -> list[dict[str, Any]]:
        gaps = []
        for file_path, data in report.files.items():
            line_cov = data["covered_lines"] / data["total_lines"] if data["total_lines"] > 0 else 0
            if line_cov < threshold:
                gaps.append({
                    "file": file_path,
                    "line_coverage": line_cov,
                    "missing_lines": data["total_lines"] - data["covered_lines"],
                })
        return gaps

    def get_summary(self, report: CoverageReport) -> dict[str, Any]:
        return {
            "total_lines": report.total_lines,
            "covered_lines": report.covered_lines,
            "line_coverage": report.line_coverage,
            "total_functions": report.total_functions,
            "covered_functions": report.covered_functions,
            "function_coverage": report.function_coverage,
            "files_analyzed": len(report.files),
        }

    def get_all_reports(self) -> list[CoverageReport]:
        return list(self._reports)
