from __future__ import annotations

import asyncio
import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Union

import httpx
import websockets


@dataclass
class SuperDevConfig:
    base_url: str = "http://localhost:8000"
    api_key: Optional[str] = None
    ws_url: Optional[str] = None
    timeout: int = 60


@dataclass
class Project:
    id: str
    name: str
    description: str = ""
    created_at: datetime
    updated_at: datetime
    owner_id: str
    settings: dict = field(default_factory=dict)


@dataclass
class Agent:
    id: str
    name: str
    type: str
    status: str
    config: dict = field(default_factory=dict)


@dataclass
class ChatMessage:
    role: str
    content: str
    metadata: dict = field(default_factory=dict)


@dataclass
class ChatResponse:
    id: str
    content: str
    model: str
    usage: dict = field(default_factory=dict)
    finish_reason: str = "stop"


@dataclass
class VerificationResult:
    task_id: str
    success: bool
    stage: str
    final_code: Optional[str] = None
    error: Optional[str] = None
    iterations: int = 0
    generation: dict = field(default_factory=dict)
    execution: dict = field(default_factory=dict)
    testing: dict = field(default_factory=dict)
    review: dict = field(default_factory=dict)
    correction: dict = field(default_factory=dict)


class SuperDevClient:
    def __init__(self, config: Optional[SuperDevConfig] = None):
        self.config = config or SuperDevConfig()
        self._client: Optional[httpx.AsyncClient] = None
        self._ws: Optional[websockets.WebSocketClientProtocol] = None
        self._api_key = self.config.api_key or os.getenv("SUPERDEV_API_KEY")

    async def __aenter__(self):
        self._client = httpx.AsyncClient(
            base_url=self.config.base_url,
            timeout=self.config.timeout,
            headers={"Authorization": f"Bearer {self._api_key}"} if self._api_key else {},
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()
        if self._ws:
            await self._ws.close()

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self._api_key}"} if self._api_key else {}

    async def _request(self, method: str, path: str, **kwargs) -> dict:
        if not self._client:
            self._client = httpx.AsyncClient(
                base_url=self.config.base_url,
                timeout=self.config.timeout,
                headers=self._headers(),
            )
        response = await self._client.request(method, path, **kwargs)
        response.raise_for_status()
        return response.json()

    async def health_check(self) -> dict:
        return await self._request("GET", "/api/v1/health")

    async def get_version(self) -> dict:
        return await self._request("GET", "/api/v1/version")

    async def create_project(
        self,
        name: str,
        description: str = "",
        template: str = "default",
    ) -> Project:
        data = await self._request("POST", "/api/v1/projects", json={
            "name": name,
            "description": description,
            "template": template,
        })
        return Project(**data["data"])

    async def list_projects(self) -> list[Project]:
        data = await self._request("GET", "/api/v1/projects")
        return [Project(**p) for p in data["data"]]

    async def get_project(self, project_id: str) -> Project:
        data = await self._request("GET", f"/api/v1/projects/{project_id}")
        return Project(**data["data"])

    async def delete_project(self, project_id: str) -> bool:
        await self._request("DELETE", f"/api/v1/projects/{project_id}")
        return True

    async def list_agents(self) -> list[Agent]:
        data = await self._request("GET", "/api/v1/agents")
        return [Agent(**a) for a in data["data"]]

    async def get_agent(self, agent_id: str) -> Agent:
        data = await self._request("GET", f"/api/v1/agents/{agent_id}")
        return Agent(**data["data"])

    async def execute_agent_task(
        self,
        agent_id: str,
        task: str,
        context: dict = None,
    ) -> dict:
        return await self._request("POST", f"/api/v1/agents/{agent_id}/execute", json={
            "task": task,
            "context": context or {},
        })

    async def chat(
        self,
        messages: list[ChatMessage],
        model: str = None,
        provider: str = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        stream: bool = False,
    ) -> Union[ChatResponse, AsyncIterator[ChatResponse]]:
        payload = {
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "model": model,
            "provider": provider,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
        }
        
        if stream:
            return self._stream_chat(payload)
        
        data = await self._request("POST", "/api/v1/chat/completions", json=payload)
        return ChatResponse(**data["data"])

    async def _stream_chat(self, payload: dict) -> AsyncIterator[ChatResponse]:
        async with self._client.stream("POST", "/api/v1/chat/stream", json=payload) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    import json
                    chunk = json.loads(data)
                    yield ChatResponse(
                        id=chunk.get("id", ""),
                        content=chunk.get("delta", ""),
                        model=chunk.get("model", ""),
                        finish_reason=chunk.get("finish_reason"),
                    )

    async def verify_code(
        self,
        task_description: str,
        language: str = "python",
        context: str = None,
        requirements: list[str] = None,
        existing_code: str = None,
        test_files: dict[str, str] = None,
        max_iterations: int = 3,
        provider: str = None,
    ) -> VerificationResult:
        data = await self._request("POST", "/api/v1/verify", json={
            "task_description": task_description,
            "language": language,
            "context": context,
            "requirements": requirements or [],
            "existing_code": existing_code,
            "test_files": test_files,
            "max_iterations": max_iterations,
            "provider": provider,
        })
        return VerificationResult(**data)

    async def generate_code(
        self,
        prompt: str,
        language: str = "python",
        context: str = None,
        provider: str = None,
    ) -> dict:
        return await self._request("POST", "/api/v1/verify/generate", json={
            "prompt": prompt,
            "language": language,
            "context": context,
            "provider": provider,
        })

    async def execute_code(
        self,
        code: str,
        language: str = "python",
    ) -> dict:
        return await self._request("POST", "/api/v1/verify/execute", json={
            "code": code,
            "language": language,
        })

    async def review_code(
        self,
        code: str,
        language: str = "python",
        context: str = None,
        provider: str = None,
    ) -> dict:
        return await self._request("POST", "/api/v1/verify/review", json={
            "code": code,
            "language": language,
            "context": context,
            "provider": provider,
        })

    async def create_workflow(
        self,
        name: str,
        description: str,
        steps: list[dict],
        variables: dict = None,
        tags: list[str] = None,
    ) -> dict:
        return await self._request("POST", "/api/v1/workflows", json={
            "name": name,
            "description": description,
            "steps": steps,
            "variables": variables or {},
            "tags": tags or [],
        })

    async def execute_workflow(
        self,
        workflow_id: str,
        variables: dict = None,
    ) -> dict:
        return await self._request("POST", f"/api/v1/workflows/{workflow_id}/execute", json={
            "variables": variables or {},
        })

    async def list_workflows(self, tags: list[str] = None) -> list[dict]:
        params = {}
        if tags:
            params["tags"] = ",".join(tags)
        data = await self._request("GET", "/api/v1/workflows", params=params)
        return data["data"]

    async def get_workflow(self, workflow_id: str) -> dict:
        data = await self._request("GET", f"/api/v1/workflows/{workflow_id}")
        return data["data"]

    async def delete_workflow(self, workflow_id: str) -> bool:
        await self._request("DELETE", f"/api/v1/workflows/{workflow_id}")
        return True

    async def create_knowledge_base(
        self,
        name: str,
        description: str = None,
        kb_type: str = "documentation",
        is_public: bool = False,
    ) -> dict:
        return await self._request("POST", "/api/v1/knowledge-bases", json={
            "name": name,
            "description": description,
            "type": kb_type,
            "is_public": is_public,
        })

    async def add_document(
        self,
        kb_id: str,
        title: str,
        content: str,
        source_url: str = None,
        source_type: str = None,
        language: str = None,
        tags: list[str] = None,
        metadata: dict = None,
    ) -> dict:
        return await self._request("POST", f"/api/v1/knowledge-bases/{kb_id}/documents", json={
            "title": title,
            "content": content,
            "source_url": source_url,
            "source_type": source_type,
            "language": language,
            "tags": tags or [],
            "metadata": metadata or {},
        })

    async def search_knowledge(
        self,
        query: str,
        kb_ids: list[str] = None,
        top_k: int = 10,
        similarity_threshold: float = 0.5,
    ) -> dict:
        return await self._request("POST", "/api/v1/knowledge-bases/search", json={
            "query": query,
            "knowledge_base_ids": kb_ids,
            "top_k": top_k,
            "similarity_threshold": similarity_threshold,
        })

    async def get_context(
        self,
        query: str,
        kb_ids: list[str] = None,
        max_tokens: int = 8000,
    ) -> dict:
        return await self._request("POST", "/api/v1/knowledge-bases/context", json={
            "query": query,
            "knowledge_base_ids": kb_ids,
            "max_tokens": max_tokens,
        })

    async def ingest_repository(
        self,
        kb_id: str,
        repo_path: str,
        file_patterns: list[str] = None,
        exclude_patterns: list[str] = None,
    ) -> dict:
        return await self._request("POST", f"/api/v1/knowledge-bases/{kb_id}/ingest-repo", json={
            "repo_path": repo_path,
            "file_patterns": file_patterns,
            "exclude_patterns": exclude_patterns,
        })

    async def find_similar_code(
        self,
        code_snippet: str,
        language: str = None,
        kb_ids: list[str] = None,
        top_k: int = 5,
    ) -> dict:
        return await self._request("POST", "/api/v1/knowledge-bases/similar-code", json={
            "code_snippet": code_snippet,
            "language": language,
            "knowledge_base_ids": kb_ids,
            "top_k": top_k,
        })

    async def list_plugins(
        self,
        plugin_type: str = None,
        tag: str = None,
        search: str = None,
    ) -> list[dict]:
        params = {}
        if plugin_type:
            params["plugin_type"] = plugin_type
        if tag:
            params["tag"] = tag
        if search:
            params["search"] = search
        data = await self._request("GET", "/api/v1/plugins/registry", params=params)
        return data

    async def install_plugin(self, slug: str) -> dict:
        return await self._request("POST", "/api/v1/plugins/install", json={"slug": slug})

    async def uninstall_plugin(self, slug: str) -> bool:
        await self._request("DELETE", f"/api/v1/plugins/{slug}")
        return True

    async def enable_plugin(self, slug: str) -> dict:
        return await self._request("POST", f"/api/v1/plugins/{slug}/enable")

    async def disable_plugin(self, slug: str) -> dict:
        return await self._request("POST", f"/api/v1/plugins/{slug}/disable")

    async def update_plugin_config(self, slug: str, settings: dict) -> dict:
        return await self._request("PUT", f"/api/v1/plugins/{slug}/config", json={"settings": settings})

    async def connect_websocket(self, project_id: str = None):
        ws_url = self.config.ws_url or self.config.base_url.replace("http", "ws")
        uri = f"{ws_url}/api/v1/ws"
        if project_id:
            uri += f"?project_id={project_id}"
        
        self._ws = await websockets.connect(uri)
        return self._ws

    async def subscribe_events(self, event_types: list[str]) -> AsyncIterator[dict]:
        if not self._ws:
            await self.connect_websocket()
        
        await self._ws.send(json.dumps({
            "type": "subscribe",
            "events": event_types,
        }))
        
        async for message in self._ws:
            yield json.loads(message)

    async def send_command(self, command: str, params: dict = None) -> dict:
        return await self._request("POST", "/api/v1/cli/execute", json={
            "command": command,
            "params": params or {},
        })


