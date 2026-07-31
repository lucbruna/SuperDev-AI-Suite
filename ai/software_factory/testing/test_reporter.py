"""Reporter for test results and coverage."""
from typing import List, Dict, Any
from collections import Counter
from .models import TestResult, TestStatus, CoverageReport


class TestReporter:
    """Generates reports from test results."""

    def __init__(self):
        self._reports: List[Dict[str, Any]] = []

    def generate_report(self, results: List[TestResult]) -> Dict[str, Any]:
        total = len(results)
        status_counts = Counter(r.status.value for r in results)
        passed = status_counts.get("passed", 0)
        failed = status_counts.get("failed", 0)
        skipped = status_counts.get("skipped", 0)

        total_duration = sum(r.duration for r in results)
        total_assertions = sum(r.assertions_passed + r.assertions_failed for r in results)

        report = {
            "total": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "pass_rate": passed / total if total > 0 else 0.0,
            "total_duration": total_duration,
            "total_assertions": total_assertions,
            "status_distribution": dict(status_counts),
            "failed_tests": [
                {"name": r.test_name, "message": r.message}
                for r in results if r.status == TestStatus.FAILED
            ],
        }
        self._reports.append(report)
        return report

    def generate_coverage_summary(self, coverage: CoverageReport) -> Dict[str, Any]:
        return {
            "line_coverage": coverage.line_coverage,
            "function_coverage": coverage.function_coverage,
            "total_lines": coverage.total_lines,
            "covered_lines": coverage.covered_lines,
            "files_covered": len(coverage.files),
        }

    def get_all_reports(self) -> List[Dict[str, Any]]:
        return list(self._reports)

    def format_text(self, report: Dict[str, Any]) -> str:
        lines = [
            "=== Test Report ===",
            f"Total: {report['total']}",
            f"Passed: {report['passed']}",
            f"Failed: {report['failed']}",
            f"Pass Rate: {report['pass_rate']:.1%}",
            f"Duration: {report['total_duration']:.3f}s",
        ]
        if report['failed_tests']:
            lines.append("\nFailed Tests:")
            for ft in report['failed_tests']:
                lines.append(f"  - {ft['name']}: {ft['message']}")
        return "\n".join(lines)
