"""Synchronous SuperDev API client."""

from __future__ import annotations

import json
from typing import Any, Iterator
from urllib import request
from urllib.error import HTTPError, URLError

from sdk.python.auth import AuthManager
from sdk.python.exceptions import (
    AuthenticationError,
    ConnectionError,
    NotFoundError,
    RateLimitError,
    ServerError,
    SuperDevError,
    TimeoutError,
    ValidationError,
)
from sdk.python.types import (
    Agent,
    ChatMessage,
    ChatResponse,
    Conversation,
    Deployment,
    EmbeddingRequest,
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


class SuperDevClient:
    """Synchronous client for the SuperDev AI Suite API.

    Args:
        base_url: Base URL of the SuperDev API (e.g. http://localhost:8000).
        api_key: API key for authentication. If not provided, use login() first.
        timeout: Default request timeout in seconds.

    Example::

        client = SuperDevClient("http://localhost:8000", api_key="sk-...")
        projects = client.projects.list()
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: str | None = None,
        timeout: int = 30,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._auth = AuthManager(api_key=api_key, base_url=self.base_url)

    # ── Auth ──────────────────────────────────────────────────────────

    def login(self, email: str, password: str) -> User:
        """Authenticate with email and password."""
        resp = self._post(
            "/api/v1/auth/login",
            json={"email": email, "password": password},
            auth=False,
        )
        self._auth.set_tokens(
            access_token=resp["access_token"],
            refresh_token=resp["refresh_token"],
            expires_in=resp.get("expires_in", 3600),
        )
        return User(**resp["user"])

    def logout(self) -> None:
        """Clear stored tokens."""
        self._auth.clear_tokens()

    # ── Users ─────────────────────────────────────────────────────────

    @property
    def users(self) -> _UserAPI:
        return _UserAPI(self)

    # ── Projects ──────────────────────────────────────────────────────

    @property
    def projects(self) -> _ProjectAPI:
        return _ProjectAPI(self)

    # ── Agents ────────────────────────────────────────────────────────

    @property
    def agents(self) -> _AgentAPI:
        return _AgentAPI(self)

    # ── Workflows ─────────────────────────────────────────────────────

    @property
    def workflows(self) -> _WorkflowAPI:
        return _WorkflowAPI(self)

    # ── Providers ─────────────────────────────────────────────────────

    @property
    def providers(self) -> _ProviderAPI:
        return _ProviderAPI(self)

    # ── Plugins ───────────────────────────────────────────────────────

    @property
    def plugins(self) -> _PluginAPI:
        return _PluginAPI(self)

    # ── Chat ──────────────────────────────────────────────────────────

    @property
    def chat(self) -> _ChatAPI:
        return _ChatAPI(self)

    # ── Deployments ───────────────────────────────────────────────────

    @property
    def deployments(self) -> _DeploymentAPI:
        return _DeploymentAPI(self)

    # ── Low-level ─────────────────────────────────────────────────────

    def _request(
        self,
        method: str,
        path: str,
        json_data: Any = None,
        params: dict[str, Any] | None = None,
        auth: bool = True,
        stream: bool = False,
    ) -> Any:
        url = f"{self.base_url}{path}"
        if params:
            qs = "&".join(f"{k}={v}" for k, v in params.items() if v is not None)
            if qs:
                url += f"?{qs}"

        headers: dict[str, str] = {"Content-Type": "application/json"}
        if auth:
            headers.update(self._auth.get_headers())

        data = json.dumps(json_data).encode() if json_data is not None else None
        req = request.Request(url, data=data, headers=headers, method=method)

        try:
            with request.urlopen(req, timeout=self.timeout) as resp:
                if stream:
                    return self._stream_response(resp)
                body = resp.read().decode()
                return json.loads(body) if body else {}
        except HTTPError as e:
            body = e.read().decode()
            try:
                error_data = json.loads(body)
            except (json.JSONDecodeError, ValueError):
                error_data = {"error": body}
            exc_class = _ERROR_MAP.get(e.code, SuperDevError)
            raise exc_class(
                message=error_data.get("message", error_data.get("error", str(e))),
                status_code=e.code,
                details=error_data,
            ) from e
        except URLError as e:
            raise ConnectionError(str(e.reason)) from e

    def _get(self, path: str, **kwargs: Any) -> Any:
        return self._request("GET", path, **kwargs)

    def _post(self, path: str, **kwargs: Any) -> Any:
        return self._request("POST", path, **kwargs)

    def _put(self, path: str, **kwargs: Any) -> Any:
        return self._request("PUT", path, **kwargs)

    def _delete(self, path: str, **kwargs: Any) -> Any:
        return self._request("DELETE", path, **kwargs)

    def _patch(self, path: str, **kwargs: Any) -> Any:
        return self._request("PATCH", path, **kwargs)

    def _stream_response(self, resp: Any) -> Iterator[StreamingChunk]:
        for line in resp:
            decoded = line.decode().strip()
            if not decoded or not decoded.startswith("data: "):
                continue
            payload = decoded[6:]
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


# ── Resource APIs ─────────────────────────────────────────────────────


class _UserAPI:
    def __init__(self, client: SuperDevClient) -> None:
        self._c = client

    def me(self) -> User:
        return User(**self._c._get("/api/v1/users/me"))

    def list(self, page: int = 1, page_size: int = 20) -> PaginatedResponse[User]:
        data = self._c._get("/api/v1/users", params={"page": page, "page_size": page_size})
        return PaginatedResponse(
            items=[User(**u) for u in data.get("items", [])],
            total=data.get("total", 0),
            page=data.get("page", 1),
            page_size=data.get("page_size", 20),
            has_next=data.get("has_next", False),
            has_previous=data.get("has_previous", False),
        )


class _ProjectAPI:
    def __init__(self, client: SuperDevClient) -> None:
        self._c = client

    def list(self, page: int = 1, page_size: int = 20) -> PaginatedResponse[Project]:
        data = self._c._get("/api/v1/projects", params={"page": page, "page_size": page_size})
        return PaginatedResponse(
            items=[Project(**p) for p in data.get("items", [])],
            total=data.get("total", 0),
            page=data.get("page", 1),
            page_size=data.get("page_size", 20),
            has_next=data.get("has_next", False),
            has_previous=data.get("has_previous", False),
        )

    def get(self, project_id: str) -> Project:
        return Project(**self._c._get(f"/api/v1/projects/{project_id}"))

    def create(self, name: str, description: str = "") -> Project:
        return Project(**self._c._post("/api/v1/projects", json={"name": name, "description": description}))

    def update(self, project_id: str, **kwargs: Any) -> Project:
        return Project(**self._c._patch(f"/api/v1/projects/{project_id}", json=kwargs))

    def delete(self, project_id: str) -> None:
        self._c._delete(f"/api/v1/projects/{project_id}")


class _AgentAPI:
    def __init__(self, client: SuperDevClient) -> None:
        self._c = client

    def list(self, page: int = 1, page_size: int = 20) -> PaginatedResponse[Agent]:
        data = self._c._get("/api/v1/agents", params={"page": page, "page_size": page_size})
        return PaginatedResponse(
            items=[Agent(**a) for a in data.get("items", [])],
            total=data.get("total", 0),
        )

    def get(self, agent_id: str) -> Agent:
        return Agent(**self._c._get(f"/api/v1/agents/{agent_id}"))

    def start(self, agent_id: str, config: dict[str, Any] | None = None) -> Agent:
        return Agent(**self._c._post(f"/api/v1/agents/{agent_id}/start", json=config or {}))

    def stop(self, agent_id: str) -> Agent:
        return Agent(**self._c._post(f"/api/v1/agents/{agent_id}/stop"))

    def logs(self, agent_id: str, limit: int = 100) -> list[dict[str, Any]]:
        data = self._c._get(f"/api/v1/agents/{agent_id}/logs", params={"limit": limit})
        return data.get("logs", [])


class _WorkflowAPI:
    def __init__(self, client: SuperDevClient) -> None:
        self._c = client

    def list(self, page: int = 1, page_size: int = 20) -> PaginatedResponse[Workflow]:
        data = self._c._get("/api/v1/workflows", params={"page": page, "page_size": page_size})
        return PaginatedResponse(
            items=[Workflow(**w) for w in data.get("items", [])],
            total=data.get("total", 0),
        )

    def get(self, workflow_id: str) -> Workflow:
        return Workflow(**self._c._get(f"/api/v1/workflows/{workflow_id}"))

    def create(self, name: str, graph: dict[str, Any], description: str = "") -> Workflow:
        return Workflow(**self._c._post(
            "/api/v1/workflows",
            json={"name": name, "graph": graph, "description": description},
        ))

    def run(self, workflow_id: str, inputs: dict[str, Any] | None = None) -> WorkflowRun:
        return WorkflowRun(**self._c._post(
            f"/api/v1/workflows/{workflow_id}/run",
            json={"inputs": inputs or {}},
        ))

    def get_run(self, workflow_id: str, run_id: str) -> WorkflowRun:
        return WorkflowRun(**self._c._get(f"/api/v1/workflows/{workflow_id}/runs/{run_id}"))

    def cancel_run(self, workflow_id: str, run_id: str) -> WorkflowRun:
        return WorkflowRun(**self._c._post(f"/api/v1/workflows/{workflow_id}/runs/{run_id}/cancel"))

    def delete(self, workflow_id: str) -> None:
        self._c._delete(f"/api/v1/workflows/{workflow_id}")


class _ProviderAPI:
    def __init__(self, client: SuperDevClient) -> None:
        self._c = client

    def list(self) -> list[Provider]:
        data = self._c._get("/api/v1/providers")
        return [Provider(**p) for p in data.get("items", [])]

    def health(self, provider_id: str) -> ProviderHealth:
        return ProviderHealth(**self._c._get(f"/api/v1/providers/{provider_id}/health"))

    def enable(self, provider_id: str) -> Provider:
        return Provider(**self._c._post(f"/api/v1/providers/{provider_id}/enable"))

    def disable(self, provider_id: str) -> Provider:
        return Provider(**self._c._post(f"/api/v1/providers/{provider_id}/disable"))

    def configure(self, provider_id: str, config: dict[str, Any]) -> Provider:
        return Provider(**self._c._put(f"/api/v1/providers/{provider_id}/config", json=config))


class _PluginAPI:
    def __init__(self, client: SuperDevClient) -> None:
        self._c = client

    def list(self) -> list[Plugin]:
        data = self._c._get("/api/v1/plugins")
        return [Plugin(**p) for p in data.get("items", [])]

    def install(self, plugin_id: str) -> Plugin:
        return Plugin(**self._c._post(f"/api/v1/plugins/{plugin_id}/install"))

    def uninstall(self, plugin_id: str) -> None:
        self._c._delete(f"/api/v1/plugins/{plugin_id}")

    def update(self, plugin_id: str) -> Plugin:
        return Plugin(**self._c._post(f"/api/v1/plugins/{plugin_id}/update"))


class _ChatAPI:
    def __init__(self, client: SuperDevClient) -> None:
        self._c = client

    def send(
        self,
        message: str,
        model: str | None = None,
        provider: str | None = None,
        conversation_id: str | None = None,
        system_prompt: str | None = None,
    ) -> ChatResponse:
        payload: dict[str, Any] = {"message": message}
        if model:
            payload["model"] = model
        if provider:
            payload["provider"] = provider
        if conversation_id:
            payload["conversation_id"] = conversation_id
        if system_prompt:
            payload["system_prompt"] = system_prompt
        data = self._c._post("/api/v1/chat", json=payload)
        return ChatResponse(**data)

    def stream(
        self,
        message: str,
        model: str | None = None,
        provider: str | None = None,
        conversation_id: str | None = None,
    ) -> Iterator[StreamingChunk]:
        payload: dict[str, Any] = {"message": message, "stream": True}
        if model:
            payload["model"] = model
        if provider:
            payload["provider"] = provider
        if conversation_id:
            payload["conversation_id"] = conversation_id
        return self._c._request("POST", "/api/v1/chat", json_data=payload, stream=True)

    def conversations(self) -> list[Conversation]:
        data = self._c._get("/api/v1/chat/conversations")
        return [Conversation(**c) for c in data.get("items", [])]

    def embeddings(
        self, input_text: str | list[str], model: str = "text-embedding-3-small"
    ) -> EmbeddingResponse:
        return EmbeddingResponse(**self._c._post(
            "/api/v1/chat/embeddings",
            json={"input": input_text, "model": model},
        ))


class _DeploymentAPI:
    def __init__(self, client: SuperDevClient) -> None:
        self._c = client

    def list(self, project_id: str | None = None) -> list[Deployment]:
        params = {"project_id": project_id} if project_id else {}
        data = self._c._get("/api/v1/deployments", params=params)
        return [Deployment(**d) for d in data.get("items", [])]

    def get(self, deployment_id: str) -> Deployment:
        return Deployment(**self._c._get(f"/api/v1/deployments/{deployment_id}"))

    def create(self, project_id: str, environment: str = "production") -> Deployment:
        return Deployment(**self._c._post(
            "/api/v1/deployments",
            json={"project_id": project_id, "environment": environment},
        ))

    def rollback(self, deployment_id: str) -> Deployment:
        return Deployment(**self._c._post(f"/api/v1/deployments/{deployment_id}/rollback"))
