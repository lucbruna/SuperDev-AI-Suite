from __future__ import annotations

import ast
import logging
import re
import subprocess  # nosec
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger("superdev.ai.bugs")


class BugSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class BugCategory(str, Enum):
    NULL_POINTER = "null_pointer"
    INDEX_ERROR = "index_error"
    TYPE_ERROR = "type_error"
    RACE_CONDITION = "race_condition"
    MEMORY_LEAK = "memory_leak"
    DEADLOCK = "deadlock"
    INFINITE_LOOP = "infinite_loop"
    RESOURCE_LEAK = "resource_leak"
    LOGIC_ERROR = "logic_error"
    OFF_BY_ONE = "off_by_one"
    DIVISION_BY_ZERO = "division_by_zero"
    UNUSED_VARIABLE = "unused_variable"
    UNREACHABLE_CODE = "unreachable_code"
    DEPRECATED_API = "deprecated_api"
    SECURITY = "security"
    PERFORMANCE = "performance"
    CONVENTION = "convention"
    REFACTOR_SUGGESTION = "refactor_suggestion"


BUG_PATTERNS: dict[str, dict[str, Any]] = {
    "division_by_zero": {
        "regex": r"(?<!/)/(?!\s*0\b)(?!/)",
        "severity": BugSeverity.HIGH,
        "category": BugCategory.DIVISION_BY_ZERO,
        "message": "Possible division by zero. Ensure denominator is not zero before division.",
        "fix_suggestion": "Add a check: `if denominator != 0:` before the division.",
    },
    "bare_except": {
        "regex": r"\bexcept\s*:",
        "severity": BugSeverity.LOW,
        "category": BugCategory.CONVENTION,
        "message": "Bare except clause catches all exceptions. Specify exception types.",
        "fix_suggestion": "Use `except SpecificException:` instead of bare `except:`.",
    },
    "print_statement": {
        "regex": r"\bprint\s*\(",
        "severity": BugSeverity.LOW,
        "category": BugCategory.CONVENTION,
        "message": "Print statement detected in production code. Use logging instead.",
        "fix_suggestion": "Replace `print()` with `logger.info()` or `logger.debug()`.",
    },
    "mutable_default_arg": {
        "regex": r"def \w+\([^)]*\b(\w+)\s*=\s*(\[\]|\{\}|set\(\))",
        "severity": BugSeverity.HIGH,
        "category": BugCategory.LOGIC_ERROR,
        "message": "Mutable default argument is shared across all calls.",
        "fix_suggestion": "Use `None` as default and create the mutable inside the function.",
    },
    "comparison_with_self": {
        "regex": r"(\w+)\s*(==|!=|<=|>=|<|>)\s*\1\b(?!\s*==)",
        "severity": BugSeverity.MEDIUM,
        "category": BugCategory.LOGIC_ERROR,
        "message": "Comparison with self is always True/False. Check the variable name.",
        "fix_suggestion": "Verify the comparison target. You likely meant to compare with a different value.",
    },
    "hardcoded_password": {
        "regex": r"(password|passwd|pwd|secret|token)\s*=\s*['\"][^'\"]{4,}['\"]",
        "severity": BugSeverity.CRITICAL,
        "category": BugCategory.SECURITY,
        "message": "Hardcoded credential detected. Use environment variables or secrets manager.",
        "fix_suggestion": "Move the credential to an environment variable or a secrets vault.",
    },
    "sql_injection": {
        "regex": r"(execute|executemany|raw_sql|query)\s*\(\s*f['\"]",
        "severity": BugSeverity.CRITICAL,
        "category": BugCategory.SECURITY,
        "message": "Possible SQL injection via f-string. Use parameterized queries.",
        "fix_suggestion": "Use parameterized queries: `cursor.execute('SELECT * FROM t WHERE x = %s', (val,))`",
    },
    "assert_in_production": {
        "regex": r"\bassert\s+",
        "severity": BugSeverity.LOW,
        "category": BugCategory.CONVENTION,
        "message": "Assert statements are removed when Python is run with -O flag.",
        "fix_suggestion": "Use proper error handling with `if/raise` instead of `assert` for validation.",
    },
    "unnecessary_pass": {
        "regex": r"except.*:\s*\n\s+pass",
        "severity": BugSeverity.INFO,
        "category": BugCategory.CONVENTION,
        "message": "Silently passing exceptions hides errors. Log or handle the exception.",
        "fix_suggestion": "Log the exception: `except Exception: logger.exception(...)`",
    },
}


