"""Bug fixer — deterministic failure analysis and fix guidance.

Parses traceback-style failure text into a structured analysis (category,
error type, location), derives concrete fix suggestions per category, and
optionally applies a provided replacement through the code generator.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from modules.autonomous_developer.config.constants import OP_MODIFY
from modules.autonomous_developer.core.exceptions import GenerationError
from modules.autonomous_developer.core.models import FileChange
from modules.autonomous_developer.generator.generator import CodeGenerator

_FILE_LINE = re.compile(r'File "([^"]+)", line (\d+)')
_ERROR_HEADER = re.compile(
    r"^\s*(?P<type>[A-Za-z_][A-Za-z0-9_.]*(?:Error|Exception))\s*:\s*(?P<msg>.*)$",
    re.MULTILINE,
)
_IMPORT_MISSING = re.compile(r"No module named '([^']+)'", re.IGNORECASE)
_NAME_UNDEFINED = re.compile(r"'([^']+)' is not defined")


@dataclass(slots=True)
class FailureAnalysis:
    """Structured analysis of a failure description."""

    category: str  # import | syntax | name | attribute | type | value | lookup | generic
    error_type: str = ""
    message: str = ""
    file: str = ""
    line: int | None = None
    summary: str = ""
    suggestions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "category": self.category,
            "error_type": self.error_type,
            "message": self.message,
            "file": self.file,
            "line": self.line,
            "summary": self.summary,
            "suggestions": list(self.suggestions),
        }


_CATEGORY_BY_TYPE = {
    "ModuleNotFoundError": "import",
    "ImportError": "import",
    "SyntaxError": "syntax",
    "NameError": "name",
    "AttributeError": "attribute",
    "TypeError": "type",
    "ValueError": "value",
    "KeyError": "lookup",
    "IndexError": "lookup",
}


def _suggestions(category: str, error_type: str, message: str) -> list[str]:
    if category == "import":
        match = _IMPORT_MISSING.search(message)
        if match:
            return [
                f"Add the missing import for '{match.group(1)}'",
                "Verify the dependency is installed and importable",
            ]
        return [
            "Add or correct the failing import statement",
            "Verify the dependency is installed and importable",
        ]
    if category == "syntax":
        return [
            "Check for missing parentheses, brackets or quotes",
            "Review the reported line and the line directly above it",
        ]
    if category == "name":
        match = _NAME_UNDEFINED.search(message)
        if match:
            return [f"'{match.group(1)}' is not defined — add the missing definition"]
        return ["A name is referenced before it is defined — check spelling and scope"]
    if category == "attribute":
        return [
            "The object does not expose that attribute — check the object type",
            "Confirm the attribute is spelled as defined on the class",
        ]
    if category == "type":
        return [
            "An argument or value has the wrong type — convert it or fix the call site",
        ]
    if category == "value":
        return [
            "A value is invalid for this operation — validate inputs before use",
        ]
    if category == "lookup":
        return [
            "A key or index does not exist — inspect the container's contents",
        ]
    return ["Review the reported location and the surrounding logic"]


class BugFixer:
    """Analyzes failures and guides/creates fixes."""

    def analyze(self, failure_text: str) -> FailureAnalysis:
        """Parse ``failure_text`` into a structured FailureAnalysis."""
        text = failure_text or ""
        file_match = _FILE_LINE.search(text)
        file = file_match.group(1) if file_match else ""
        line = int(file_match.group(2)) if file_match else None

        error_type = ""
        message = ""
        for match in _ERROR_HEADER.finditer(text):
            error_type = match.group("type")
            message = match.group("msg").strip()
        # The last header match is the deepest frame in a traceback.
        if not error_type:
            error_type = "Exception"
            message = text.strip().splitlines()[-1] if text.strip() else "Unknown failure"

        category = _CATEGORY_BY_TYPE.get(error_type, "generic")
        summary = f"{error_type}: {message}" if message else error_type
        return FailureAnalysis(
            category=category,
            error_type=error_type,
            message=message,
            file=file,
            line=line,
            summary=summary,
            suggestions=_suggestions(category, error_type, message),
        )

    def suggest_fix(self, analysis: FailureAnalysis) -> list[str]:
        """Return concrete fix suggestions, plus a location hint when known."""
        suggestions = list(analysis.suggestions)
        if analysis.file:
            location = analysis.file if analysis.line is None else f"{analysis.file}:{analysis.line}"
            suggestions.append(f"Inspect '{location}'")
        return suggestions

    def run(self, ctx, goal: str, session_id: str | None = None, **kwargs: Any) -> FailureAnalysis:
        """Runtime component entry point.

        Requires ``failure`` (failure text). When ``path`` and ``replacement``
        are given, applies the replacement through the code generator.
        """
        failure = kwargs.get("failure")
        if not failure:
            raise GenerationError("A failure description is required for analysis")
        analysis = self.analyze(failure)
        ctx.record("bug_category", analysis.category)
        ctx.record("bug_error_type", analysis.error_type)
        ctx.record("bug_suggestions", len(analysis.suggestions))

        written = 0
        path = kwargs.get("path")
        replacement = kwargs.get("replacement")
        if path and replacement is not None:
            generator = CodeGenerator()
            result = generator.apply_changes(
                [FileChange(path=path, content=replacement, operation=OP_MODIFY)],
                project_root=ctx.config.project_root,
                dry_run=bool(kwargs.get("dry_run", False)),
            )
            written = len(result.written)
            ctx.record("bugfix_files_written", written)
            ctx.record("bugfix_errors", len(result.errors))
        ctx.publish(
            "bugfix.completed",
            {
                "category": analysis.category,
                "error_type": analysis.error_type,
                "written": written,
            },
        )
        return analysis
