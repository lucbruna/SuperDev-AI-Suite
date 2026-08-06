"""Markdown report generator: deterministic orchestrator reports."""
from __future__ import annotations

from typing import Any

from modules.super_ai_orchestrator.api import OrchestratorAPI


class OrchestratorReport:
    """Renders a deterministic Markdown report from the facade state.

    The report is a pure function of the orchestrator state: the same
    kernel state always produces the same Markdown. No clock, no I/O
    except the explicit ``to_file`` write.
    """

    def __init__(self, api: OrchestratorAPI) -> None:
        self._api = api

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def markdown(self) -> str:
        """Render the full report."""
        sections = [
            self._header(),
            self._metrics(),
            self._analytics(),
            self._governance(),
            self._integrations(),
            self._audit(),
        ]
        return "\n\n".join(sections).rstrip() + "\n"

    def to_file(self, path: str) -> str:
        """Write the report to ``path`` (UTF-8); returns the path."""
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(self.markdown())
        return path

    def __str__(self) -> str:
        return self.markdown()

    # ------------------------------------------------------------------ #
    # Sections
    # ------------------------------------------------------------------ #
    def _header(self) -> str:
        health = self._api.health()
        status = health.get("status", "unknown")
        lines = [
            "# Super AI Orchestrator Report",
            f"Version: {self._api.version()}",
            f"Health: {status}",
        ]
        issues = health.get("issues", [])
        if issues:
            lines.append("Issues:")
            lines.extend(f"- {issue}" for issue in issues)
        return "\n".join(lines)

    def _metrics(self) -> str:
        metrics = self._api.health().get("metrics", {})
        rows = "\n".join(
            f"| {key} | {self._fmt(value)} |" for key, value in sorted(metrics.items())
        )
        return "## Metrics\n\n| metric | value |\n|---|---|\n" + rows

    def _analytics(self) -> str:
        analytics = self._api.analytics_report()
        totals = analytics.get("totals", {})
        rows = "\n".join(
            f"| {key} | {self._fmt(value)} |" for key, value in sorted(totals.items())
        )
        sections = [
            "## Analytics",
            "### Totals",
            "| metric | value |\n|---|---|",
            rows,
        ]
        for label, key in (
            ("By kind", "by_kind"),
            ("By owner", "by_owner"),
            ("By llm", "by_llm"),
        ):
            counts = analytics.get(key, {})
            sections.append(f"### {label}")
            if counts:
                rows = "\n".join(
                    f"| {name} | {count} |" for name, count in sorted(counts.items())
                )
                sections.append("| key | count |\n|---|---|")
                sections.append(rows)
            else:
                sections.append("(none)")

        sections.append("### Top failures")
        failures = analytics.get("top_failures", [])
        if failures:
            sections.extend(
                f"- [{f.get('kind', '?')}] {f.get('title', '?')}: "
                f"{f.get('error', '?')}"
                for f in failures
            )
        else:
            sections.append("(none)")
        return "\n".join(sections)

    def _governance(self) -> str:
        policy = self._api.governance_policy()
        lines = ["## Governance"]
        for key in sorted(policy):
            value = policy[key]
            if isinstance(value, (set, frozenset, tuple)):
                rendered = ", ".join(sorted(str(v) for v in value))
            else:
                rendered = str(value)
            lines.append(f"- {key}: {rendered}")
        return "\n".join(lines)

    def _integrations(self) -> str:
        data = self._api.integrations()
        available = data.get("available", [])
        total = data.get("total", len(available))
        lines = [
            "## Integrations",
            f"{len(available)}/{total} connectors available",
        ]
        lines.extend(f"- {name}" for name in available)
        return "\n".join(lines)

    def _audit(self) -> str:
        records = self._api.audit()[-10:]
        lines = ["## Recent audit"]
        if not records:
            lines.append("(none)")
            return "\n".join(lines)
        for record in records:
            detail = record.get("detail", {})
            extra = f" {self._compact(detail)}" if detail else ""
            lines.append(
                f"- #{record.get('task_seq', '?')} {record.get('kind', '?')}"
                f"{extra}"
            )
        return "\n".join(lines)

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    @staticmethod
    def _fmt(value: Any) -> str:
        if value is None:
            return "-"
        if isinstance(value, float):
            return f"{value:.4f}"
        return str(value)

    @staticmethod
    def _compact(detail: dict[str, Any]) -> str:
        parts = []
        for key in sorted(detail):
            value = detail[key]
            if isinstance(value, (dict, list)):
                continue
            parts.append(f"{key}={value}")
        return "(" + ", ".join(parts) + ")" if parts else ""
