from __future__ import annotations

import difflib
import os
from typing import Any


class DiffAnalyzer:
    def analyze_diff(self, old_content: str, new_content: str, filename: str = "") -> dict[str, Any]:
        old_lines = old_content.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)
        diff = list(difflib.unified_diff(old_lines, new_lines, fromfile=f"a/{filename}", tofile=f"b/{filename}"))
        added_lines = [l[1:] for l in diff if l.startswith("+") and not l.startswith("+++") and not l.startswith("---")]
        removed_lines = [l[1:] for l in diff if l.startswith("-") and not l.startswith("---") and not l.startswith("+++")]
        return {
            "filename": filename,
            "diff": "".join(diff),
            "additions": len(added_lines),
            "deletions": len(removed_lines),
            "total_changes": len([l for l in diff if l.startswith("+") or l.startswith("-")]),
            "added_content": "\n".join(added_lines),
            "removed_content": "\n".join(removed_lines),
            "significance": self._calculate_significance(len(added_lines), len(removed_lines), new_content),
        }

    def analyze_diff_file(self, filepath_a: str, filepath_b: str) -> dict[str, Any]:
        if not os.path.exists(filepath_a) or not os.path.exists(filepath_b):
            return {"error": "File not found"}
        with open(filepath_a, encoding="utf-8", errors="ignore") as f:
            old_content = f.read()
        with open(filepath_b, encoding="utf-8", errors="ignore") as f:
            new_content = f.read()
        return self.analyze_diff(old_content, new_content, os.path.basename(filepath_a))

    def classify_change(self, diff_text: str) -> str:
        lines = diff_text.split("\n")
        for line in lines:
            if line.startswith("+") and any(kw in line.lower() for kw in ("def ", "class ", "async def", "@")):
                return "structural"
            if line.startswith("+") and any(kw in line.lower() for kw in ("import ", "from ")):
                return "dependency"
            if line.startswith("+") and any(kw in line.lower() for kw in ("print(", "logger.", "logging.")):
                return "logging"
            if line.startswith("+") and "TODO" in line:
                return "incomplete"
        return "modification"

    def _calculate_significance(self, additions: int, deletions: int, new_content: str) -> str:
        total_lines = new_content.count("\n") + 1
        change_ratio = (additions + deletions) / max(total_lines, 1)
        if change_ratio > 0.5:
            return "major"
        if change_ratio > 0.2:
            return "moderate"
        return "minor"
