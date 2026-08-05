from __future__ import annotations

import ast
import difflib
import logging
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger("superdev.ai.refactoring")


class SmellSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class RefactoringType(str, Enum):
    EXTRACT_METHOD = "extract_method"
    RENAME_VARIABLE = "rename_variable"
    SIMPLIFY_CONDITIONAL = "simplify_conditional"
    DECOMPOSE_CONDITIONAL = "decompose_conditional"
    REPLACE_TEMP_WITH_QUERY = "replace_temp_with_query"
    INTRODUCE_PARAMETER_OBJECT = "introduce_parameter_object"
    REPLACE_METHOD_WITH_METHOD_OBJECT = "replace_method_with_method_object"
    EXTRACT_CLASS = "extract_class"
    PULL_UP_FIELD = "pull_up_field"
    PUSH_DOWN_FIELD = "push_down_field"
    REPLACE_INHERITANCE_WITH_DELEGATION = "replace_inheritance_with_delegation"
    REPLACE_DELEGATION_WITH_INHERITANCE = "replace_delegation_with_inheritance"


SMELL_PATTERNS: dict[str, dict[str, Any]] = {
    "long_method": {
        "regex": r"def .+\):\n(?:.+\n){20,}",
        "severity": SmellSeverity.WARNING,
        "message": "Method is too long (>20 lines). Consider extracting smaller methods.",
        "refactoring": RefactoringType.EXTRACT_METHOD,
    },
    "too_many_params": {
        "regex": r"def \w+\([^)]{1,5}(?:,\s*\w+\s*(?::\s*\w+)?\s*){5,}\)",
        "severity": SmellSeverity.WARNING,
        "message": "Method has too many parameters. Consider using a parameter object.",
        "refactoring": RefactoringType.INTRODUCE_PARAMETER_OBJECT,
    },
    "temp_variable": {
        "regex": r"(\w+)\s*=\s*.*\(.*\)\s*\n.*\1",
        "severity": SmellSeverity.INFO,
        "message": "Temporary variable that could be replaced with a query method.",
        "refactoring": RefactoringType.REPLACE_TEMP_WITH_QUERY,
    },
    "nested_conditionals": {
        "regex": r"if .+:\n\s+if .+:",
        "severity": SmellSeverity.WARNING,
        "message": "Nested conditionals detected. Consider decomposing or simplifying.",
        "refactoring": RefactoringType.DECOMPOSE_CONDITIONAL,
    },
    "magic_number": {
        "regex": r"(?<!= )\b\d{4,}\b(?!\s*=)",
        "severity": SmellSeverity.INFO,
        "message": "Magic number detected. Extract to a named constant.",
        "refactoring": None,
    },
    "large_class": {
        "regex": r"class \w+:\n(?:.+\n){30,}",
        "severity": SmellSeverity.WARNING,
        "message": "Class is too large (>30 lines). Consider extracting a new class.",
        "refactoring": RefactoringType.EXTRACT_CLASS,
    },
    "duplicate_code": {
        "regex": r"(\n {4}.+\n)(?=.*\1)",
        "severity": SmellSeverity.WARNING,
        "message": "Duplicate code block detected. Consider extracting a method.",
        "refactoring": RefactoringType.EXTRACT_METHOD,
    },
    "single_letter_var": {
        "regex": r"\b([a-z])\s*=\s*(?![\"'`'\"])",
        "severity": SmellSeverity.INFO,
        "message": "Single-letter variable name detected. Use descriptive names.",
        "refactoring": RefactoringType.RENAME_VARIABLE,
    },
}


@dataclass
class CodeSmell:
    type: str
    message: str
    severity: SmellSeverity
    line_number: int
    column: int = 0
    snippet: str = ""
    refactoring_type: Optional[RefactoringType] = None
    suggested_fix: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "message": self.message,
            "severity": self.severity.value,
            "line_number": self.line_number,
            "column": self.column,
            "snippet": self.snippet[:200],
            "refactoring_type": self.refactoring_type.value if self.refactoring_type else None,
            "suggested_fix": self.suggested_fix[:500] if self.suggested_fix else None,
        }


@dataclass
class RefactoringSuggestion:
    smell: CodeSmell
    refactoring_type: RefactoringType
    description: str
    original_code: str = ""
    refactored_code: str = ""
    applies_to: list[str] = field(default_factory=list)
    complexity: int = 1
    confidence: float = 0.8

    def to_dict(self) -> dict[str, Any]:
        return {
            "refactoring_type": self.refactoring_type.value,
            "description": self.description,
            "original_code": self.original_code[:500],
            "refactored_code": self.refactored_code[:500],
            "complexity": self.complexity,
            "confidence": self.confidence,
            "smell": self.smell.to_dict(),
        }


@dataclass
class RefactoringResult:
    success: bool
    original_code: str = ""
    refactored_code: str = ""
    suggestions: list[RefactoringSuggestion] = field(default_factory=list)
    applied_refactorings: list[RefactoringSuggestion] = field(default_factory=list)
    diff: str = ""
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    rollback_available: bool = False
    syntax_checked: bool = False


