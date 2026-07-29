"""API Builder — generates REST, GraphQL, and WebSocket API scaffolding."""

from __future__ import annotations

import json
import time
from typing import Any

from ..base import (
    ApiType, BaseBuilder, BuildConfig, BuildResult, DatabaseType,
    FrameworkType, GeneratedFile,
)


class APIBuilder(BaseBuilder):
    name = "api"
    description = "Generates API scaffolding (REST, GraphQL, WebSocket, gRPC)"
    framework = FrameworkType.FASTAPI

    async def build(self, config: BuildConfig) -> BuildResult:
        start = time.time()
        slug = config.project_slug
        files: list[GeneratedFile] = []

        try:
            if config.api_type == ApiType.GRAPHQL:
                files = self._generate_graphql(config, slug)
            elif config.api_type == ApiType.WEBSOCKET:
                files = self._generate_websocket(config, slug)
            elif config.api_type == ApiType.GRPC:
                files = self._generate_grpc(config, slug)
            else:
                files = self._generate_rest(config, slug)

            elapsed_ms = round((time.time() - start) * 1000, 2)
            return BuildResult(
                builder_name=self.name,
                project_name=config.project_name,
                project_slug=slug,
                total_files=len(files),
                files=files,
                build_duration_ms=elapsed_ms,
            )
        except Exception as e:
            return BuildResult(
                builder_name=self.name,
                project_name=config.project_name,
                project_slug=slug,
                error=str(e),
                build_duration_ms=round((time.time() - start) * 1000, 2),
            )

    def _generate_rest(self, config: BuildConfig, slug: str) -> list[GeneratedFile]:
        files: list[GeneratedFile] = []

        # CRUD router template
        files.append(self._make_file(
            f"{slug}/router.py",
            f'''"""REST API router with CRUD endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1", tags=["api"])


class ItemBase(BaseModel):
    name: str
    description: str = ""


class ItemCreate(ItemBase):
    pass


class ItemResponse(ItemBase):
    id: int

    model_config = {{"from_attributes": True}}


ITEMS: list[dict] = []
_counter: int = 0


@router.get("/items", response_model=list[ItemResponse])
async def list_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> list[dict]:
    return ITEMS[skip : skip + limit]


@router.post("/items", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemCreate) -> dict:
    global _counter
    _counter += 1
    new_item = {{"id": _counter, **item.model_dump()}}
    ITEMS.append(new_item)
    return new_item


@router.get("/items/{{item_id}}", response_model=ItemResponse)
async def get_item(item_id: int) -> dict:
    for item in ITEMS:
        if item["id"] == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")


@router.put("/items/{{item_id}}", response_model=ItemResponse)
async def update_item(item_id: int, item: ItemCreate) -> dict:
    for i, existing in enumerate(ITEMS):
        if existing["id"] == item_id:
            ITEMS[i] = {{"id": item_id, **item.model_dump()}}
            return ITEMS[i]
    raise HTTPException(status_code=404, detail="Item not found")


@router.delete("/items/{{item_id}}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int) -> None:
    for i, existing in enumerate(ITEMS):
        if existing["id"] == item_id:
            ITEMS.pop(i)
            return
    raise HTTPException(status_code=404, detail="Item not found")
''',
            language="python",
        ))

        # Auth router
        if config.include_auth:
            files.append(self._make_file(
                f"{slug}/auth_router.py",
                '''"""Authentication router with JWT."""

from __future__ import annotations

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

FAKE_USERS_DB: dict[str, dict] = {}


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest) -> dict:
    if request.username not in FAKE_USERS_DB:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": "fake-jwt-token", "token_type": "bearer"}
''',
                language="python",
            ))

        # Pagination utility
        files.append(self._make_file(
            f"{slug}/pagination.py",
            '''"""Pagination utilities for REST APIs."""

from __future__ import annotations

from math import ceil
from typing import Any, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool


def paginate(items: list, page: int = 1, page_size: int = 50) -> dict[str, Any]:
    total = len(items)
    total_pages = max(1, ceil(total / page_size))
    start = (page - 1) * page_size
    end = start + page_size
    return {
        "items": items[start:end],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
    }
''',
            language="python",
        ))

        # Error handlers
        files.append(self._make_file(
            f"{slug}/errors.py",
            '''"""API error handling utilities."""

from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message, "error": exc.__class__.__name__},
    )
''',
            language="python",
        ))

        # requirements.txt
        deps = [
            "fastapi>=0.110.0",
            "uvicorn[standard]>=0.27.0",
            "pydantic>=2.5.0",
        ]
        if config.include_auth:
            deps.extend(["python-jose[cryptography]>=3.3.0", "passlib[bcrypt]>=1.7.4"])
        files.append(self._make_file(
            f"{slug}/requirements.txt",
            "\n".join(deps) + "\n",
            language="ini",
        ))

        return files

    def _generate_graphql(self, config: BuildConfig, slug: str) -> list[GeneratedFile]:
        """Generate GraphQL API scaffolding with Strawberry."""
        files: list[GeneratedFile] = []

        files.append(self._make_file(
            f"{slug}/schema.py",
            f'''"""GraphQL schema using Strawberry."""

from __future__ import annotations

import strawberry


@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Hello from {config.project_name} GraphQL API"

    @strawberry.field
    def health(self) -> str:
        return "healthy"


schema = strawberry.Schema(query=Query)
''',
            language="python",
        ))

        files.append(self._make_file(
            f"{slug}/main.py",
            '''"""GraphQL API entry point."""

from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from .schema import schema

app = FastAPI(title="GraphQL API")
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")
''',
            language="python",
        ))

        files.append(self._make_file(
            f"{slug}/requirements.txt",
            "fastapi>=0.110.0\nstrawberry-graphql>=0.227.0\nuvicorn[standard]>=0.27.0\n",
            language="ini",
        ))

        return files

    def _generate_websocket(self, config: BuildConfig, slug: str) -> list[GeneratedFile]:
        """Generate WebSocket server scaffolding."""
        files: list[GeneratedFile] = []

        files.append(self._make_file(
            f"{slug}/server.py",
            f'''"""WebSocket server with FastAPI."""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI(title="{config.project_name} WebSocket")


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: list[WebSocket] = []

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self._connections.append(ws)

    def disconnect(self, ws: WebSocket) -> None:
        self._connections.remove(ws)

    async def broadcast(self, message: dict[str, Any]) -> None:
        for conn in self._connections:
            try:
                await conn.send_json(message)
            except Exception:
                pass


manager = ConnectionManager()


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket) -> None:
    await manager.connect(ws)
    try:
        while True:
            data = await ws.receive_text()
            message = json.loads(data)
            response = {{
                "echo": message,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }}
            await ws.send_json(response)
    except WebSocketDisconnect:
        manager.disconnect(ws)
    except Exception:
        manager.disconnect(ws)


@app.get("/")
async def root() -> dict[str, str]:
    return {{"message": "WebSocket API", "connections": len(manager._connections)}}
''',
            language="python",
        ))

        files.append(self._make_file(
            f"{slug}/requirements.txt",
            "fastapi>=0.110.0\nuvicorn[standard]>=0.27.0\nwebsockets>=12.0\n",
            language="ini",
        ))

        return files

    def _generate_grpc(self, config: BuildConfig, slug: str) -> list[GeneratedFile]:
        """Generate gRPC service scaffolding."""
        files: list[GeneratedFile] = []

        files.append(self._make_file(
            f"{slug}/proto/service.proto",
            f'''syntax = "proto3";

package {slug};

service {config.project_name.replace(" ", "")}Service {{
  rpc SayHello (HelloRequest) returns (HelloResponse);
  rpc Health (HealthRequest) returns (HealthResponse);
}}

message HelloRequest {{
  string name = 1;
}}

message HelloResponse {{
  string message = 1;
}}

message HealthRequest {{}}

message HealthResponse {{
  string status = 1;
}}
''',
            language="ini",
        ))

        files.append(self._make_file(
            f"{slug}/server.py",
            f'''"""gRPC server implementation."""

from __future__ import annotations

from concurrent import futures
import grpc

# Generated proto imports would go here
# from .proto import service_pb2, service_pb2_grpc


class GreeterServicer:  # Would inherit from generated base
    def SayHello(self, request, context):
        return None  # service_pb2.HelloResponse(message=f"Hello, {{request.name}}!")

    def Health(self, request, context):
        return None  # service_pb2.HealthResponse(status="healthy")


def serve() -> None:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    # Would register the servicer
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
''',
            language="python",
        ))

        files.append(self._make_file(
            f"{slug}/requirements.txt",
            "grpcio>=1.62.0\ngrpcio-tools>=1.62.0\nprotobuf>=4.25.0\n",
            language="ini",
        ))

        return files
