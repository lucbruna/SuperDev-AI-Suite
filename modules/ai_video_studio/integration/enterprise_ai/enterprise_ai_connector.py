"""Enterprise AI Connector — facade over the enterprise AI sub-components."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.integration.connector_base import DomainConnector
from modules.ai_video_studio.integration.enterprise_ai.embeddings_connector import (
    get_embeddings_connector,
)
from modules.ai_video_studio.integration.enterprise_ai.knowledge_connector import (
    get_knowledge_connector,
)
from modules.ai_video_studio.integration.enterprise_ai.llm_router import get_llm_router
from modules.ai_video_studio.integration.enterprise_ai.memory_connector import (
    get_memory_connector,
)
from modules.ai_video_studio.integration.enterprise_ai.multi_agent_manager import (
    get_multi_agent_manager,
)
from modules.ai_video_studio.integration.enterprise_ai.prompt_dispatcher import (
    get_prompt_dispatcher,
)
from modules.ai_video_studio.integration.enterprise_ai.reasoning_engine import (
    get_reasoning_engine,
)
from modules.ai_video_studio.integration.enterprise_ai.vector_database_connector import (
    get_vector_database_connector,
)


class EnterpriseAIConnector(DomainConnector):
    """Routes, dispatches and reasons across the enterprise AI stack."""

    domain = "enterprise_ai"
    description = "LLM routing, prompt dispatch, multi-agent reasoning, memory, knowledge, embeddings and vector search"

    def __init__(self) -> None:
        super().__init__()
        self._register("route_prompt", self._route_prompt)
        self._register("dispatch_prompt", self._dispatch_prompt)
        self._register("reason", self._reason)
        self._register("multi_agent", self._multi_agent)
        self._register("store_memory", self._store_memory)
        self._register("recall_memory", self._recall_memory)
        self._register("ingest_knowledge", self._ingest_knowledge)
        self._register("query_knowledge", self._query_knowledge)
        self._register("embed", self._embed)
        self._register("vector_search", self._vector_search)

    def _route_prompt(self, data: dict[str, Any]) -> dict[str, Any]:
        return get_llm_router().route(data.get("prompt", ""), task=data.get("task"))

    def _dispatch_prompt(self, data: dict[str, Any]) -> dict[str, Any]:
        return get_prompt_dispatcher().dispatch(data.get("prompt", ""), context=data.get("context"))

    def _reason(self, data: dict[str, Any]) -> dict[str, Any]:
        return get_reasoning_engine().reason(data.get("question", ""), evidence=data.get("evidence"))

    def _multi_agent(self, data: dict[str, Any]) -> dict[str, Any]:
        return get_multi_agent_manager().run(data.get("task", ""), agents=data.get("agents"))

    def _store_memory(self, data: dict[str, Any]) -> dict[str, Any]:
        return get_memory_connector().store(data.get("content", ""), **data.get("meta", {}))

    def _recall_memory(self, data: dict[str, Any]) -> dict[str, Any]:
        return get_memory_connector().recall(data.get("query", ""))

    def _ingest_knowledge(self, data: dict[str, Any]) -> dict[str, Any]:
        return get_knowledge_connector().ingest(data.get("fact", ""), **data.get("meta", {}))

    def _query_knowledge(self, data: dict[str, Any]) -> dict[str, Any]:
        return get_knowledge_connector().query(data.get("question", ""))

    def _embed(self, data: dict[str, Any]) -> dict[str, Any]:
        return get_embeddings_connector().embed(data.get("text", ""))

    def _vector_search(self, data: dict[str, Any]) -> dict[str, Any]:
        return get_vector_database_connector().search(data.get("query", ""), top_k=data.get("top_k", 5))


_enterprise_ai_connector: EnterpriseAIConnector | None = None


def get_enterprise_ai_connector() -> EnterpriseAIConnector:
    global _enterprise_ai_connector
    if _enterprise_ai_connector is None:
        _enterprise_ai_connector = EnterpriseAIConnector()
    return _enterprise_ai_connector
