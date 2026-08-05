from __future__ import annotations

import difflib
import os
from typing import Any

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/diff", tags=["diff"])

# Frontend compatibility router: the diff-merge UI posts full file content
# to /api/v1/workspace/diff/apply. Kept separate so the classic unified-diff
# endpoints below stay unchanged.
workspace_router = APIRouter(prefix="/workspace/diff", tags=["workspace-diff"])


@router.post("/generate")
async def generate_diff(payload: dict[str, Any]) -> dict[str, Any]:
    old_content = payload.get("old_content", "")
    new_content = payload.get("new_content", "")
    filename = payload.get("filename", "unknown")

    diff_lines = list(
        difflib.unified_diff(
            old_content.splitlines(keepends=True),
            new_content.splitlines(keepends=True),
            fromfile=f"a/{filename}",
            tofile=f"b/{filename}",
        )
    )

    additions = sum(1 for l in diff_lines if l.startswith("+") and not l.startswith("+++"))
    deletions = sum(1 for l in diff_lines if l.startswith("-") and not l.startswith("---"))

    return {
        "filename": filename,
        "diff": "".join(diff_lines),
        "stats": {
            "additions": additions,
            "deletions": deletions,
            "total_changes": additions + deletions,
            "files_changed": 1,
        },
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


@workspace_router.post("/apply")
async def apply_file_content(payload: dict[str, Any]) -> dict[str, Any]:
    """Write full file content (used by the frontend diff-merge UI).

    Accepts ``{path, content}`` — the complete new file content for the
    given workspace path — and persists it directly.
    """
    filepath = payload.get("path", "")
    content = payload.get("content", "")
    if not filepath:
        raise HTTPException(status_code=400, detail="path is required")
    if not isinstance(content, str):
        raise HTTPException(status_code=400, detail="content must be a string")

    directory = os.path.dirname(filepath)
    if directory:
        os.makedirs(directory, exist_ok=True)
    size_before = os.path.getsize(filepath) if os.path.exists(filepath) else 0
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return {
        "path": filepath,
        "status": "applied",
        "size_before": size_before,
        "size_after": len(content),
    }
