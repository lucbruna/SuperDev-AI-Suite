from __future__ import annotations

import difflib
from dataclasses import dataclass, field
from typing import Any


@dataclass
class DiffHunk:
    """A single diff hunk between two versions."""

    old_start: int
    old_count: int
    new_start: int
    new_count: int
    lines: list[dict[str, Any]]  # {"op": "-"|"+"|" ", "text": str}


@dataclass
class FileDiff:
    """A complete file diff."""

    path: str
    hunks: list[DiffHunk] = field(default_factory=list)
    additions: int = 0
    deletions: int = 0

    @property
    def changed(self) -> bool:
        return self.additions > 0 or self.deletions > 0


class DiffViewer:
    """Computes unified diffs between file versions."""

    def __init__(self) -> None:
        self._diffs: dict[str, FileDiff] = {}

    def compare(self, path: str, old_text: str, new_text: str) -> FileDiff:
        old_lines = old_text.splitlines(keepends=True)
        new_lines = new_text.splitlines(keepends=True)
        sm = difflib.SequenceMatcher(None, old_lines, new_lines)
        hunks: list[DiffHunk] = []
        additions = 0
        deletions = 0
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == "equal":
                continue
            lines: list[dict[str, Any]] = []
            for line in old_lines[i1:i2]:
                lines.append({"op": "-", "text": line.rstrip("\n")})
                deletions += 1
            for line in new_lines[j1:j2]:
                lines.append({"op": "+", "text": line.rstrip("\n")})
                additions += 1
            hunks.append(
                DiffHunk(
                    old_start=i1,
                    old_count=i2 - i1,
                    new_start=j1,
                    new_count=j2 - j1,
                    lines=lines,
                )
            )
        file_diff = FileDiff(path=path, hunks=hunks, additions=additions, deletions=deletions)
        self._diffs[path] = file_diff
        return file_diff

    def get(self, path: str) -> FileDiff | None:
        return self._diffs.get(path)

    def list(self) -> list[FileDiff]:
        return list(self._diffs.values())

    def apply(self, path: str, target_text: str, accept_additions: bool = True) -> str:
        file_diff = self._diffs.get(path)
        if file_diff is None:
            return target_text
        target_lines = target_text.splitlines(keepends=True)
        result: list[str] = []
        index = 0
        for hunk in file_diff.hunks:
            while index < hunk.old_start and index < len(target_lines):
                result.append(target_lines[index])
                index += 1
            for line in hunk.lines:
                if line["op"] == "+":
                    result.append(line["text"] + "\n")
                else:
                    if index < len(target_lines) and target_lines[index].rstrip("\n") == line["text"]:
                        index += 1
        while index < len(target_lines):
            result.append(target_lines[index])
            index += 1
        return "".join(result)

    def clear(self) -> None:
        self._diffs.clear()
