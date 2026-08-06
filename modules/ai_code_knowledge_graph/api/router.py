"""FastAPI router exposing the AI Code Knowledge Graph through the API.

Mounted by ``backend.app`` via ``_safe_include`` under
``/api/v1/code-knowledge``, following the same convention as the other native
modules.

Every endpoint wraps the shared ``KnowledgeEngine`` singleton facade and
returns the backend standard envelope ``{"success": bool, "data": ...}``.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body

from modules.ai_code_knowledge_graph.core.knowledge_engine import (
    KnowledgeEngine,
    get_engine,
)

router = APIRouter(tags=["code-knowledge"])


def _engine() -> KnowledgeEngine:
    return get_engine()


@router.post("/scan")
async def scan(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    project_root = body.get("project_root")
    meta = body.get("meta")
    result = _engine().scan(project_root=project_root, meta=meta)
    return {"success": True, "data": result}


@router.get("/status")
async def status() -> dict[str, Any]:
    return {"success": True, "data": _engine().status()}


@router.get("/snapshot")
async def snapshot() -> dict[str, Any]:
    return {"success": True, "data": _engine().snapshot()}


@router.get("/files")
async def files(language: str | None = None) -> dict[str, Any]:
    return {"success": True, "data": {"files": _engine().files(language=language)}}


@router.get("/entity-counts")
async def entity_counts() -> dict[str, Any]:
    return {"success": True, "data": _engine().entity_counts()}


@router.get("/languages")
async def languages() -> dict[str, Any]:
    return {"success": True, "data": _engine().languages()}


@router.post("/reset")
async def reset() -> dict[str, Any]:
    _engine().reset()
    return {"success": True, "data": {"reset": True}}
