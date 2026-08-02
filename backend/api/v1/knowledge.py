from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.rbac import Action, Resource, require_permission
from backend.database.session import get_db
from backend.dependencies import get_current_active_user
from backend.knowledge_base.models import KnowledgeBaseType
from backend.knowledge_base.service import KnowledgeBaseService, get_knowledge_base_service

router = APIRouter(dependencies=[Depends(get_current_active_user)])


class KnowledgeBaseCreate(BaseModel):
    name: str
    description: str | None = None
    type: str = "documentation"
    is_public: bool = False


class KnowledgeBaseUpdate(BaseModel):
    description: str | None = None
    type: str | None = None
    is_public: bool | None = None


class KnowledgeBaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None
    type: str
    is_public: bool
    created_at: str
    updated_at: str


class DocumentCreate(BaseModel):
    title: str
    content: str
    source_url: str | None = None
    source_type: str | None = None
    language: str | None = None
    tags: list[str] = []
    metadata: dict = {}


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    knowledge_base_id: UUID
    title: str
    content: str
    source_url: str | None
    source_type: str | None
    language: str | None
    tags: list[str]
    metadata: dict
    created_at: str
    updated_at: str


class SearchRequest(BaseModel):
    query: str
    knowledge_base_ids: list[UUID] | None = None
    top_k: int = 10
    similarity_threshold: float = 0.5


class SearchResultItem(BaseModel):
    entry_id: UUID
    chunk_id: UUID
    title: str
    content: str
    similarity: float
    language: str | None
    tags: list[str]


class SearchResponse(BaseModel):
    results: list[SearchResultItem]
    total: int


class ContextRequest(BaseModel):
    query: str
    knowledge_base_ids: list[UUID] | None = None
    max_tokens: int = 8000


class ContextResponse(BaseModel):
    context: str
    total_tokens: int


class IngestRepoRequest(BaseModel):
    repo_path: str
    file_patterns: list[str] | None = None
    exclude_patterns: list[str] | None = None


@router.post("/knowledge-bases", response_model=KnowledgeBaseResponse, status_code=status.HTTP_201_CREATED)
async def create_knowledge_base(
    request: KnowledgeBaseCreate,
    db: AsyncSession = Depends(get_db),
    service: KnowledgeBaseService = Depends(get_knowledge_base_service),
    _user: Any = Depends(require_permission(Resource.KNOWLEDGE, Action.CREATE)),
) -> KnowledgeBaseResponse:
    kb = await service.create_knowledge_base(
        name=request.name,
        description=request.description,
        type=KnowledgeBaseType(request.type),
        is_public=request.is_public,
    )
    return KnowledgeBaseResponse(
        id=kb.id,
        name=kb.name,
        description=kb.description,
        type=kb.type.value,
        is_public=kb.is_public,
        created_at=kb.created_at.isoformat(),
        updated_at=kb.updated_at.isoformat(),
    )


@router.get("/knowledge-bases", response_model=list[KnowledgeBaseResponse])
async def list_knowledge_bases(
    is_public: bool | None = Query(None),
    type: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    service: KnowledgeBaseService = Depends(get_knowledge_base_service),
) -> list[KnowledgeBaseResponse]:
    kbs = await service.vector_store.list_knowledge_bases(is_public=is_public, kb_type=type)
    return [
        KnowledgeBaseResponse(
            id=kb.id,
            name=kb.name,
            description=kb.description,
            type=kb.type.value,
            is_public=kb.is_public,
            created_at=kb.created_at.isoformat(),
            updated_at=kb.updated_at.isoformat(),
        )
        for kb in kbs
    ]


@router.get("/knowledge-bases/{kb_id}", response_model=KnowledgeBaseResponse)
async def get_knowledge_base(
    kb_id: UUID,
    db: AsyncSession = Depends(get_db),
    service: KnowledgeBaseService = Depends(get_knowledge_base_service),
) -> KnowledgeBaseResponse:
    kb = await service.vector_store.get_knowledge_base(kb_id)
    if not kb:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge base not found")

    return KnowledgeBaseResponse(
        id=kb.id,
        name=kb.name,
        description=kb.description,
        type=kb.type.value,
        is_public=kb.is_public,
        created_at=kb.created_at.isoformat(),
        updated_at=kb.updated_at.isoformat(),
    )


