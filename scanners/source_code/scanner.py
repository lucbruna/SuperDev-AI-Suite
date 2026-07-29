"""Source Code Scanner — analyzes source code for patterns, issues, and best practices."""

from __future__ import annotations

import ast
import os
import re
import time
from typing import Any

from ..base import BaseScanner, Finding, FindingType, ScanResult, Severity


class SourceCodeScanner(BaseScanner):
    name = "source_code"
    description = "Analyzes source code for bugs, security issues, and best practices via AST"

    # Pattern definitions for text-based analysis
    PATTERNS: list[dict[str, Any]] = [
        {
            "rule_id": "SC-SEC-001",
            "title": "Hardcoded password detected",
            "pattern": r'(?:password|passwd|pwd|secret)\s*[=:]\s*["\'](?!.*\{|getenv|\$|os\.)',
            "severity": Severity.HIGH,
            "type": FindingType.SECURITY,
            "extensions": [".py", ".js", ".ts", ".jsx", ".tsx", ".env", ".yaml", ".yml", ".json"],
        },
        {
            "rule_id": "SC-SEC-002",
            "title": "Hardcoded API key/token",
            "pattern": r'(?:api_key|apikey|token|access_key|secret_key)\s*[=:]\s*["\'][A-Za-z0-9_\-]{16,}',
            "severity": Severity.HIGH,
            "type": FindingType.SECURITY,
            "extensions": [".py", ".js", ".ts", ".yaml", ".yml"],
        },
        {
            "rule_id": "SC-SEC-003",
            "title": "eval() or exec() usage",
            "pattern": r'\b(?:eval|exec)\s*\(',
            "severity": Severity.HIGH,
            "type": FindingType.VULNERABILITY,
            "extensions": [".py", ".js"],
        },
        {
            "rule_id": "SC-SEC-004",
            "title": "SQL injection risk",
            "pattern": r'(?:execute|query|raw_query)\s*\(\s*["\'](?!.*%(?:s|d|f))',
            "severity": Severity.CRITICAL,
            "type": FindingType.VULNERABILITY,
            "extensions": [".py", ".js", ".ts"],
        },
        {
            "rule_id": "SC-SEC-005",
            "title": "Debug endpoint in production",
            "pattern": r'@app\.(?:route|get|post|put|delete)\([\s\S]{0,50}(?:debug|test|admin)',
            "severity": Severity.MEDIUM,
            "type": FindingType.SECURITY,
            "extensions": [".py"],
        },
        {
            "rule_id": "SC-BP-001",
            "title": "Too many arguments in function",
            "pattern": r'',
            "severity": Severity.LOW,
            "type": FindingType.BEST_PRACTICE,
            "extensions": [".py"],
            "ast_check": "too_many_args",
        },
        {
            "rule_id": "SC-BP-002",
            "title": "Too complex function (cyclomatic complexity)",
            "pattern": r'',
            "severity": Severity.MEDIUM,
            "type": FindingType.COMPLEXITY,
            "extensions": [".py"],
            "ast_check": "too_complex",
        },
        {
            "rule_id": "SC-BP-003",
            "title": "Try-except without specific exception",
            "pattern": r'except\s*:',
            "severity": Severity.MEDIUM,
            "type": FindingType.BEST_PRACTICE,
            "extensions": [".py"],
        },
        {
            "rule_id": "SC-BP-004",
            "title": "Wildcard import detected",
            "pattern": r'from\s+\S+\s+import\s+\*',
            "severity": Severity.LOW,
            "type": FindingType.BEST_PRACTICE,
            "extensions": [".py"],
        },
        {
            "rule_id": "SC-BP-005",
            "title": "Debug print statement",
            "pattern": r'(?:print|console\.log)\s*\(',
            "severity": Severity.LOW,
            "type": FindingType.BEST_PRACTICE,
            "extensions": [".py", ".js", ".ts", ".jsx", ".tsx"],
        },
        {
            "rule_id": "SC-SEC-006",
            "title": "Insecure hash function",
            "pattern": r'(?:md5|sha1)\s*\(',
            "severity": Severity.MEDIUM,
            "type": FindingType.VULNERABILITY,
            "extensions": [".py", ".js", ".ts"],
        },
        {
            "rule_id": "SC-SEC-007",
            "title": "Potential path traversal",
            "pattern": r'(?:open|read_text|write_text)\s*\([\s\S]{0,30}\.\./',
            "severity": Severity.HIGH,
            "type": FindingType.VULNERABILITY,
            "extensions": [".py"],
        },
        {
            "rule_id": "SC-SEC-008",
            "title": "assert usage in non-test code",
            "pattern": r'\bassert\s+',
            "severity": Severity.LOW,
            "type": FindingType.BEST_PRACTICE,
            "extensions": [".py"],
            "exclude_pattern": r'(?:test_|conftest)\.py$',
        },
    ]

    MAX_FUNCTION_ARGS = 6
    MAX_COMPLEXITY = 15

    IGNORE_DIRS = {
        ".git", "__pycache__", "node_modules", ".next", ".venv",
        "venv", ".tox", ".egg-info", "dist", "build",
        ".mypy_cache", ".pytest_cache", ".ruff_cache",
    }

    async def scan(self, target: str) -> ScanResult:
        start = time.time()
        all_findings: list[Finding] = []

        if os.path.isfile(target):
            findings = await self._scan_file(target)
            all_findings.extend(findings)
        elif os.path.isdir(target):
            for root, dirs, files in os.walk(target):
                dirs[:] = [d for d in dirs if d not in self.IGNORE_DIRS]
                for fname in files:
                    file_path = os.path.join(root, fname)
                    findings = await self._scan_file(file_path)
                    all_findings.extend(findings)
        else:
            return ScanResult(
                scanner_name=self.name,
                target=target,
                error=f"Invalid target: {target}",
            )

        elapsed_ms = round((time.time() - start) * 1000, 2)
        return ScanResult(
            scanner_name=self.name,
            target=target,
            total_findings=len(all_findings),
            findings=all_findings,
            scan_duration_ms=elapsed_ms,
            timestamp=__import__("datetime").datetime.now().isoformat(),
        )

    async def _scan_file(self, file_path: str) -> list[Finding]:
        findings: list[Finding] = []
        ext = os.path.splitext(file_path)[1].lower()

        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception:
            return findings

        lines = content.split("\n")

        # Pattern-based analysis
        for pattern_def in self.PATTERNS:
            if ext not in pattern_def["extensions"]:
                continue

            # Check exclusion pattern
            excl = pattern_def.get("exclude_pattern", "")
            if excl and re.search(excl, file_path):
                continue

            # AST-based checks (Python only)
            if pattern_def.get("ast_check") and ext == ".py":
                ast_findings = self._check_ast(content, file_path, pattern_def)
                findings.extend(ast_findings)
                continue

            # Regex pattern check
            if not pattern_def["pattern"]:
                continue

            for line_no, line in enumerate(lines, 1):
                matches = re.finditer(pattern_def["pattern"], line)
                for match in matches:
                    snippet_start = max(0, match.start() - 20)
                    snippet_end = min(len(line), match.end() + 20)
                    snippet = line[snippet_start:snippet_end].strip()
                    findings.append(Finding(
                        rule_id=pattern_def["rule_id"],
                        title=pattern_def["title"],
                        description=f"Found in {os.path.basename(file_path)}",
                        severity=pattern_def["severity"],
                        file_path=file_path,
                        line=line_no,
                        column=max(1, match.start()),
                        snippet=snippet,
                        recommendation=self._get_recommendation(pattern_def["rule_id"]),
                        type=pattern_def["type"],
                    ))

        return findings

    def _check_ast(self, content: str, file_path: str, pattern_def: dict) -> list[Finding]:
        findings: list[Finding] = []
        try:
            tree = ast.parse(content, filename=file_path)
        except SyntaxError:
            return findings

        for node in ast.walk(tree):
            if pattern_def["ast_check"] == "too_many_args" and isinstance(node, ast.FunctionDef):
                args = [a for a in node.args.args if a.arg != "self"]
                if len(args) > self.MAX_FUNCTION_ARGS and not node.name.startswith("__"):
                    findings.append(Finding(
                        rule_id=pattern_def["rule_id"],
                        title=f"Function '{node.name}' has too many arguments ({len(args)})",
                        description=f"Function has {len(args)} parameters (max: {self.MAX_FUNCTION_ARGS})",
                        severity=pattern_def["severity"],
                        file_path=file_path,
                        line=node.lineno or 0,
                        recommendation="Consider using *args, **kwargs, or a dataclass/config object",
                        type=pattern_def["type"],
                    ))

            if pattern_def["ast_check"] == "too_complex" and isinstance(node, ast.FunctionDef):
                complexity = self._calculate_complexity(node)
                if complexity > self.MAX_COMPLEXITY:
                    findings.append(Finding(
                        rule_id=pattern_def["rule_id"],
                        title=f"Function '{node.name}' has high cyclomatic complexity ({complexity})",
                        description=f"Complexity score: {complexity} (max: {self.MAX_COMPLEXITY})",
                        severity=pattern_def["severity"],
                        file_path=file_path,
                        line=node.lineno or 0,
                        recommendation="Refactor into smaller functions",
                        type=pattern_def["type"],
                    ))

        return findings

    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity for a function."""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.Try):
                complexity += len(child.handlers)
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            elif isinstance(child, ast.Assert):
                complexity += 1
        return complexity

    def _get_recommendation(self, rule_id: str) -> str:
        recommendations = {
            "SC-SEC-001": "Use environment variables or a secrets manager. Never hardcode passwords.",
            "SC-SEC-002": "Use environment variables or a secrets vault for API keys.",
            "SC-SEC-003": "Avoid eval/exec. Use safer alternatives like ast.literal_eval().",
            "SC-SEC-004": "Use parameterized queries or an ORM to prevent SQL injection.",
            "SC-SEC-005": "Remove debug endpoints before production deployment.",
            "SC-BP-001": "Reduce the number of function arguments.",
            "SC-BP-002": "Split complex functions into smaller, focused functions.",
            "SC-BP-003": "Always catch specific exceptions instead of bare except.",
            "SC-BP-004": "Import only what you need: 'from module import specific_name'.",
            "SC-BP-005": "Remove debug print statements or use a proper logger.",
            "SC-SEC-006": "Use SHA-256 or bcrypt instead of MD5/SHA1.",
            "SC-SEC-007": "Use path sanitization to prevent directory traversal.",
            "SC-SEC-008": "Remove assert statements from production code.",
        }
        return recommendations.get(rule_id, "Review the code and apply best practices.")
