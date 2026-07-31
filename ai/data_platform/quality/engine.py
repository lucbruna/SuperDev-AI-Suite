"""Quality engine."""
import uuid
from typing import Any

from .models import QualityCheck, QualityReport, QualityRule, QualityStatus


class QualityEngine:
    def __init__(self):
        self._rules: dict[str, QualityRule] = {}
        self._checks: list[QualityCheck] = []
        self._reports: list[QualityReport] = []

    def add_rule(self, rule: QualityRule) -> QualityRule:
        self._rules[rule.rule_id] = rule
        return rule

    def get_rule(self, rule_id: str) -> QualityRule | None:
        return self._rules.get(rule_id)

    def check_completeness(self, dataset: str, records: list[dict[str, Any]], required_fields: list[str]) -> QualityCheck:
        total = len(records)
        issues = []
        incomplete = 0
        for i, r in enumerate(records):
            missing = [f for f in required_fields if not r.get(f)]
            if missing:
                incomplete += 1
                issues.append({"record_index": i, "missing_fields": missing})
        score = (total - incomplete) / total if total > 0 else 1.0
        check = QualityCheck(
            check_id=str(uuid.uuid4())[:8],
            dataset=dataset,
            status=QualityStatus.PASSED if score >= 0.95 else QualityStatus.FAILED,
            score=score,
            issues=issues,
        )
        self._checks.append(check)
        return check

    def check_uniqueness(self, dataset: str, records: list[dict[str, Any]], key_field: str) -> QualityCheck:
        seen: dict[Any, int] = {}
        issues = []
        for i, r in enumerate(records):
            key = r.get(key_field)
            if key in seen:
                seen[key] += 1
                issues.append({"record_index": i, "duplicate_key": key, "count": seen[key]})
            else:
                seen[key] = 1
        duplicates = sum(1 for v in seen.values() if v > 1)
        score = (len(records) - duplicates) / len(records) if records else 1.0
        check = QualityCheck(
            check_id=str(uuid.uuid4())[:8],
            dataset=dataset,
            status=QualityStatus.PASSED if score >= 0.95 else QualityStatus.FAILED,
            score=score,
            issues=issues,
        )
        self._checks.append(check)
        return check

    def check_validity(self, dataset: str, records: list[dict[str, Any]], validations: dict[str, Any]) -> QualityCheck:
        issues = []
        invalid = 0
        for i, r in enumerate(records):
            for field_name, expected_type in validations.items():
                value = r.get(field_name)
                if value is not None:
                    if expected_type == "string" and not isinstance(value, str) or expected_type == "number" and not isinstance(value, (int, float)):
                        invalid += 1
                        issues.append({"record_index": i, "field": field_name, "issue": "type_mismatch"})
        total_fields = len(records) * len(validations) if records else 1
        score = (total_fields - invalid) / total_fields if total_fields > 0 else 1.0
        check = QualityCheck(
            check_id=str(uuid.uuid4())[:8],
            dataset=dataset,
            status=QualityStatus.PASSED if score >= 0.95 else QualityStatus.FAILED,
            score=score,
            issues=issues,
        )
        self._checks.append(check)
        return check

    def generate_report(self, dataset: str) -> QualityReport:
        dataset_checks = [c for c in self._checks if c.dataset == dataset]
        passed = sum(1 for c in dataset_checks if c.status == QualityStatus.PASSED)
        failed = sum(1 for c in dataset_checks if c.status == QualityStatus.FAILED)
        warnings = sum(1 for c in dataset_checks if c.status == QualityStatus.WARNING)
        overall = sum(c.score for c in dataset_checks) / len(dataset_checks) if dataset_checks else 1.0
        report = QualityReport(
            report_id=str(uuid.uuid4())[:8],
            dataset=dataset,
            checks=dataset_checks,
            overall_score=overall,
            passed=passed,
            failed=failed,
            warnings=warnings,
        )
        self._reports.append(report)
        return report

    def get_checks(self, dataset: str | None = None) -> list[QualityCheck]:
        if dataset:
            return [c for c in self._checks if c.dataset == dataset]
        return list(self._checks)

    def get_reports(self, dataset: str | None = None) -> list[QualityReport]:
        if dataset:
            return [r for r in self._reports if r.dataset == dataset]
        return list(self._reports)

    def get_stats(self) -> dict:
        return {
            "rules": len(self._rules),
            "checks": len(self._checks),
            "reports": len(self._reports),
            "passed": sum(1 for c in self._checks if c.status == QualityStatus.PASSED),
            "failed": sum(1 for c in self._checks if c.status == QualityStatus.FAILED),
        }
