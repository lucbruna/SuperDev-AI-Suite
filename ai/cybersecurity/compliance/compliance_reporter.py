"""
Compliance Reporting
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json


class ReportFormat(Enum):
    JSON = "json"
    SUMMARY = "summary"
    EXECUTIVE = "executive"
    DETAILED = "detailed"


class TrendDirection(Enum):
    IMPROVING = "improving"
    DECLINING = "declining"
    STABLE = "stable"


@dataclass
class ComplianceMetric:
    metric_name: str
    value: float
    target: float = 100.0
    unit: str = "percentage"
    trend: TrendDirection = TrendDirection.STABLE
    measured_at: datetime = field(default_factory=datetime.now)


@dataclass
class ComplianceReport:
    report_id: str
    framework: str
    format: ReportFormat = ReportFormat.SUMMARY
    metrics: List[ComplianceMetric] = field(default_factory=list)
    overall_score: float = 0.0
    findings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.now)


class ComplianceReporter:
    def __init__(self):
        self.metrics: Dict[str, List[ComplianceMetric]] = {}
        self.reports: List[ComplianceReport] = []

    def record_metric(self, metric_name: str, value: float, target: float = 100.0, trend: TrendDirection = TrendDirection.STABLE) -> ComplianceMetric:
        metric = ComplianceMetric(metric_name=metric_name, value=value, target=target, trend=trend)
        self.metrics.setdefault(metric_name, []).append(metric)
        return metric

    def generate_report(self, framework: str, format: ReportFormat = ReportFormat.SUMMARY) -> ComplianceReport:
        all_metrics = []
        for metric_list in self.metrics.values():
            if metric_list:
                all_metrics.append(metric_list[-1])
        overall = sum(m.value for m in all_metrics) / max(len(all_metrics), 1)
        findings = [f"Metric {m.metric_name}: {m.value}%" for m in all_metrics if m.value < m.target]
        recs = ["Improve " + m.metric_name for m in all_metrics if m.value < m.target]
        report = ComplianceReport(report_id=f"report_{len(self.reports)}", framework=framework, format=format, metrics=all_metrics, overall_score=overall, findings=findings, recommendations=recs)
        self.reports.append(report)
        return report

    def get_trend(self, metric_name: str) -> TrendDirection:
        metric_list = self.metrics.get(metric_name, [])
        if len(metric_list) < 2:
            return TrendDirection.STABLE
        recent = metric_list[-1].value
        previous = metric_list[-2].value
        if recent > previous:
            return TrendDirection.IMPROVING
        elif recent < previous:
            return TrendDirection.DECLINING
        return TrendDirection.STABLE

    def get_executive_summary(self, framework: str) -> Dict[str, Any]:
        framework_metrics = []
        for metric_list in self.metrics.values():
            if metric_list:
                framework_metrics.append(metric_list[-1])
        overall = sum(m.value for m in framework_metrics) / max(len(framework_metrics), 1)
        return {"framework": framework, "overall_score": overall, "total_metrics": len(framework_metrics), "below_target": sum(1 for m in framework_metrics if m.value < m.target)}

    def get_reports(self, framework: str = None) -> List[ComplianceReport]:
        if framework:
            return [r for r in self.reports if r.framework == framework]
        return self.reports

    def count(self) -> int:
        return len(self.reports)
