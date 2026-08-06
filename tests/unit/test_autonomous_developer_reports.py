"""Tests for report generation (Phase H)."""
from __future__ import annotations

from modules.autonomous_developer.config import DeveloperConfig
from modules.autonomous_developer.core import DeveloperContext, DeveloperRegistry
from modules.autonomous_developer.reports import Report, ReportGenerator, ReportSection


def make_context(tmp_path):
    return DeveloperContext(
        config=DeveloperConfig(project_root=tmp_path),
        registry=DeveloperRegistry(),
    )


class TestReport:
    def test_to_markdown(self):
        report = Report(
            title="T",
            sections=[
                ReportSection("Goal", "Build X"),
                ReportSection("Stats", "- a: 1"),
            ],
        )
        assert report.to_markdown() == "# T\n\n## Goal\n\nBuild X\n\n## Stats\n\n- a: 1\n"

    def test_defaults(self):
        report = Report(title="T")
        assert report.sections == []
        assert report.to_markdown() == "# T\n"


class TestReportGenerator:
    def test_session_report_stats_sorted(self, tmp_path):
        ctx = make_context(tmp_path)
        ctx.record("zebra", 1)
        ctx.record("alpha", 2)
        report = ReportGenerator().session_report(ctx, goal="Build X")
        assert report.title == "Session Report"
        bodies = {section.heading: section.body for section in report.sections}
        assert bodies["Goal"] == "Build X"
        assert bodies["Stats"] == "- alpha: 2\n- zebra: 1"

    def test_session_report_empty_stats(self, tmp_path):
        ctx = make_context(tmp_path)
        bodies = {
            section.heading: section.body
            for section in ReportGenerator().session_report(ctx).sections
        }
        assert bodies["Stats"] == "_none_"
        assert bodies["Artifacts"] == "_none_"

    def test_session_report_artifact_types(self, tmp_path):
        ctx = make_context(tmp_path)
        ctx.set_artifact("plan", {"id": 1})
        bodies = {
            section.heading: section.body
            for section in ReportGenerator().session_report(ctx).sections
        }
        assert bodies["Artifacts"] == "- plan: dict"

    def test_summary_report(self, tmp_path):
        ctx = make_context(tmp_path)
        ctx.record("a", 1)
        report = ReportGenerator().summary_report(ctx)
        assert report.title == "Summary Report"
        assert report.sections[0].body == "Recorded 1 stat(s)."
        assert report.sections[1].body == "Produced 0 artifact(s)."

    def test_run_records_and_publishes(self, tmp_path):
        ctx = make_context(tmp_path)
        report = ReportGenerator().run(ctx, "Build X")
        assert report.title == "Session Report"
        assert ctx.stats["report_sections"] == len(report.sections)
