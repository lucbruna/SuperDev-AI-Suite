"""Filesystem scanner — deterministic walk of the repository.

Produces a sorted list of :class:`FileInfo` records (relative path, category,
size, mtime) for every indexable file. Honors the ignore lists, hidden-file
policy and the max-file safety caps from :class:`ScannerConfig`.

The ``language`` field doubles as the dispatch category: regular languages
come from the extension map, while named files (Dockerfile, git metadata,
plugin/workflow descriptors, SQL schemas) receive dedicated categories that
:mod:`.project_scanner` routes to their content scanners.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from modules.ai_code_knowledge_graph.config.constants import LANGUAGE_EXTENSIONS
from modules.ai_code_knowledge_graph.config.scanner_config import ScannerConfig

# Named files whose category is decided by name rather than extension.
_NAMED_FILES: dict[str, str] = {
    "dockerfile": "docker",
    ".gitignore": "git",
    ".gitattributes": "git",
    ".gitmodules": "git",
    ".gitconfig": "git",
    ".mailmap": "git",
    "schema.prisma": "database",
}

# Filenames treated as plugin descriptors wherever they appear.
_PLUGIN_FILES: frozenset[str] = frozenset({"plugin.json", "plugin.yaml", "plugin.yml"})

# Extension-map languages that map to a content scanner under another name.
_CATEGORY_ALIASES: dict[str, str] = {
    "sql": "database",
}


@dataclass(slots=True)
class FileInfo:
    rel_path: str
    language: str
    size: int
    mtime: float


def _is_ignored_dir(name: str, ignore_dirs: frozenset[str]) -> bool:
    return name in ignore_dirs


def _is_workflow(rel_path: str) -> bool:
    return "workflows" in Path(rel_path).parts


def _hidden_allowed(name: str, rel_path: str) -> bool:
    return name in _NAMED_FILES or ".github" in Path(rel_path).parts


def _language_for(filename: str, rel_path: str, extensions: dict[str, str]) -> str:
    lower = filename.lower()
    named = _NAMED_FILES.get(lower)
    if named:
        return named
    if lower in _PLUGIN_FILES:
        return "plugin"
    if _is_workflow(rel_path):
        return "workflow"
    language = extensions.get(Path(lower).suffix, "")
    return _CATEGORY_ALIASES.get(language, language)


def scan_files(config: ScannerConfig) -> list[FileInfo]:
    """Walk every configured scan directory under the project root."""
    extensions = config.language_extensions or LANGUAGE_EXTENSIONS
    root = Path(config.project_root)
    results: list[FileInfo] = []
    seen: set[str] = set()

    def walk(base: Path, recurse: bool = True) -> None:
        if len(results) >= config.max_files:
            return
        try:
            entries = sorted(base.iterdir(), key=lambda p: p.name.lower())
        except OSError:
            return
        for entry in entries:
            if len(results) >= config.max_files:
                return
            name = entry.name
            if entry.is_dir():
                if not recurse:
                    continue
                if _is_ignored_dir(name, config.ignore_dirs):
                    continue
                if not config.follow_symlinks and entry.is_symlink():
                    continue
                walk(entry)
                continue
            if not entry.is_file():
                continue
            if name in config.ignore_files or any(
                name.endswith(pattern[1:]) for pattern in config.ignore_files if pattern.startswith("*")
            ):
                continue
            try:
                stat = entry.stat()
            except OSError:
                continue
            if stat.st_size > config.max_file_size:
                continue
            rel = entry.relative_to(root).as_posix()
            if name.startswith(".") and not config.include_hidden and not _hidden_allowed(name, rel):
                continue
            language = _language_for(name, rel, extensions)
            if not language:
                continue
            if rel in seen:
                continue
            seen.add(rel)
            results.append(FileInfo(rel_path=rel, language=language, size=stat.st_size, mtime=stat.st_mtime))

    for dir_name in config.scan_dirs:
        walk(root / dir_name)
    # Root-level files (Dockerfile, .gitignore, README, package.json, ...) are
    # part of the project identity and scanned non-recursively.
    walk(root, recurse=False)
    return results


def language_for_file(rel_path: str, extensions: dict[str, str] | None = None) -> str:
    """Return the dispatch category for a relative path (no filesystem access)."""
    ext_map = extensions or LANGUAGE_EXTENSIONS
    path = Path(rel_path)
    return _language_for(path.name, rel_path, ext_map)
