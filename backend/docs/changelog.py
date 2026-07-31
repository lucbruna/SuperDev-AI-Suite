from __future__ import annotations

import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class ChangelogGenerator:
    def __init__(self, repo_path: str | None = None):
        self._repo = Path(repo_path) if repo_path else Path.cwd()
        self._commits: list[dict[str, Any]] = []

    def _git_log(self, since: str | None = None, max_count: int = 100) -> list[dict[str, Any]]:
        args = ["git", "log", f"--max-count={max_count}", "--format=%H|%ai|%an|%s"]
        if since:
            args.insert(2, f"--since={since}")
        try:
            result = subprocess.run(args, capture_output=True, text=True, cwd=str(self._repo), timeout=10)
            if result.returncode != 0:
                return []
            commits = []
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                parts = line.split("|", 3)
                if len(parts) == 4:
                    commits.append({"hash": parts[0][:8], "date": parts[1], "author": parts[2], "message": parts[3]})
            return commits
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return []

    def _categorize(self, message: str) -> str:
        msg = message.lower()
        if msg.startswith("feat") or msg.startswith("feature") or msg.startswith("add"):
            return "Features"
        if msg.startswith("fix") or msg.startswith("bugfix") or msg.startswith("hotfix"):
            return "Bug Fixes"
        if msg.startswith("refactor") or msg.startswith("refac"):
            return "Refactoring"
        if msg.startswith("docs") or msg.startswith("document"):
            return "Documentation"
        if msg.startswith("test"):
            return "Tests"
        if msg.startswith("ci") or msg.startswith("cd") or msg.startswith("deploy"):
            return "CI/CD"
        if msg.startswith("perf") or msg.startswith("optimize"):
            return "Performance"
        if msg.startswith("style") or msg.startswith("lint"):
            return "Style"
        if msg.startswith("chore") or msg.startswith("build") or msg.startswith("deps"):
            return "Chores"
        return "Other"

    def generate(self, since: str | None = None, max_count: int = 100) -> dict[str, Any]:
        self._commits = self._git_log(since, max_count)
        categorized: dict[str, list[dict[str, Any]]] = {}
        for c in self._commits:
            cat = self._categorize(c["message"])
            if cat not in categorized:
                categorized[cat] = []
            categorized[cat].append(c)
        return {
            "generated_at": datetime.now(UTC).isoformat(),
            "total_commits": len(self._commits),
            "since": since or "all time",
            "categories": {k: len(v) for k, v in categorized.items()},
            "commits": categorized,
        }

    def to_markdown(self, data: dict[str, Any] | None = None) -> str:
        d = data or self._commits
        if isinstance(d, list):
            d = {"total_commits": len(d), "categories": {}, "commits": {"All": d}}
        lines = ["# Changelog", f"Generated: {d.get('generated_at', 'N/A')}", f"Total commits: {d.get('total_commits', 0)}", ""]
        for category, commits in d.get("commits", {}).items():
            if not commits:
                continue
            lines.append(f"## {category}")
            for c in commits:
                lines.append(f"- `{c['hash']}` {c['message']} ({c['author']}, {c['date'][:10]})")
            lines.append("")
        return "\n".join(lines)

    def generate_and_save(self, output_path: str, since: str | None = None) -> str:
        data = self.generate(since)
        markdown = self.to_markdown(data)
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(markdown, encoding="utf-8")
        return str(output_file)