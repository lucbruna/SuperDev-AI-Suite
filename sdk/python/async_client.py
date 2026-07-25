"""Asynchronous SuperDev API client using httpx."""

from __future__ import annotations

import json
from typing import Any, AsyncIterator

try:
    import httpx
except ImportError:
    httpx = None  # type: ignore[assignment]

from sdk.python.auth import AuthManager
from sdk.python.exceptions import (
    AuthenticationError,
    ConnectionError,
    NotFoundError,
    RateLimitError,
    ServerError,
    SuperDevError,
    ValidationError,
)
from sdk.python.types import (
    Agent,
    ChatResponse,
    Conversation,
    Deployment,
    EmbeddingResponse,
    MessageRole,
    PaginatedResponse,
    Plugin,
    Project,
    Provider,
    ProviderHealth,
    StreamingChunk,
    User,
    Workflow,
    WorkflowRun,
)

_ERROR_MAP: dict[int, type[SuperDevError]] = {
    401: AuthenticationError,
    403: AuthenticationError,
    404: NotFoundError,
    422: ValidationError,
    429: RateLimitError,
    500: ServerError,
}


class AsyncSuperDevClient:
    """Asynchronous client for the SuperDev AI Suite API.

    Requires the ``httpx`` package: ``pip install superdev-sdk[async]``

    Example::

        async with AsyncSuperDevClient("http://localhost:8000", api_key="sk-...") as client:
            projects = await client.projects.list()
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: str | None = None,
        timeout: int = 30,
    ) -> None:
        if httpx is None:
            raise ImportError("httpx is required for async usage. Install with: pip install superdev-sdk[async]")
        self.base_url = base_url.rstrip("/")
        self._auth = AuthManager(api_key=api_key, base_url=self.base_url)
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            follow_redirects=True,
        )

    async def __aenter__(self) -> AsyncSuperDevClient:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self._client.aclose()

    # ── Auth ──────────────────────────────────────────────────────────

    async def login(self, email: str, password: str) -> User:
        resp = await self._post("/api/v1/auth/login", json={"email": email, "password": password}, auth=False)
        self._auth.set_tokens(
            access_token=resp["access_token"],
            refresh_token=resp["refresh_token"],
            expires_in=resp.get("expires_in", 3600),
        )
        return User(**resp["user"])

    def logout(self) -> None:
        self._auth.clear_tokens()

    # ── Resource properties ───────────────────────────────────────────

    @property
    def users(self) -> AsyncUserAPI:
        return AsyncUserAPI(self)

    @property
    def projects(self) -> AsyncProjectAPI:
        return AsyncProjectAPI(self)

    @property
    def agents(self) -> AsyncAgentAPI:
        return AsyncAgentAPI(self)

    @property
    def workflows(self) -> AsyncWorkflowAPI:
        return AsyncWorkflowAPI(self)

    @property
    def providers(self) -> AsyncProviderAPI:
        return AsyncProviderAPI(self)

    @property
    def plugins(self) -> AsyncPluginAPI:
        return AsyncPluginAPI(self)

    @property
    def chat(self) -> AsyncChatAPI:
        return AsyncChatAPI(self)

    # ── Low-level ─────────────────────────────────────────────────────

    async def _request(
        self,
        method: str,
        path: str,
        json_data: Any = None,
        params: dict[str, Any] | None = None,
        auth: bool = True,
    ) -> Any:
        headers: dict[str, str] = {}
        if auth:
            headers.update(self._auth.get_headers())

        resp = await self._client.request(
            method,
            path,
            json=json_data,
            params=params,
            headers=headers,
        )

        if resp.status_code >= 400:
            try:
                error_data = resp.json()
            except Exception:
                error_data = {"error": resp.text}
            exc_class = _ERROR_MAP.get(resp.status_code, SuperDevError)
            raise exc_class(
                message=error_data.get("message", error_data.get("error", str(resp.status_code))),
                status_code=resp.status_code,
                details=error_data,
            )

        if resp.status_code == 204:
            return {}
        return resp.json()

    async def _get(self, path: str, **kwargs: Any) -> Any:
        return await self._request("GET", path, **kwargs)

    async def _post(self, path: str, **kwargs: Any) -> Any:
        return await self._request("POST", path, **kwargs)

    async def _put(self, path: str, **kwargs: Any) -> Any:
        return await self._request("PUT", path, **kwargs)

    async def _delete(self, path: str, **kwargs: Any) -> Any:
        return await self._request("DELETE", path, **kwargs)

    async def _patch(self, path: str, **kwargs: Any) -> Any:
        return await self._request("PATCH", path, **kwargs)

    async def stream(
        self,
        method: str,
        path: str,
        json_data: Any = None,
        auth: bool = True,
    ) -> AsyncIterator[StreamingChunk]:
        headers: dict[str, str] = {}
        if auth:
            headers.update(self._auth.get_headers())

        async with self._client.stream(method, path, json=json_data, headers=headers) as resp:
            async for line in resp.aiter_lines():
                if not line or not line.startswith("data: "):
                    continue
                payload = line[6:]
                if payload == "[DONE]":
                    break
                try:
                    data = json.loads(payload)
                    yield StreamingChunk(
                        delta=data.get("delta", ""),
                        model=data.get("model", ""),
                        finish_reason=data.get("finish_reason"),
                        usage=data.get("usage", {}),
                    )
                except json.JSONDecodeError:
                    continue


# ── Async Resource APIs ──────────────────────────────────────────────


class AsyncUserAPI:
    def __init__(self, client: AsyncSuperDevClient) -> None:
        self._c = client

    async def me(self) -> User:
        return User(**await self._c._get("/api/v1/users/me"))

    async def list(self, page: int = 1, page_size: int = 20) -> PaginatedResponse[User]:
        data = await self._c._get("/api/v1/users", params={"page": page, "page_size": page_size})
        return PaginatedResponse(
            items=[User(**u) for u in data.get("items", [])],
            total=data.get("total", 0),
        )


class AsyncProjectAPI:
    def __init__(self, client: AsyncSuperDevClient) -> None:
        self._c = client

    async def list(self, page: int = 1, page_size: int = 20) -> PaginatedResponse[Project]:
        data = await self._c._get("/api/v1/projects", params={"page": page, "page_size": page_size})
        return PaginatedResponse(
            items=[Project(**p) for p in data.get("items", [])],
            total=data.get("total", 0),
        )

    async def get(self, project_id: str) -> Project:
        return Project(**await self._c._get(f"/api/v1/projects/{project_id}"))

    async def create(self, name: str, description: str = "") -> Project:
        return Project(**await self._c._post("/api/v1/projects", json={"name": name, "description": description}))

    async def delete(self, project_id: str) -> None:
        await self._c._delete(f"/api/v1/projects/{project_id}")


class AsyncAgentAPI:
    def __init__(self, client: AsyncSuperDevClient) -> None:
        self._c = client

    async def list(self, page: int = 1, page_size: int = 20) -> PaginatedResponse[Agent]:
        data = await self._c._get("/api/v1/agents", params={"page": page, "page_size": page_size})
        return PaginatedResponse(
            items=[Agent(**a) for a in data.get("items", [])],
            total=data.get("total", 0),
        )

    async def get(self, agent_id: str) -> Agent:
        return Agent(**await self._c._get(f"/api/v1/agents/{agent_id}"))

    async def start(self, agent_id: str, config: dict[str, Any] | None = None) -> Agent:
        return Agent(**await self._c._post(f"/api/v1/agents/{agent_id}/start", json=config or {}))

    async def stop(self, agent_id: str) -> Agent:
        return Agent(**await self._c._post(f"/api/v1/agents/{agent_id}/stop"))


class AsyncWorkflowAPI:
    def __init__(self, client: AsyncSuperDevClient) -> None:
        self._c = client

    async def list(self, page: int = 1, page_size: int = 20) -> PaginatedResponse[Workflow]:
        data = await self._c._get("/api/v1/workflows", params={"page": page, "page_size": page_size})
        return PaginatedResponse(
            items=[Workflow(**w) for w in data.get("items", [])],
            total=data.get("total", 0),
        )

    async def get(self, workflow_id: str) -> Workflow:
        return Workflow(**await self._c._get(f"/api/v1/workflows/{workflow_id}"))

    async def create(self, name: str, graph: dict[str, Any], description: str = "") -> Workflow:
        return Workflow(**await self._c._post(
            "/api/v1/workflows",
            json={"name": name, "graph": graph, "description": description},
        ))

    async def run(self, workflow_id: str, inputs: dict[str, Any] | None = None) -> WorkflowRun:
        return WorkflowRun(**await self._c._post(
            f"/api/v1/workflows/{workflow_id}/run",
            json={"inputs": inputs or {}},
        ))

    async def delete(self, workflow_id: str) -> None:
        await self._c._delete(f"/api/v1/workflows/{workflow_id}")


class AsyncProviderAPI:
    def __init__(self, client: AsyncSuperDevClient) -> None:
        self._c = client

    async def list(self) -> list[Provider]:
        data = await self._c._get("/api/v1/providers")
        return [Provider(**p) for p in data.get("items", [])]

    async def health(self, provider_id: str) -> ProviderHealth:
        return ProviderHealth(**await self._c._get(f"/api/v1/providers/{provider_id}/health"))

    async def enable(self, provider_id: str) -> Provider:
        return Provider(**await self._c._post(f"/api/v1/providers/{provider_id}/enable"))

    async def disable(self, provider_id: str) -> Provider:
        return Provider(**await self._c._post(f"/api/v1/providers/{provider_id}/disable"))


class AsyncPluginAPI:
    def __init__(self, client: AsyncSuperDevClient) -> None:
        self._c = client

    async def list(self) -> list[Plugin]:
        data = await self._c._get("/api/v1/plugins")
        return [Plugin(**p) for p in data.get("items", [])]

    async def install(self, plugin_id: str) -> Plugin:
        return Plugin(**await self._c._post(f"/api/v1/plugins/{plugin_id}/install"))

    async def uninstall(self, plugin_id: str) -> None:
        await self._c._delete(f"/api/v1/plugins/{plugin_id}")


class AsyncChatAPI:
    def __init__(self, client: AsyncSuperDevClient) -> None:
        self._c = client

    async def send(
        self,
        message: str,
        model: str | None = None,
        provider: str | None = None,
        conversation_id: str | None = None,
    ) -> ChatResponse:
        payload: dict[str, Any] = {"message": message}
        if model:
            payload["model"] = model
        if provider:
            payload["provider"] = provider
        if conversation_id:
            payload["conversation_id"] = conversation_id
        data = await self._c._post("/api/v1/chat", json=payload)
        return ChatResponse(**data)

    async def stream(
        self,
        message: str,
        model: str | None = None,
        provider: str | None = None,
    ) -> AsyncIterator[StreamingChunk]:
        payload: dict[str, Any] = {"message": message, "stream": True}
        if model:
            payload["model"] = model
        if provider:
            payload["provider"] = provider
        async for chunk in self._c.stream("POST", "/api/v1/chat", json_data=payload):
            yield chunk

    async def conversations(self) -> list[Conversation]:
        data = await self._c._get("/api/v1/chat/conversations")
        return [Conversation(**c) for c in data.get("items", [])]

    async def embeddings(
        self, input_text: str | list[str], model: str = "text-embedding-3-small"
    ) -> EmbeddingResponse:
        return EmbeddingResponse(**await self._c._post(
            "/api/v1/chat/embeddings",
            json={"input": input_text, "model": model},
        ))
