from __future__ import annotations

import difflib
import os
from typing import Any

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/diff", tags=["diff"])


@router.post("/generate")
async def generate_diff(payload: dict[str, Any]) -> dict[str, Any]:
    old_content = payload.get("old_content", "")
    new_content = payload.get("new_content", "")
    filename = payload.get("filename", "unknown")

    diff_lines = list(difflib.unified_diff(
        old_content.splitlines(keepends=True),
        new_content.splitlines(keepends=True),
        fromfile=f"a/{filename}",
        tofile=f"b/{filename}",
    ))

    additions = sum(1 for l in diff_lines if l.startswith("+") and not l.startswith("+++"))
    deletions = sum(1 for l in diff_lines if l.startswith("-") and not l.startswith("---"))

    return {
        "filename": filename,
        "diff": "".join(diff_lines),
        "stats": {"additions": additions, "deletions": deletions, "total_changes": additions + deletions, "files_changed": 1},
    }


@router.post("/apply")
async def apply_diff(payload: dict[str, Any]) -> dict[str, Any]:
    filepath = payload.get("filepath", "")
    diff_text = payload.get("diff", "")
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail=f"File not found: {filepath}")
    with open(filepath) as f:
        original = f.read()
    patched = _apply_patch(original, diff_text)
    with open(filepath, "w") as f:
        f.write(patched)
    return {"filepath": filepath, "status": "applied", "size_before": len(original), "size_after": len(patched)}


@router.post("/preview")
async def preview_diff(payload: dict[str, Any]) -> dict[str, Any]:
    filepath = payload.get("filepath", "")
    diff_text = payload.get("diff", "")
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail=f"File not found: {filepath}")
    with open(filepath) as f:
        original = f.read()
    patched = _apply_patch(original, diff_text)
    return {
        "filepath": filepath,
        "original_size": len(original),
        "patched_size": len(patched),
        "preview": patched[:5000],
    }


@router.get("/file/{filepath:path}")
async def get_file_diff(filepath: str) -> dict[str, Any]:
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    with open(filepath) as f:
        content = f.read()
    return {"filepath": filepath, "content": content, "size": len(content), "lines": len(content.splitlines())}


def _apply_patch(original: str, diff_text: str) -> str:
    original.splitlines(keepends=True)
    patch_lines = diff_text.splitlines(keepends=True)
    result = list(difflib.restore(patch_lines, 2))
    return "".join(result) if result else original