class SafetyCheckError(Exception):
    pass


class RefactoringEngine:
    def __init__(self) -> None:
        self._backup_cache: dict[str, str] = {}
        self._smell_patterns = SMELL_PATTERNS

    def detect_smells(
        self,
        code: str,
        file_path: Optional[str] = None,
    ) -> list[CodeSmell]:
        smells: list[CodeSmell] = []
        lines = code.split("\n")

        for smell_type, pattern_info in self._smell_patterns.items():
            for match in re.finditer(pattern_info["regex"], code, re.MULTILINE):
                matched_text = match.group()
                start_pos = match.start()
                line_number = code[:start_pos].count("\n") + 1

                start_line = max(0, line_number - 2)
                end_line = min(len(lines), line_number + 2)
                snippet = "\n".join(lines[start_line:end_line])

                smells.append(
                    CodeSmell(
                        type=smell_type,
                        message=pattern_info["message"],
                        severity=pattern_info["severity"],
                        line_number=line_number,
                        snippet=snippet,
                        refactoring_type=pattern_info["refactoring"],
                    )
                )

        smells.sort(key=lambda s: (s.severity != SmellSeverity.CRITICAL, s.severity != SmellSeverity.WARNING, s.line_number))
        return smells

    def _detect_ast_smells(self, code: str) -> list[CodeSmell]:
        smells: list[CodeSmell] = []
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if len(node.body) > 20:
                        smells.append(
                            CodeSmell(
                                type="long_function_ast",
                                message=f"Function '{node.name}' has {len(node.body)} statements (limit: 20)",
                                severity=SmellSeverity.WARNING,
                                line_number=node.lineno if hasattr(node, "lineno") else 0,
                                refactoring_type=RefactoringType.EXTRACT_METHOD,
                            )
                        )
                    if len(node.args.args) > 5:
                        smells.append(
                            CodeSmell(
                                type="too_many_params_ast",
                                message=f"Function '{node.name}' has {len(node.args.args)} parameters (limit: 5)",
                                severity=SmellSeverity.WARNING,
                                line_number=node.lineno if hasattr(node, "lineno") else 0,
                                refactoring_type=RefactoringType.INTRODUCE_PARAMETER_OBJECT,
                            )
                        )
                elif isinstance(node, ast.ClassDef):
                    concrete_methods = [n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                    if len(concrete_methods) > 15:
                        smells.append(
                            CodeSmell(
                                type="large_class_ast",
                                message=f"Class '{node.name}' has {len(concrete_methods)} methods (limit: 15)",
                                severity=SmellSeverity.WARNING,
                                line_number=node.lineno if hasattr(node, "lineno") else 0,
                                refactoring_type=RefactoringType.EXTRACT_CLASS,
                            )
                        )
        except SyntaxError:
            pass
        return smells

    def get_suggestions(
        self,
        smells: list[CodeSmell],
        code: str,
    ) -> list[RefactoringSuggestion]:
        suggestions: list[RefactoringSuggestion] = []
        for smell in smells:
            if not smell.refactoring_type:
                continue

            suggestion = RefactoringSuggestion(
                smell=smell,
                refactoring_type=smell.refactoring_type,
                description=self._generate_refactoring_description(smell),
                original_code=smell.snippet,
                confidence=self._calculate_confidence(smell),
            )

            refactored = self._apply_single_refactoring(code, smell)
            if refactored:
                suggestion.refactored_code = refactored

            suggestions.append(suggestion)

        suggestions.sort(key=lambda s: (s.confidence, s.smell.severity != SmellSeverity.CRITICAL), reverse=True)
        return suggestions

    def _generate_refactoring_description(self, smell: CodeSmell) -> str:
        descriptions = {
            RefactoringType.EXTRACT_METHOD: f"Extract the code at line {smell.line_number} into a separate method with a descriptive name.",
            RefactoringType.RENAME_VARIABLE: f"Rename the variable at line {smell.line_number} to be more descriptive.",
            RefactoringType.SIMPLIFY_CONDITIONAL: f"Simplify the conditional at line {smell.line_number} by removing unnecessary nesting.",
            RefactoringType.DECOMPOSE_CONDITIONAL: f"Decompose the conditional at line {smell.line_number} into separate guard clauses.",
            RefactoringType.REPLACE_TEMP_WITH_QUERY: f"Replace the temporary variable at line {smell.line_number} with a query method.",
            RefactoringType.INTRODUCE_PARAMETER_OBJECT: f"Introduce a parameter object to reduce the number of parameters at line {smell.line_number}.",
            RefactoringType.EXTRACT_CLASS: f"Extract a new class from the code around line {smell.line_number}.",
        }
        return descriptions.get(smell.refactoring_type, f"Apply refactoring at line {smell.line_number}.")

    def _calculate_confidence(self, smell: CodeSmell) -> float:
        severity_map = {
            SmellSeverity.CRITICAL: 0.95,
            SmellSeverity.WARNING: 0.80,
            SmellSeverity.INFO: 0.60,
        }
        return severity_map.get(smell.severity, 0.5)

    def _apply_single_refactoring(self, code: str, smell: CodeSmell) -> Optional[str]:
        if not smell.refactoring_type:
            return None

        lines = code.split("\n")
        if smell.line_number < 1 or smell.line_number > len(lines):
            return None

        try:
            if smell.refactoring_type == RefactoringType.RENAME_VARIABLE:
                line = lines[smell.line_number - 1]
                match = re.search(r"\b([a-z])\s*=\s*(?![\"'`])", line)
                if match:
                    old_name = match.group(1)
                    new_name = self._suggest_variable_name(code, old_name)
                    lines[smell.line_number - 1] = line.replace(f"{old_name} =", f"{new_name} =", 1)
                    for i in range(len(lines)):
                        lines[i] = re.sub(rf"\b{old_name}\b(?!\s*=)", new_name, lines[i])
                    return "\n".join(lines)

            elif smell.refactoring_type == RefactoringType.SIMPLIFY_CONDITIONAL:
                code = self._simplify_nested_if(code)

            return "\n".join(lines)
        except Exception:
            return None

    def _suggest_variable_name(self, code: str, old_name: str) -> str:
        context_lines = code.split("\n")
        suggestions = {
            "i": "index", "j": "column", "k": "key",
            "x": "value_x", "y": "value_y", "z": "value_z",
            "s": "string", "n": "count", "c": "character",
            "d": "data", "f": "file", "t": "temp",
            "e": "element", "l": "item_list",
        }
        return suggestions.get(old_name, f"{old_name}_value")

    def _simplify_nested_if(self, code: str) -> str:
        pattern = r"if (.+):\n(\s+)if (.+):\n\s+(.+)(?:\n\s*return .+)?"
        replacement = r"if \1 and \3:\n\2\4"
        return re.sub(pattern, replacement, code)

    async def execute_refactoring(
        self,
        code: str,
        suggestion: RefactoringSuggestion,
        file_path: Optional[str] = None,
    ) -> RefactoringResult:
        backup_key = file_path or uuid.uuid4().hex
        self._backup_cache[backup_key] = code

        result = RefactoringResult(
            success=False,
            original_code=code,
            rollback_available=True,
        )

        safe, error = self._safety_check(code)
        result.syntax_checked = safe
        if not safe:
            result.errors.append(f"Safety check failed: {error}")
            return result

        refactored = self._apply_single_refactoring(code, suggestion.smell)
        if not refactored:
            result.errors.append(f"Could not apply refactoring: {suggestion.refactoring_type.value}")
            return result

        safe2, error2 = self._safety_check(refactored)
        if not safe2:
            result.errors.append(f"Refactored code fails safety check: {error2}")
            result.refactored_code = refactored
            return result

        result.refactored_code = refactored
        result.success = True
        result.applied_refactorings.append(suggestion)
        result.diff = self.generate_diff(code, refactored)

        logger.info(
            "Applied refactoring '%s' at line %d",
            suggestion.refactoring_type.value,
            suggestion.smell.line_number,
        )

        return result

    async def refactor_code(
        self,
        code: str,
        file_path: Optional[str] = None,
        auto_apply: bool = False,
    ) -> RefactoringResult:
        result = RefactoringResult(original_code=code, rollback_available=(file_path is not None))

        smells = self.detect_smells(code)
        ast_smells = self._detect_ast_smells(code)
        smells.extend(ast_smells)

        suggestions = self.get_suggestions(smells, code)
        result.suggestions = suggestions

        if auto_apply:
            for suggestion in suggestions[:3]:
                refactor_result = await self.execute_refactoring(code, suggestion, file_path)
                if refactor_result.success:
                    code = refactor_result.refactored_code
                    result.applied_refactorings.append(suggestion)
                    result.warnings.append(
                        f"Auto-applied: {suggestion.refactoring_type.value}"
                    )
                else:
                    result.errors.extend(refactor_result.errors)

            result.refactored_code = code
            if result.applied_refactorings:
                result.diff = self.generate_diff(result.original_code, code)

        return result

    def _safety_check(self, code: str) -> tuple[bool, str]:
        try:
            ast.parse(code)
            return True, ""
        except SyntaxError as exc:
            return False, str(exc)

    def generate_diff(self, original: str, refactored: str) -> str:
        original_lines = original.splitlines(keepends=True)
        refactored_lines = refactored.splitlines(keepends=True)
        diff = difflib.unified_diff(
            original_lines,
            refactored_lines,
            fromfile="original",
            tofile="refactored",
        )
        return "".join(diff)

    def rollback(self, file_path: str) -> Optional[str]:
        original = self._backup_cache.pop(file_path, None)
        if original:
            logger.info("Rolled back refactoring for %s", file_path)
        return original

    def get_backup(self, file_path: str) -> Optional[str]:
        return self._backup_cache.get(file_path)