@dataclass
class DetectedBug:
    bug_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    category: BugCategory = BugCategory.LOGIC_ERROR
    severity: BugSeverity = BugSeverity.MEDIUM
    message: str = ""
    line_number: int = 0
    column: int = 0
    snippet: str = ""
    confidence: float = 0.8
    fix_suggestion: Optional[str] = None
    source: str = "pattern"
    file_path: Optional[str] = None
    tool_name: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "bug_id": self.bug_id,
            "category": self.category.value,
            "severity": self.severity.value,
            "message": self.message,
            "line_number": self.line_number,
            "column": self.column,
            "snippet": self.snippet[:300],
            "confidence": self.confidence,
            "fix_suggestion": self.fix_suggestion[:500] if self.fix_suggestion else None,
            "source": self.source,
            "tool_name": self.tool_name,
        }


class BugDetector:
    def __init__(self) -> None:
        self._patterns = BUG_PATTERNS
        self._false_positive_cache: dict[str, set[str]] = {}

    def detect_bugs(
        self,
        code: str,
        file_path: Optional[str] = None,
        enable_static_analysis: bool = True,
        min_confidence: float = 0.3,
    ) -> list[DetectedBug]:
        all_bugs: list[DetectedBug] = []

        pattern_bugs = self._detect_pattern_bugs(code, file_path)
        all_bugs.extend(pattern_bugs)

        if enable_static_analysis:
            static_bugs = self._run_static_analysis(code, file_path)
            all_bugs.extend(static_bugs)

        ast_bugs = self._detect_ast_bugs(code, file_path)
        all_bugs.extend(ast_bugs)

        all_bugs = self._reduce_false_positives(all_bugs)
        all_bugs = [b for b in all_bugs if b.confidence >= min_confidence]

        all_bugs.sort(
            key=lambda b: (
                BugSeverity.CRITICAL.value if b.severity == BugSeverity.CRITICAL
                else BugSeverity.HIGH.value if b.severity == BugSeverity.HIGH
                else BugSeverity.MEDIUM.value if b.severity == BugSeverity.MEDIUM
                else BugSeverity.LOW.value if b.severity == BugSeverity.LOW
                else BugSeverity.INFO.value
            )
        )

        return all_bugs

    def _detect_pattern_bugs(
        self, code: str, file_path: Optional[str] = None
    ) -> list[DetectedBug]:
        bugs: list[DetectedBug] = []

        for pattern_name, pattern_info in self._patterns.items():
            try:
                for match in re.finditer(pattern_info["regex"], code, re.MULTILINE):
                    start_pos = match.start()
                    line_number = code[:start_pos].count("\n") + 1
                    lines = code.split("\n")
                    start_line = max(0, line_number - 2)
                    end_line = min(len(lines), line_number + 2)
                    snippet = "\n".join(lines[start_line:end_line])

                    confidence = self._calculate_confidence(pattern_name, match)

                    if file_path:
                        cache_key = f"{file_path}:{pattern_name}"
                        self._false_positive_cache.setdefault(cache_key, set())

                    bugs.append(
                        DetectedBug(
                            category=pattern_info["category"],
                            severity=pattern_info["severity"],
                            message=pattern_info["message"],
                            line_number=line_number,
                            snippet=snippet,
                            confidence=confidence,
                            fix_suggestion=pattern_info.get("fix_suggestion"),
                            source="pattern",
                            file_path=file_path,
                            tool_name=f"pattern:{pattern_name}",
                        )
                    )
            except re.error as exc:
                logger.warning("Invalid regex pattern '%s': %s", pattern_name, exc)

        return bugs

    def _calculate_confidence(self, pattern_name: str, match: re.Match) -> float:
        base_confidence: dict[str, float] = {
            "hardcoded_password": 0.95,
            "sql_injection": 0.90,
            "bare_except": 0.85,
            "mutable_default_arg": 0.90,
            "division_by_zero": 0.50,
            "comparison_with_self": 0.80,
            "assert_in_production": 0.75,
            "print_statement": 0.70,
            "unnecessary_pass": 0.85,
        }

        confidence = base_confidence.get(pattern_name, 0.65)

        matched_text = match.group()
        if len(matched_text) > 200:
            confidence *= 0.9

        return round(confidence, 3)

    def _detect_ast_bugs(
        self, code: str, file_path: Optional[str] = None
    ) -> list[DetectedBug]:
        bugs: list[DetectedBug] = []
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
                    if isinstance(node.right, ast.Constant) and node.right.value == 0:
                        bugs.append(
                            DetectedBug(
                                category=BugCategory.DIVISION_BY_ZERO,
                                severity=BugSeverity.CRITICAL,
                                message="Explicit division by zero detected.",
                                line_number=getattr(node, "lineno", 0),
                                confidence=1.0,
                                fix_suggestion="Remove or guard the division by zero.",
                                source="ast",
                                file_path=file_path,
                            )
                        )

                elif isinstance(node, ast.FunctionDef):
                    default_mutable = False
                    for default in node.args.defaults:
                        if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                            default_mutable = True
                            break
                    if default_mutable:
                        bugs.append(
                            DetectedBug(
                                category=BugCategory.LOGIC_ERROR,
                                severity=BugSeverity.HIGH,
                                message=f"Function '{node.name}' has mutable default arguments.",
                                line_number=getattr(node, "lineno", 0),
                                confidence=0.95,
                                fix_suggestion="Use None as default and create the mutable inside the function.",
                                source="ast",
                                file_path=file_path,
                                tool_name="ast:mutable_default",
                            )
                        )

                elif isinstance(node, ast.Raise):
                    if isinstance(node.cause, ast.Call) and isinstance(node.cause.func, ast.Name) and node.cause.func.id == "Exception":
                        pass

            for node in ast.walk(tree):
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                    if len(node.id) == 1 and node.id.isalpha() and node.id not in ("i", "j", "k"):
                        pass

        except SyntaxError:
            logger.debug("AST analysis skipped due to syntax errors")
        return bugs

    def _run_static_analysis(
        self, code: str, file_path: Optional[str] = None
    ) -> list[DetectedBug]:
        bugs: list[DetectedBug] = []
        tools_to_try = [
            ("pylint", ["--from-stdin", "input.py"]),
        ]

        for tool_name, args in tools_to_try:
            try:
                proc = subprocess.run(  # nosec
                    ["python", "-m", tool_name, *args],
                    input=code,
                    capture_output=True,
                    text=True,
                    timeout=30.0,
                )
                output = proc.stderr if proc.stderr else proc.stdout
                for line in output.split("\n"):
                    parsed = self._parse_linter_output(line, tool_name, file_path)
                    if parsed:
                        bugs.append(parsed)
            except (FileNotFoundError, subprocess.TimeoutExpired, OSError) as exc:
                logger.debug("Static analysis tool '%s' unavailable: %s", tool_name, exc)

        return bugs

    def _parse_linter_output(
        self, line: str, tool_name: str, file_path: Optional[str] = None
    ) -> Optional[DetectedBug]:
        if not line.strip() or "---" in line:
            return None

        pylint_pattern = r"^(.+?):(\d+):(\d+):\s*(\w+):\s*(.+)$"
        match = re.match(pylint_pattern, line)
        if match:
            _, line_str, col_str, msg_type, message = match.groups()
            severity_map = {
                "error": BugSeverity.HIGH,
                "warning": BugSeverity.MEDIUM,
                "convention": BugSeverity.LOW,
                "info": BugSeverity.INFO,
                "refactor": BugSeverity.INFO,
                "fatal": BugSeverity.CRITICAL,
            }
            category_map = {
                "error": BugCategory.LOGIC_ERROR,
                "warning": BugCategory.CONVENTION,
                "convention": BugCategory.CONVENTION,
                "refactor": BugCategory.REFACTOR_SUGGESTION,
            }
            return DetectedBug(
                category=category_map.get(msg_type.lower(), BugCategory.LOGIC_ERROR),
                severity=severity_map.get(msg_type.lower(), BugSeverity.MEDIUM),
                message=message.strip(),
                line_number=int(line_str),
                column=int(col_str),
                confidence=0.7,
                source="static_analysis",
                file_path=file_path,
                tool_name=f"{tool_name}:{msg_type}",
            )

        return None

    def _reduce_false_positives(self, bugs: list[DetectedBug]) -> list[DetectedBug]:
        deduped: dict[str, DetectedBug] = {}
        for bug in bugs:
            key = f"{bug.line_number}:{bug.category.value}:{bug.message[:80]}"
            if key in deduped:
                existing = deduped[key]
                existing.confidence = max(existing.confidence, bug.confidence)
                if existing.severity != bug.severity:
                    severity_order = [BugSeverity.CRITICAL, BugSeverity.HIGH, BugSeverity.MEDIUM, BugSeverity.LOW, BugSeverity.INFO]
                    existing.severity = min(
                        [existing.severity, bug.severity],
                        key=lambda s: severity_order.index(s),
                    )
            else:
                deduped[key] = bug

        filtered: list[DetectedBug] = []
        for bug in deduped.values():
            cache_key = f"{bug.file_path}:{bug.tool_name}" if bug.file_path and bug.tool_name else ""
            if cache_key and bug.bug_id in self._false_positive_cache.get(cache_key, set()):
                continue
            filtered.append(bug)

        return filtered

    def classify_severity(self, bug: DetectedBug) -> BugSeverity:
        return bug.severity

    def suggest_fix(self, bug: DetectedBug, code: str) -> Optional[str]:
        if bug.fix_suggestion:
            return bug.fix_suggestion

        if bug.category == BugCategory.DIVISION_BY_ZERO:
            return "Add a guard: `if denominator != 0: result = numerator / denominator`"
        elif bug.category == BugCategory.NULL_POINTER:
            return "Add a None check before accessing the variable."
        elif bug.category == BugCategory.INDEX_ERROR:
            return "Check the list length before accessing the index."
        elif bug.category == BugCategory.RESOURCE_LEAK:
            return "Use a context manager (`with` statement) to ensure proper cleanup."

        return None

    def mark_false_positive(
        self, bug_id: str, file_path: str, tool_name: str
    ) -> None:
        cache_key = f"{file_path}:{tool_name}"
        self._false_positive_cache.setdefault(cache_key, set()).add(bug_id)
        logger.info("Marked bug %s as false positive", bug_id)

    def get_bug_summary(self, bugs: list[DetectedBug]) -> dict[str, Any]:
        severity_counts: dict[str, int] = {}
        category_counts: dict[str, int] = {}
        for bug in bugs:
            severity_counts[bug.severity.value] = severity_counts.get(bug.severity.value, 0) + 1
            category_counts[bug.category.value] = category_counts.get(bug.category.value, 0) + 1

        return {
            "total_bugs": len(bugs),
            "by_severity": severity_counts,
            "by_category": category_counts,
            "critical_count": severity_counts.get(BugSeverity.CRITICAL.value, 0),
            "high_count": severity_counts.get(BugSeverity.HIGH.value, 0),
            "medium_count": severity_counts.get(BugSeverity.MEDIUM.value, 0),
            "low_count": severity_counts.get(BugSeverity.LOW.value, 0),
            "average_confidence": round(
                sum(b.confidence for b in bugs) / max(len(bugs), 1), 3
            ),
        }
