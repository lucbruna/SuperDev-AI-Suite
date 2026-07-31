from __future__ import annotations

import os
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from backend.dependencies import get_current_active_user

router = APIRouter(prefix="/api/code-search", tags=["code_search"], dependencies=[Depends(get_current_active_user)])

_file_index: dict[str, dict[str, Any]] = {}


def _walk_project(root: str = ".") -> None:
    _file_index.clear()
    for dirpath, _, filenames in os.walk(root):
        if any(
            skip in dirpath
            for skip in ("node_modules", ".git", "__pycache__", ".venv", "venv", ".next", "dist", "build")
        ):
            continue
        for f in filenames:
            if f.endswith(
                (
                    ".py",
                    ".ts",
                    ".tsx",
                    ".js",
                    ".jsx",
                    ".go",
                    ".rs",
                    ".yaml",
                    ".yml",
                    ".json",
                    ".md",
                    ".css",
                    ".html",
                    ".sql",
                )
            ):
                path = os.path.join(dirpath, f)
                try:
                    with open(path, encoding="utf-8", errors="ignore") as fh:
                        content = fh.read()
                    rel = os.path.relpath(path, root).replace("\\", "/")
                    _file_index[rel] = {
                        "path": rel,
                        "content": content,
                        "lines": content.count("\n") + 1,
                        "size": len(content),
                        "ext": os.path.splitext(f)[1],
                    }
                except Exception:
                    pass


@router.on_event("startup")
async def _init_index():
    _walk_project()


@router.post("/reindex")
async def reindex(path: str = "."):
    _walk_project(path)
    return {"files_indexed": len(_file_index)}


@router.get("/search")
async def search(
    q: str = Query(..., description="Search query"),
    ext: str | None = Query(None, description="File extension filter"),
    max_results: int = Query(20, le=50),
):
    if not _file_index:
        _walk_project()

    query = q.lower()
    results = []

    for path, info in _file_index.items():
        content = info["content"]
        ext_match = not ext or info.get("ext") == ext if ext else True
        if not ext_match:
            continue

        lines = content.split("\n")
        matches = []
        for i, line in enumerate(lines, 1):
            if query in line.lower():
                matches.append({"line": i, "content": line.strip()[:200]})

        if matches:
            score = len(matches) * 10
            score += 5 if query in path.lower() else 0
            results.append(
                {
                    "file": path,
                    "ext": info.get("ext", ""),
                    "total_lines": info["lines"],
                    "matches_count": len(matches),
                    "matches": matches[:5],
                    "score": score,
                }
            )

    results.sort(key=lambda r: -r["score"])

    return {
        "query": q,
        "total_results": len(results),
        "total_files_searched": len(_file_index),
        "results": results[:max_results],
        "file_filters": list({info["ext"] for info in _file_index.values()}),
    }


@router.get("/file/{filepath:path}")
async def get_file(filepath: str):
    info = _file_index.get(filepath)
    if not info:
        for p, i in _file_index.items():
            if p.endswith(filepath):
                info = i
                break
        if not info:
            filepath = filepath.lstrip("/")
            if os.path.exists(filepath):
                with open(filepath, encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                return {
                    "filepath": filepath,
                    "content": content,
                    "size": len(content),
                    "lines": content.count("\n") + 1,
                }
            raise HTTPException(status_code=404, detail=f"File not found: {filepath}")
    return {"filepath": info["path"], "content": info["content"], "size": info["size"], "lines": info["lines"]}


@router.get("/stats")
async def get_stats():
    if not _file_index:
        _walk_project()
    by_ext: dict[str, int] = {}
    for info in _file_index.values():
        ext = info.get("ext", "unknown")
        by_ext[ext] = by_ext.get(ext, 0) + 1
    return {
        "total_files": len(_file_index),
        "total_lines": sum(i["lines"] for i in _file_index.values()),
        "total_size_bytes": sum(i["size"] for i in _file_index.values()),
        "by_extension": by_ext,
    }
