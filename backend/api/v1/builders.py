"""FastAPI routes for all SuperDev builders (project scaffolding generators).

Exposes 4 builders as REST endpoints under /api/v1/builders:
- backend: FastAPI/Django/Flask scaffolding
- frontend: React/Next.js/Vue/Svelte scaffolding
- api: REST/GraphQL/WebSocket/gRPC scaffolding
- microservices: Multi-service microservices with Docker Compose
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from backend.dependencies import get_current_active_user

router = APIRouter(
    tags=["builders"],
    dependencies=[Depends(get_current_active_user)],
)


# ─── Schemas ──────────────────────────────────────────────────────────────────


class GeneratedFileOut(BaseModel):
    path: str
    content_length: int
    language: str
    overwrite: bool = False


class BuildResultOut(BaseModel):
    builder_name: str
    project_name: str = ""
    project_slug: str = ""
    total_files: int = 0
    files: list[GeneratedFileOut] = []
    build_duration_ms: float = 0.0
    error: str = ""
    timestamp: str = ""


class BuildRequest(BaseModel):
    project_name: str = "my-app"
    project_slug: str = ""
    output_dir: str = "."
    framework: str = "fastapi"
    database: str = "postgresql"
    api_type: str = "rest"
    include_auth: bool = True
    include_docker: bool = True
    include_tests: bool = True
    include_ci: bool = False
    include_docs: bool = False
    packages: list[str] = []
    extra_config: dict[str, Any] = {}


class BuilderInfo(BaseModel):
    name: str
    description: str
    available: bool
    frameworks: list[str] = []
    api_types: list[str] = []


class BuildersListResponse(BaseModel):
    builders: list[BuilderInfo]


# ─── Builder Registry ─────────────────────────────────────────────────────────


BUILDER_REGISTRY: dict[str, dict[str, Any]] = {
    "backend": {
        "name": "backend",
        "description": "Generates backend project scaffolding (FastAPI, Django, Flask)",
        "class": None,  # Lazy-imported
        "frameworks": ["fastapi", "django", "flask", "python"],
    },
    "frontend": {
        "name": "frontend",
        "description": "Generates frontend project scaffolding (React, Next.js, Vue, Svelte)",
        "class": None,
        "frameworks": ["react", "nextjs", "vue", "svelte"],
    },
    "api": {
        "name": "api",
        "description": "Generates API scaffolding (REST, GraphQL, WebSocket, gRPC)",
        "class": None,
        "api_types": ["rest", "graphql", "websocket", "grpc"],
    },
    "microservices": {
        "name": "microservices",
        "description": "Generates multi-service microservices project with Docker Compose orchestration",
        "class": None,
        "frameworks": ["fastapi"],
    },
}


def _resolve_builder_class(builder_id: str) -> Any:
    """Lazy-import and resolve a builder class by ID."""
    if builder_id not in BUILDER_REGISTRY:
        return None

    entry = BUILDER_REGISTRY[builder_id]
    if entry["class"] is not None:
        return entry["class"]

    imports = {
        "backend": "builders.backend.builder:BackendBuilder",
        "frontend": "builders.frontend.builder:FrontendBuilder",
        "api": "builders.api.builder:APIBuilder",
        "microservices": "builders.microservices.builder:MicroservicesBuilder",
    }

    import_path = imports.get(builder_id)
    if not import_path:
        return None

    try:
        module_path, class_name = import_path.split(":")
        import importlib

        module = importlib.import_module(module_path)
        cls = getattr(module, class_name)
        entry["class"] = cls
        return cls
    except (ImportError, AttributeError) as e:
        logger.warning(
            "Failed to import builder '%s' from %s: %s",
            builder_id,
            import_path,
            e,
        )
        return None


async def run_builder(
    builder_id: str,
    builder_class: Any,
    request: BuildRequest,
) -> dict[str, Any]:
    """Instantiate and run a builder, returning structured results."""
    import time

    from builders.base import ApiType, BuildConfig, DatabaseType, FrameworkType

    start = time.time()
    try:
        # Map string values to enum types
        framework_map = {e.value: e for e in FrameworkType}
        database_map = {e.value: e for e in DatabaseType}
        api_type_map = {e.value: e for e in ApiType}

        config = BuildConfig(
            project_name=request.project_name,
            project_slug=request.project_slug or "",
            output_dir=request.output_dir,
            framework=framework_map.get(request.framework, FrameworkType.FASTAPI),
            database=database_map.get(request.database, DatabaseType.POSTGRESQL),
            api_type=api_type_map.get(request.api_type, ApiType.REST),
            include_auth=request.include_auth,
            include_docker=request.include_docker,
            include_tests=request.include_tests,
            include_ci=request.include_ci,
            include_docs=request.include_docs,
            packages=request.packages,
            extra_config=request.extra_config,
        )

        builder = builder_class()
        result = await builder.build(config)

        return {
            "builder_name": result.builder_name,
            "project_name": result.project_name,
            "project_slug": result.project_slug,
            "total_files": result.total_files,
            "files": [f.to_dict() for f in (result.files or [])],
            "build_duration_ms": result.build_duration_ms,
            "error": result.error,
            "timestamp": result.timestamp,
        }
    except Exception as e:
        return {
            "builder_name": builder_id,
            "project_name": request.project_name,
            "project_slug": request.project_slug or request.project_name.lower().replace(" ", "-"),
            "total_files": 0,
            "files": [],
            "build_duration_ms": round((time.time() - start) * 1000, 2),
            "error": str(e)[:200],
            "timestamp": "",
        }


# ─── Endpoints ────────────────────────────────────────────────────────────────


@router.get("", response_model=BuildersListResponse)
async def list_builders() -> dict[str, Any]:
    """List all available builders."""
    builders = []
    for bid, info in BUILDER_REGISTRY.items():
        cls = _resolve_builder_class(bid)
        builders.append(
            BuilderInfo(
                name=bid,
                description=info["description"],
                available=cls is not None,
                frameworks=info.get("frameworks", []),
                api_types=info.get("api_types", []),
            )
        )
    return {"builders": builders}


@router.post("/{builder_id}/build", response_model=BuildResultOut)
async def run_build(
    builder_id: str,
    request: BuildRequest = BuildRequest(),
) -> dict[str, Any]:
    """Run a specific builder with the given configuration."""
    cls = _resolve_builder_class(builder_id)
    if cls is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Builder '{builder_id}' not found. Use GET /api/v1/builders to list available builders.",
        )

    return await run_builder(builder_id, cls, request)


@router.post("/all/build", response_model=list[BuildResultOut])
async def run_all_builders(
    request: BuildRequest = BuildRequest(),
) -> list[dict[str, Any]]:
    """Run all available builders with the same configuration."""
    results: list[dict[str, Any]] = []
    for bid in BUILDER_REGISTRY:
        cls = _resolve_builder_class(bid)
        if cls is None:
            continue
        result = await run_builder(bid, cls, request)
        results.append(result)
    return results
