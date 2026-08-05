"""Import resolution: maps import specifiers to project-relative file paths.

* Python: dotted module names resolved against the known file set
  (``backend.api.router`` -> ``backend/api/router.py``).
* JS/TS: relative paths (``./x``, ``../x``) and the ``@/`` alias used by the
  Next.js frontend (maps to ``frontend/src/``).
* Unresolvable specifiers (stdlib, site-packages, npm packages) return None
  and are classified as external by the caller.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

_ALIAS_RE = re.compile(r"^@/")


def stdlib_modules() -> frozenset[str]:
    """Top-level standard library module names (py >= 3.10)."""
    try:
        return frozenset(sys.stdlib_module_names)  # type: ignore[attr-defined]
    except AttributeError:
        return frozenset(
            {"os", "sys", "re", "json", "typing", "pathlib", "collections",
             "datetime", "dataclasses", "asyncio", "logging", "abc", "io",
             "math", "random", "time", "uuid", "functools", "itertools"}
        )


def _normalize(rel_path: str) -> str:
    return rel_path.replace("\\", "/")


def python_module_to_path(
    module: str, *, known_files: set[str], level: int = 0
) -> str | None:
    """Resolve a Python import to a repo-relative file path."""
    if not module:
        return None
    top = module.split(".")[0]
    if top in stdlib_modules():
        return None

    relative_parts = module.split(".")
    candidate = "/".join(relative_parts) + ".py"
    if candidate in known_files:
        return candidate
    init_candidate = "/".join(relative_parts) + "/__init__.py"
    if init_candidate in known_files:
        return init_candidate
    # Trim trailing parts to handle imports of submodules that resolve to
    # package directories.
    for i in range(len(relative_parts) - 1, 0, -1):
        prefix = "/".join(relative_parts[:i])
        pkg_init = prefix + "/__init__.py"
        if pkg_init in known_files:
            return pkg_init
    return None


def js_module_to_path(
    spec: str, *, current_rel: str, known_files: set[str], root: str = ""
) -> str | None:
    """Resolve a JS/TS import specifier to a repo-relative file path."""
    if not spec.startswith(("./", "../", "@/")):
        return None  # bare package -> external
    if _ALIAS_RE.match(spec):
        rel = "frontend/src/" + spec[2:]
    else:
        base = Path(current_rel).parent
        rel = (base / spec).as_posix()
    for candidate in (rel + ".ts", rel + ".tsx", rel + ".js", rel + ".jsx", rel + ".json"):
        if candidate in known_files:
            return candidate
    index_candidates = (
        rel + "/index.ts", rel + "/index.tsx", rel + "/index.js", rel + "/index.jsx",
    )
    for candidate in index_candidates:
        if candidate in known_files:
            return candidate
    return None
