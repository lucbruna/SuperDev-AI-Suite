"""JavaScript / JSX source parser (regex based).

Extracts import statements (ESM + CJS + dynamic) and API path references so
the scanner can map frontend files to backend endpoints.
"""
from __future__ import annotations

import re
from typing import Any

_IMPORT_RE = re.compile(
    r"(?:import\s+(?:type\s+)?(?:\{[\s\S]*?\}|[\w*]+[\s\S]*?)\s+from\s*"
    r"|import\s+(?:type\s+)?['\"])['\"]([^'\"]+)['\"]"
)
_REQUIRE_RE = re.compile(r"require\s*\(\s*['\"]([^'\"]+)['\"]\s*\)")
_DYNAMIC_RE = re.compile(r"import\s*\(\s*['\"]([^'\"]+)['\"]\s*\)")
_API_RE = re.compile(r"['\"](?:/api|/?api/v1)[^'\"]*['\"]")
_MODULE_ALIAS_RE = re.compile(r"@/[\w\-./]+|@\w+[\w\-./]*")


def parse_imports(text: str) -> list[dict[str, Any]]:
    """Extract import statements (module specifiers only)."""
    imports: list[dict[str, Any]] = []
    for match in _IMPORT_RE.finditer(text):
        spec = match.group(1).strip()
        if spec:
            imports.append({"module": spec, "kind": "esm"})
    for match in _REQUIRE_RE.finditer(text):
        imports.append({"module": match.group(1).strip(), "kind": "cjs"})
    for match in _DYNAMIC_RE.finditer(text):
        imports.append({"module": match.group(1).strip(), "kind": "dynamic"})
    return imports


def parse_api_paths(text: str) -> list[str]:
    """Extract API route strings referenced by the file."""
    return list(dict.fromkeys(m.group(0).strip("'\"") for m in _API_RE.finditer(text)))


def parse(text: str, path: str = "") -> dict[str, Any]:
    return {
        "imports": parse_imports(text),
        "api_paths": parse_api_paths(text),
        "uses_module_alias": bool(_MODULE_ALIAS_RE.search(text)),
        "jsx": "</>" in text or "<" in text and "return (" in text,
    }