class SuperDevSyncClient:
    def __init__(self, config: Optional[SuperDevConfig] = None):
        self.config = config or SuperDevConfig()
        self._api_key = self.config.api_key or os.getenv("SUPERDEV_API_KEY")
        self._client: Optional[httpx.Client] = None

    def __enter__(self):
        self._client = httpx.Client(
            base_url=self.config.base_url,
            timeout=self.config.timeout,
            headers={"Authorization": f"Bearer {self._api_key}"} if self._api_key else {},
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            self._client.close()

    def _request(self, method: str, path: str, **kwargs) -> dict:
        if not self._client:
            self._client = httpx.Client(
                base_url=self.config.base_url,
                timeout=self.config.timeout,
                headers={"Authorization": f"Bearer {self._api_key}"} if self._api_key else {},
            )
        response = self._client.request(method, path, **kwargs)
        response.raise_for_status()
        return response.json()

    def health_check(self) -> dict:
        return self._request("GET", "/api/v1/health")

    def chat(self, messages: list[dict], **kwargs) -> dict:
        return self._request("POST", "/api/v1/chat/completions", json={
            "messages": messages,
            **kwargs,
        })

    def verify_code(self, task_description: str, **kwargs) -> dict:
        return self._request("POST", "/api/v1/verify", json={
            "task_description": task_description,
            **kwargs,
        })


async def create_client(config: Optional[SuperDevConfig] = None) -> SuperDevClient:
    client = SuperDevClient(config)
    await client.__aenter__()
    return client