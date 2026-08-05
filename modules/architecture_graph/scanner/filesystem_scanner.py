"""Filesystem scanner: walks the project and yields indexable files.

Produces a deterministic list of :class:`FileInfo` records (relative path,
language, size, mtime) which downstream scanners consume. Honors the ignore
lists and the max-file safety caps from the module config.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from modules.architecture_graph.config.graph_config import GraphConfig
from modules.architecture_graph.config.graph_constants import EXTENSION_LANG, SCANNABLE_EXTENSIONS


@dataclass(slots=True)
class FileInfo:
    rel_path: str
    language: str
    size: int
    mtime: float


def _is_ignored_dir(name: str, ignore_dirs: frozenset[str]) -> bool:
    return name in ignore_dirs or (name.startswith(".") and name not in {".github", ".gitignore"})


def _language_for(filename: str) -> str:
    lower = filename.lower()
    if lower == "dockerfile" or lower.endswith(".dockerfile"):
        return "docker"
    suffix = Path(lower).suffix
    return EXTENSION_LANG.get(suffix, "")


def scan_files(config: GraphConfig) -> list[FileInfo]:
    root = Path(config.project_root)
    results: list[FileInfo] = []
    seen: set[str] = set()

    def walk(base: Path) -> None:
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
                if _is_ignored_dir(name, config.ignore_dirs):
                    continue
                if not config.follow_symlinks and entry.is_symlink():
                    continue
                walk(entry)
                continue
            if not entry.is_file():
                continue
            if name in config.ignore_files or any(name.endswith(pat[1:]) for pat in config.ignore_files if pat.startswith("*")):
                continue
            if name.startswith(".") and not config.include_hidden:
                continue
            if name == "mantis-summary.md":
                continue
            try:
                size = entry.stat().st_size
            except OSError:
                continue
            if size > config.max_file_size:
                continue
            language = _language_for(name)
            if not language:
                continue
            rel = entry.relative_to(root).as_posix()
            if rel in seen:
                continue
            seen.add(rel)
            results.append(FileInfo(rel_path=rel, language=language, size=size, mtime=entry.stat().st_mtime))

    for dir_name in config.scan_dirs:
        walk(root / dir_name)
    return results


def language_for_file(rel_path: str) -> str:
    return _language_for(Path(rel_path).name)


def iter_scannable(files: Iterable[FileInfo]) -> Iterable[FileInfo]:
    for info in files:
        if Path(info.rel_path).suffix in SCANNABLE_EXTENSIONS or info.language in {"docker", "markdown"}:
            yield info