@router.delete("/knowledge-bases/{kb_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_knowledge_base(
    kb_id: UUID,
    db: AsyncSession = Depends(get_db),
    service: KnowledgeBaseService = Depends(get_knowledge_base_service),
    _user: Any = Depends(require_permission(Resource.KNOWLEDGE, Action.DELETE)),
) -> None:
    deleted = await service.vector_store.delete_knowledge_base(kb_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge base not found")


@router.post("/knowledge-bases/{kb_id}/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def add_document(
    kb_id: UUID,
    request: DocumentCreate,
    db: AsyncSession = Depends(get_db),
    service: KnowledgeBaseService = Depends(get_knowledge_base_service),
    _user: Any = Depends(require_permission(Resource.KNOWLEDGE, Action.CREATE)),
) -> DocumentResponse:
    entry = await service.add_document(
        knowledge_base_id=kb_id,
        title=request.title,
        content=request.content,
        source_url=request.source_url,
        source_type=request.source_type,
        language=request.language,
        tags=request.tags,
        metadata=request.metadata,
    )
    return DocumentResponse(
        id=entry.id,
        knowledge_base_id=entry.knowledge_base_id,
        title=entry.title,
        content=entry.content,
        source_url=entry.source_url,
        source_type=entry.source_type,
        language=entry.language,
        tags=entry.tags,
        metadata=entry.metadata,
        created_at=entry.created_at.isoformat(),
        updated_at=entry.updated_at.isoformat(),
    )


@router.post(
    "/knowledge-bases/{kb_id}/documents/code", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED
)
async def add_code_file(
    kb_id: UUID,
    file_path: str,
    content: str,
    language: str | None = None,
    tags: list[str] | None = None,
    db: AsyncSession = Depends(get_db),
    service: KnowledgeBaseService = Depends(get_knowledge_base_service),
    _user: Any = Depends(require_permission(Resource.KNOWLEDGE, Action.CREATE)),
) -> DocumentResponse:
    entry = await service.add_code_file(
        knowledge_base_id=kb_id,
        file_path=file_path,
        content=content,
        language=language,
        tags=tags,
    )
    return DocumentResponse(
        id=entry.id,
        knowledge_base_id=entry.knowledge_base_id,
        title=entry.title,
        content=entry.content,
        source_url=entry.source_url,
        source_type=entry.source_type,
        language=entry.language,
        tags=entry.tags,
        metadata=entry.metadata,
        created_at=entry.created_at.isoformat(),
        updated_at=entry.updated_at.isoformat(),
    )


@router.post("/knowledge-bases/{kb_id}/search", response_model=SearchResponse)
async def search_knowledge_base(
    kb_id: UUID,
    request: SearchRequest,
    db: AsyncSession = Depends(get_db),
    service: KnowledgeBaseService = Depends(get_knowledge_base_service),
) -> SearchResponse:
    kb = await service.vector_store.get_knowledge_base(kb_id)
    if not kb:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge base not found")

    results = await service.search(
        query=request.query,
        knowledge_base_ids=[kb_id],
        top_k=request.top_k,
        similarity_threshold=request.similarity_threshold,
    )

    return SearchResponse(
        results=[
            SearchResultItem(
                entry_id=r.entry.id,
                chunk_id=r.chunk.id,
                title=r.entry.title,
                content=r.chunk.content,
                similarity=r.similarity,
                language=r.entry.language,
                tags=r.entry.tags,
            )
            for r in results
        ],
        total=len(results),
    )


@router.post("/knowledge-bases/search", response_model=SearchResponse)
async def search_all_knowledge_bases(
    request: SearchRequest,
    db: AsyncSession = Depends(get_db),
    service: KnowledgeBaseService = Depends(get_knowledge_base_service),
) -> SearchResponse:
    results = await service.search(
        query=request.query,
        knowledge_base_ids=request.knowledge_base_ids,
        top_k=request.top_k,
        similarity_threshold=request.similarity_threshold,
    )

    return SearchResponse(
        results=[
            SearchResultItem(
                entry_id=r.entry.id,
                chunk_id=r.chunk.id,
                title=r.entry.title,
                content=r.chunk.content,
                similarity=r.similarity,
                language=r.entry.language,
                tags=r.entry.tags,
            )
            for r in results
        ],
        total=len(results),
    )


@router.post("/knowledge-bases/{kb_id}/context", response_model=ContextResponse)
async def get_context(
    kb_id: UUID,
    request: ContextRequest,
    db: AsyncSession = Depends(get_db),
    service: KnowledgeBaseService = Depends(get_knowledge_base_service),
) -> ContextResponse:
    kb = await service.vector_store.get_knowledge_base(kb_id)
    if not kb:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge base not found")

    context = await service.get_context_for_query(
        query=request.query,
        knowledge_base_ids=[kb_id],
        max_tokens=request.max_tokens,
    )

    return ContextResponse(
        context=context,
        total_tokens=len(context.split()),
    )


@router.post("/knowledge-bases/context", response_model=ContextResponse)
async def get_context_all(
    request: ContextRequest,
    db: AsyncSession = Depends(get_db),
    service: KnowledgeBaseService = Depends(get_knowledge_base_service),
) -> ContextResponse:
    context = await service.get_context_for_query(
        query=request.query,
        knowledge_base_ids=request.knowledge_base_ids,
        max_tokens=request.max_tokens,
    )

    return ContextResponse(
        context=context,
        total_tokens=len(context.split()),
    )


@router.post("/knowledge-bases/{kb_id}/ingest-repo", status_code=status.HTTP_200_OK)
async def ingest_repository(
    kb_id: UUID,
    request: IngestRepoRequest,
    db: AsyncSession = Depends(get_db),
    service: KnowledgeBaseService = Depends(get_knowledge_base_service),
    _user: Any = Depends(require_permission(Resource.KNOWLEDGE, Action.CREATE)),
) -> dict[str, Any]:
    kb = await service.vector_store.get_knowledge_base(kb_id)
    if not kb:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge base not found")

    count = await service.ingest_repository(
        knowledge_base_id=kb_id,
        repo_path=request.repo_path,
        file_patterns=request.file_patterns,
        exclude_patterns=request.exclude_patterns,
    )

    return {"ingested_files": count, "knowledge_base_id": str(kb_id)}


@router.post("/knowledge-bases/{kb_id}/similar-code", response_model=SearchResponse)
async def find_similar_code(
    kb_id: UUID,
    code_snippet: str,
    language: str | None = Query(None),
    top_k: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
    service: KnowledgeBaseService = Depends(get_knowledge_base_service),
) -> SearchResponse:
    kb = await service.vector_store.get_knowledge_base(kb_id)
    if not kb:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge base not found")

    results = await service.find_similar_code(
        code_snippet=code_snippet,
        language=language,
        knowledge_base_ids=[kb_id],
        top_k=top_k,
    )

    return SearchResponse(
        results=[
            SearchResultItem(
                entry_id=r.entry.id,
                chunk_id=r.chunk.id,
                title=r.entry.title,
                content=r.chunk.content,
                similarity=r.similarity,
                language=r.entry.language,
                tags=r.entry.tags,
            )
            for r in results
        ],
        total=len(results),
    )
