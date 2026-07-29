from __future__ import annotations

import difflib
import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/prompt-hub", tags=["prompt_hub"])

_prompts: dict[str, dict[str, Any]] = {}
_versions: dict[str, list[dict[str, Any]]] = {}


@router.post("/prompts")
async def create_prompt(name: str, content: str, model: str = "gpt-4o", tags: str = "", description: str = ""):
    prompt_id = f"prompt_{uuid.uuid4().hex[:12]}"
    version = 1
    now = datetime.utcnow().isoformat()
    _prompts[prompt_id] = {
        "id": prompt_id,
        "name": name,
        "description": description,
        "current_version": version,
        "model": model,
        "tags": [t.strip() for t in tags.split(",") if t.strip()],
        "created_at": now,
        "updated_at": now,
    }
    _versions[prompt_id] = [{"version": version, "content": content, "created_at": now, "author": "system"}]
    return _prompts[prompt_id]


@router.get("/prompts")
async def list_prompts(tag: str | None = None, search: str | None = None):
    results = list(_prompts.values())
    if tag:
        results = [p for p in results if tag in p.get("tags", [])]
    if search:
        q = search.lower()
        results = [p for p in results if q in p["name"].lower() or q in p.get("description", "").lower()]
    return {"prompts": results, "total": len(results)}


@router.get("/prompts/{prompt_id}")
async def get_prompt(prompt_id: str, version: int | None = None):
    prompt = _prompts.get(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    versions = _versions.get(prompt_id, [])
    if version:
        v = next((v for v in versions if v["version"] == version), None)
        if not v:
            raise HTTPException(status_code=404, detail=f"Version {version} not found")
        return {**prompt, "version": v}
    return {**prompt, "versions": versions}


@router.put("/prompts/{prompt_id}")
async def update_prompt(prompt_id: str, content: str, author: str = "user"):
    prompt = _prompts.get(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    versions = _versions[prompt_id]
    last = versions[-1]
    if last["content"] == content:
        return {"status": "unchanged"}
    new_version = last["version"] + 1
    now = datetime.utcnow().isoformat()
    versions.append({"version": new_version, "content": content, "created_at": now, "author": author})
    prompt["current_version"] = new_version
    prompt["updated_at"] = now
    return {"status": "updated", "new_version": new_version}


@router.get("/prompts/{prompt_id}/versions")
async def list_versions(prompt_id: str):
    prompt = _prompts.get(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return {"versions": _versions.get(prompt_id, [])}


@router.get("/prompts/{prompt_id}/compare")
async def compare_prompt(prompt_id: str, v1: int, v2: int):
    versions = _versions.get(prompt_id, [])
    a = next((v for v in versions if v["version"] == v1), None)
    b = next((v for v in versions if v["version"] == v2), None)
    if not a or not b:
        raise HTTPException(status_code=404, detail="Version not found")
    diff = list(difflib.unified_diff(a["content"].splitlines(keepends=True), b["content"].splitlines(keepends=True), fromfile=f"v{v1}", tofile=f"v{v2}"))
    return {"version_a": v1, "version_b": v2, "diff": "".join(diff), "additions": sum(1 for l in diff if l.startswith("+") and not l.startswith("+++")), "deletions": sum(1 for l in diff if l.startswith("-") and not l.startswith("---"))}


@router.post("/prompts/{prompt_id}/promote")
async def promote_version(prompt_id: str, version: int):
    prompt = _prompts.get(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    prompt["current_version"] = version
    prompt["updated_at"] = datetime.utcnow().isoformat()
    return {"status": "promoted", "new_current_version": version}


@router.get("/prompts/{prompt_id}/diff")
async def diff_prompt(prompt_id: str, v1: int, v2: int):
    versions = _versions.get(prompt_id, [])
    a = next((v for v in versions if v["version"] == v1), None)
    b = next((v for v in versions if v["version"] == v2), None)
    if not a or not b:
        raise HTTPException(status_code=404, detail="Version not found")
    diff = list(difflib.unified_diff(a["content"].splitlines(keepends=True), b["content"].splitlines(keepends=True), fromfile=f"v{v1}", tofile=f"v{v2}"))
    return {"prompt_id": prompt_id, "from_version": v1, "to_version": v2, "diff": "".join(diff), "additions": sum(1 for l in diff if l.startswith("+") and not l.startswith("+++")), "deletions": sum(1 for l in diff if l.startswith("-") and not l.startswith("---"))}


@router.get("/tags")
async def list_tags():
    tags = set()
    for p in _prompts.values():
        tags.update(p.get("tags", []))
    return {"tags": sorted(tags)}


@router.delete("/prompts/{prompt_id}")
async def delete_prompt(prompt_id: str):
    _prompts.pop(prompt_id, None)
    _versions.pop(prompt_id, None)
    return {"status": "deleted"}