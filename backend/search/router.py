"""Full-text search API routes."""

from __future__ import annotations

from typing import Any

from backend.dependencies import get_current_active_user
from backend.search.full_text_search import SearchableType, SearchDocument, full_text_search
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

router = APIRouter(dependencies=[Depends(get_current_active_user)])


class IndexDocumentRequest(BaseModel):
    id: str | None = None
    type: str = "custom"
    title: str
    content: str
    metadata: dict[str, Any] = {}


class SearchRequest(BaseModel):
    query: str
    type: str | None = None
    limit: int = 10
    offset: int = 0


@router.post("/index")
async def index_document(
    request: IndexDocumentRequest,
    current_user: dict[str, Any] = Depends(get_current_active_user),
) -> dict[str, Any]:
    from backend.utils.uuid_utils import generate_uuid

    doc_id = request.id or generate_uuid()
    doc = SearchDocument(
        id=doc_id,
        type=SearchableType(request.type),
        title=request.title,
        content=request.content,
        metadata=request.metadata,
    )
    full_text_search.add_document(doc)
    return {"success": True, "document_id": doc_id}


@router.post("/search")
async def search(
    request: SearchRequest,
    current_user: dict[str, Any] = Depends(get_current_active_user),
) -> dict[str, Any]:
    doc_type = SearchableType(request.type) if request.type else None
    results = full_text_search.search(
        request.query,
        doc_type=doc_type,
        limit=request.limit,
        offset=request.offset,
    )
    return {
        "query": request.query,
        "total": len(results),
        "results": [
            {
                "id": r.document_id,
                "type": r.document_type,
                "title": r.title,
                "snippet": r.snippet,
                "score": r.score,
                "metadata": r.metadata,
            }
            for r in results
        ],
    }


@router.delete("/documents/{doc_id}")
async def remove_document(
    doc_id: str,
    current_user: dict[str, Any] = Depends(get_current_active_user),
) -> dict[str, bool]:
    removed = full_text_search.remove_document(doc_id)
    return {"removed": removed}


@router.get("/documents")
async def list_documents(
    type: str | None = None,
    limit: int = Query(default=50, le=200),
    current_user: dict[str, Any] = Depends(get_current_active_user),
) -> dict[str, Any]:
    doc_type = SearchableType(type) if type else None
    docs = full_text_search.list_documents(doc_type=doc_type, limit=limit)
    return {
        "documents": [
            {
                "id": d.id,
                "type": d.type.value,
                "title": d.title,
                "created_at": d.created_at.isoformat(),
            }
            for d in docs
        ]
    }


@router.get("/stats")
async def search_stats(
    current_user: dict[str, Any] = Depends(get_current_active_user),
) -> dict[str, Any]:
    return full_text_search.get_stats()
