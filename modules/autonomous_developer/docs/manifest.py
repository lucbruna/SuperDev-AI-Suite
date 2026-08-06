"""Deterministic module documentation manifest."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

__all__ = ["DocsManifest", "ModuleDocs"]


@dataclass(slots=True)
class ModuleDocs:
    """Documentation entry for one package inside the module."""

    package: str
    module_count: int


class DocsManifest:
    """Scans a module root and renders a deterministic package index."""

    def scan(self, module_root: str | Path) -> list[ModuleDocs]:
        """List packages (dirs with __init__.py), sorted, with .py counts."""
        root = Path(module_root)
        entries: list[ModuleDocs] = []
        if not root.is_dir():
            return entries
        for child in sorted(root.iterdir()):
            if not child.is_dir() or not (child / "__init__.py").exists():
                continue
            module_count = sum(
                1
                for item in child.iterdir()
                if item.is_file()
                and item.suffix == ".py"
                and item.name != "__init__.py"
            )
            entries.append(ModuleDocs(package=child.name, module_count=module_count))
        return entries

    def render_index(self, module_root: str | Path) -> str:
        """Render the package index as deterministic markdown."""
        entries = self.scan(module_root)
        lines = ["# Autonomous Developer Module", ""]
        if not entries:
            lines.append("_no packages_")
        else:
            lines.extend(
                f"- `{entry.package}`: {entry.module_count} module(s)"
                for entry in entries
            )
        return "\n".join(lines) + "\n"
