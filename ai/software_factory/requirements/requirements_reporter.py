"""Reporter for requirements analysis and status reports."""
from typing import List, Dict, Any, Optional
from datetime import datetime
from .models import Requirement, RequirementSet
from .requirements_analyzer import RequirementsAnalyzer
from .requirements_mapper import RequirementsMapper


class RequirementsReporter:
    """Generates reports on requirements status, quality, and coverage."""

    def __init__(self):
        self.analyzer = RequirementsAnalyzer()
        self.mapper = RequirementsMapper()

    def generate_status_report(self, req_set: RequirementSet) -> Dict[str, Any]:
        """Generate a status report for a requirement set."""
        analysis = self.analyzer.analyze_set(req_set)
        quality = self.analyzer.compute_quality_score(req_set)
        return {
            "report_type": "status",
            "generated_at": datetime.utcnow().isoformat(),
            "set_name": req_set.name,
            "summary": analysis,
            "quality_score": quality,
        }

    def generate_coverage_report(self, requirements: List[Requirement]) -> Dict[str, Any]:
        """Generate a coverage report."""
        coverage = self.mapper.compute_coverage(requirements)
        return {
            "report_type": "coverage",
            "generated_at": datetime.utcnow().isoformat(),
            "coverage": coverage,
        }

    def generate_gap_report(self, req_set: RequirementSet) -> Dict[str, Any]:
        """Generate a gap analysis report."""
        gaps = self.analyzer.find_gaps(req_set)
        return {
            "report_type": "gaps",
            "generated_at": datetime.utcnow().isoformat(),
            "total_gaps": len(gaps),
            "gaps": gaps,
        }

    def generate_full_report(self, req_set: RequirementSet) -> Dict[str, Any]:
        """Generate a comprehensive report combining all report types."""
        return {
            "report_type": "full",
            "generated_at": datetime.utcnow().isoformat(),
            "status": self.generate_status_report(req_set),
            "coverage": self.generate_coverage_report(req_set.requirements),
            "gaps": self.generate_gap_report(req_set),
        }

    def export_summary(self, req_set: RequirementSet) -> str:
        """Export a text summary."""
        report = self.generate_status_report(req_set)
        lines = [
            f"Requirements Report: {req_set.name}",
            f"Generated: {report['generated_at']}",
            f"Total Requirements: {report['summary']['total']}",
            f"Quality Score: {report['quality_score']:.2f}",
            f"Approved Ratio: {report['summary']['approved_ratio']:.2%}",
        ]
        return "\n".join(lines)
