"""Analyzer for requirements quality metrics and insights."""
from collections import Counter
from typing import Any

from .models import RequirementSet, RequirementStatus


class RequirementsAnalyzer:
    """Analyzes requirement sets for metrics, coverage, and quality."""

    def analyze_set(self, req_set: RequirementSet) -> dict[str, Any]:
        """Full analysis of a requirement set."""
        requirements = req_set.requirements
        if not requirements:
            return {"empty": True, "total": 0}

        type_dist = Counter(r.requirement_type.value for r in requirements)
        prio_dist = Counter(r.priority.value for r in requirements)
        status_dist = Counter(r.status.value for r in requirements)

        with_criteria = sum(1 for r in requirements if r.acceptance_criteria)
        with_deps = sum(1 for r in requirements if r.dependencies)
        avg_criteria = (
            sum(len(r.acceptance_criteria) for r in requirements) / len(requirements)
        )

        return {
            "total": len(requirements),
            "type_distribution": dict(type_dist),
            "priority_distribution": dict(prio_dist),
            "status_distribution": dict(status_dist),
            "with_acceptance_criteria": with_criteria,
            "acceptance_criteria_ratio": with_criteria / len(requirements),
            "with_dependencies": with_deps,
            "avg_acceptance_criteria": avg_criteria,
            "approved_ratio": status_dist.get("approved", 0) / len(requirements),
        }

    def find_gaps(self, req_set: RequirementSet) -> list[dict[str, Any]]:
        """Find requirements with missing information."""
        gaps = []
        for req in req_set.requirements:
            issues = []
            if not req.description:
                issues.append("missing_description")
            if not req.acceptance_criteria:
                issues.append("missing_acceptance_criteria")
            if not req.tags:
                issues.append("missing_tags")
            if not req.author:
                issues.append("missing_author")
            if issues:
                gaps.append({"requirement_id": req.requirement_id, "title": req.title, "issues": issues})
        return gaps

    def compute_quality_score(self, req_set: RequirementSet) -> float:
        """Compute a 0-1 quality score for the requirement set."""
        if not req_set.requirements:
            return 0.0
        total = 0.0
        for req in req_set.requirements:
            score = 0.0
            if req.title:
                score += 0.2
            if req.description:
                score += 0.2
            if req.acceptance_criteria:
                score += 0.2
            if req.tags:
                score += 0.1
            if req.dependencies:
                score += 0.1
            if req.author:
                score += 0.1
            if req.status != RequirementStatus.DRAFT:
                score += 0.1
            total += score
        return total / len(req_set.requirements)

    def summarize(self, req_set: RequirementSet) -> dict[str, Any]:
        """Generate a summary of the requirement set."""
        analysis = self.analyze_set(req_set)
        gaps = self.find_gaps(req_set)
        quality = self.compute_quality_score(req_set)
        return {
            "set_name": req_set.name,
            "analysis": analysis,
            "gaps_count": len(gaps),
            "quality_score": quality,
            "gaps": gaps[:5],
        }
