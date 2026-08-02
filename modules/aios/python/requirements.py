"""Python requirements — parse, render and round-trip requirements files."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Sequence

_LINE_RE = re.compile(
    r"^\s*(?P<name>[A-Za-z0-9_.\-]+)\s*(?P<spec>[<>=!~;\[].*?)?\s*(?P<comment>\s*#.*)?$"
)


class Requirement:
    """One pinned/loose dependency line (name + optional specifier)."""

    __slots__ = ("name", "specifier", "comment")

    def __init__(self, name: str, specifier: str = "", comment: str = "") -> None:
        self.name = name
        self.specifier = specifier.strip()
        self.comment = comment

    @classmethod
    def from_line(cls, line: str) -> Requirement | None:
        text = line.strip()
        if not text or text.startswith("#"):
            return None
        match = _LINE_RE.match(text)
        if not match:
            return None
        return cls(
            name=match.group("name"),
            specifier=(match.group("spec") or "").strip(),
            comment=(match.group("comment") or "").strip(),
        )

    def to_line(self) -> str:
        line = self.name
        if self.specifier:
            line += self.specifier
        if self.comment:
            line += f"  {self.comment}"
        return line

    def as_dict(self) -> dict[str, str]:
        return {"name": self.name, "specifier": self.specifier, "comment": self.comment}

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"Requirement({self.to_line()!r})"


def parse_requirements(text: str) -> list[Requirement]:
    """Parse requirement lines (comments and blanks are skipped)."""
    return [
        req
        for line in text.splitlines()
        if (req := Requirement.from_line(line)) is not None
    ]


def render_requirements(
    requirements: Sequence[Requirement | dict[str, str] | str],
) -> str:
    """Render requirements back to text (round-trip for parsed lists)."""
    lines: list[str] = []
    for req in requirements:
        if isinstance(req, str):
            lines.append(req)
        elif isinstance(req, dict):
            item = req.get("name", "")
            spec = req.get("specifier", "")
            comment = req.get("comment", "")
            lines.append(
                Requirement(name=item, specifier=spec, comment=comment).to_line()
            )
        else:
            lines.append(req.to_line())
    return "\n".join(lines) + ("\n" if lines else "")


def parse_file(path: str | Path) -> list[Requirement]:
    return parse_requirements(Path(path).read_text(encoding="utf-8"))


def write_file(path: str | Path, requirements: list[Requirement]) -> None:
    Path(path).write_text(render_requirements(requirements), encoding="utf-8")


__all__ = [
    "Requirement",
    "parse_requirements",
    "render_requirements",
    "parse_file",
    "write_file",
]
