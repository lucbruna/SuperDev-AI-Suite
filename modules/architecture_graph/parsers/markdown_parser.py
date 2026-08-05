"""Markdown parser: extracts headings and cross-references to code files."""
from __future__ import annotations

import re
from typing import Any

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
_REF_RE = re.compile(r"`?([\w./\-]+\.(?:py|ts|tsx|js|jsx|yaml|yml|json|md))`?")


def parse(text: str, path: str = "") -> dict[str, Any]:
    headings: list[dict[str, str]] = []
    refs: list[str] = []
    for line in text.splitlines():
        match = _HEADING_RE.match(line)
        if match:
            headings.append({"level": str(len(match.group(1))), "title": match.group(2).strip()})
        for ref in _REF_RE.findall(line):
            refs.append(ref)
    title = headings[0]["title"] if headings else (path.split("/")[-1] if path else "")
    return {
        "title": title,
        "headings": headings,
        "code_refs": list(dict.fromkeys(refs)),
    }
