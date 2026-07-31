from __future__ import annotations

import logging
from typing import Any

from ..parsing.ast_manager import ASTManager

#: Per-kind weights used by :meth:`SymbolIndex.rank` to score how strongly a
#: symbol signals relevance: a file defining a *class* is more relevant to a
#: query than one that merely imports the name.
RELEVANCE_WEIGHTS = {"class": 3, "function": 2, "import": 1}


class SymbolIndex:
    """Indexes symbols (classes, functions, imports) across the codebase.

    Populated from :class:`ASTManager` parse results: each symbol maps to one
    or more locations ``{"kind", "path"}``. ``search`` is the plain
    substring lookup; ``rank`` adds relevance ordering (used by code
    navigation and prompt-context selection).
    """

    def __init__(self, ast_manager: ASTManager | None = None) -> None:
        self._symbols: dict[str, list[dict[str, Any]]] = {}
        self._ast = ast_manager or ASTManager()
        self._log = logging.getLogger("superdev.code.understanding.symbols")

    # -- core API (kept from the original stub) --------------------------

    def add(self, name: str, location: dict[str, Any]) -> None:
        """Register a symbol location (deduplicated per path/kind)."""
        locations = self._symbols.setdefault(name, [])
        if location not in locations:
            locations.append(location)

    def find(self, name: str) -> list[dict[str, Any]]:
        """Locations where *name* is defined/imported."""
        return self._symbols.get(name, [])

    # -- population from AST ---------------------------------------------

    def index_parsed(self, path: str, parsed: dict[str, Any]) -> SymbolIndex:
        """Index classes, functions and imports from an ASTManager result."""
        for cls in parsed.get("classes", []):
            self.add(cls, {"kind": "class", "path": path})
        for fn in parsed.get("functions", []):
            self.add(fn, {"kind": "function", "path": path})
        for imp in parsed.get("imports", []):
            self.add(imp["module"], {"kind": "import", "path": path})
        return self

    def index_file(self, path: str, content: str) -> bool:
        """Parse a single file and index its symbols. Returns False on
        syntax error (the file is skipped)."""
        parsed = self._ast.parse(content or "")
        if parsed is None:
            return False
        self.index_parsed(path, parsed)
        return True

    def index_files(self, files: list[Any]) -> int:
        """Index *files* (``CodeFile`` objects or dicts with ``path``/
        ``content``). Returns the number of files parsed successfully."""
        parsed_count = 0
        for file in files:
            if isinstance(file, dict):
                content = file.get("content", "")
                path = file.get("path", "")
            else:
                content = getattr(file, "content", "")
                path = getattr(file, "path", "")
            if self.index_file(path, content):
                parsed_count += 1
        return parsed_count

    # -- queries ----------------------------------------------------------

    def search(self, query: str) -> list[tuple[str, list[dict[str, Any]]]]:
        """Case-insensitive substring search over symbol names."""
        needle = query.lower()
        return [(name, list(locations))
                for name, locations in self._symbols.items()
                if needle in name.lower()]

    def rank(self, query: str) -> list[dict[str, Any]]:
        """Symbols matching *query*, sorted by descending relevance.

        Each symbol's ``relevance`` is the sum of
        :data:`RELEVANCE_WEIGHTS` across its indexed locations (so a
        class defined in two files outranks one imported once). Returns
        ``[{"name", "locations", "relevance"}]``; a blank *query*
        matches every symbol (relevance still scored). Sorting is stable,
        so symbols with equal relevance keep insertion order.
        """
        needle = query.lower()
        matches = []
        for name, locations in self._symbols.items():
            if needle not in name.lower():
                continue
            relevance = sum(
                RELEVANCE_WEIGHTS.get(loc.get("kind", ""), 1)
                for loc in locations
            )
            matches.append({
                "name": name,
                "locations": list(locations),
                "relevance": relevance,
            })
        matches.sort(key=lambda m: m["relevance"], reverse=True)
        return matches

    def symbols(self) -> list[str]:
        """All indexed symbol names."""
        return list(self._symbols)

    def files(self) -> list[str]:
        """All files that contributed symbols (sorted)."""
        return sorted({loc["path"]
                       for locations in self._symbols.values()
                       for loc in locations})

    def count(self) -> int:
        """Total number of indexed symbol locations."""
        return sum(len(locations) for locations in self._symbols.values())

    def to_dict(self) -> dict[str, list[dict[str, Any]]]:
        """Serializable ``symbol -> [locations]`` mapping."""
        return {name: list(locations)
                for name, locations in self._symbols.items()}
