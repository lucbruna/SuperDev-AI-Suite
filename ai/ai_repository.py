from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

BackendType = Literal["memory", "redis", "database"]


class AIRepository:
    """Repository layer for AI data persistence."""

    def __init__(self, backend: BackendType = "memory"):
        self._backend_type = backend
        self._sessions: dict[str, dict[str, Any]] = {}
        self._conversations: dict[str, dict[str, Any]] = {}
        self._agent_states: dict[str, dict[str, Any]] = {}
        self._model_configs: dict[str, dict[str, Any]] = {}
        self._cache: dict[str, Any] = {}

    def save_session(self, session_id: str, data: dict[str, Any]) -> None:
        """Save a session."""
        self._sessions[session_id] = {**data, "updated_at": datetime.now(UTC).isoformat()}

    def get_session(self, session_id: str) -> dict[str, Any] | None:
        """Get a session by ID."""
        return self._sessions.get(session_id)

    def delete_session(self, session_id: str) -> None:
        """Delete a session."""
        self._sessions.pop(session_id, None)

    def list_sessions(self, user_id: str | None = None) -> list[dict[str, Any]]:
        """List sessions, optionally filtered by user_id."""
        sessions = list(self._sessions.values())
        if user_id:
            sessions = [s for s in sessions if s.get("user_id") == user_id]
        return sessions

    def save_conversation(self, conversation_id: str, data: dict[str, Any]) -> None:
        """Save a conversation."""
        self._conversations[conversation_id] = {**data, "updated_at": datetime.now(UTC).isoformat()}

    def get_conversation(self, conversation_id: str) -> dict[str, Any] | None:
        """Get a conversation by ID."""
        return self._conversations.get(conversation_id)

    def delete_conversation(self, conversation_id: str) -> None:
        """Delete a conversation."""
        self._conversations.pop(conversation_id, None)

    def list_conversations(self, session_id: str | None = None) -> list[dict[str, Any]]:
        """List conversations, optionally filtered by session_id."""
        conversations = list(self._conversations.values())
        if session_id:
            conversations = [c for c in conversations if c.get("session_id") == session_id]
        return conversations

    def save_agent_state(self, agent_id: str, data: dict[str, Any]) -> None:
        """Save agent state."""
        self._agent_states[agent_id] = {**data, "updated_at": datetime.now(UTC).isoformat()}

    def get_agent_state(self, agent_id: str) -> dict[str, Any] | None:
        """Get agent state by ID."""
        return self._agent_states.get(agent_id)

    def save_model_config(self, model_name: str, config: dict[str, Any]) -> None:
        """Save a model configuration."""
        self._model_configs[model_name] = {**config, "updated_at": datetime.now(UTC).isoformat()}

    def get_model_config(self, model_name: str) -> dict[str, Any] | None:
        """Get a model configuration."""
        return self._model_configs.get(model_name)

    def list_model_configs(self) -> list[dict[str, Any]]:
        """List all model configurations."""
        return [
            {"name": name, **config}
            for name, config in self._model_configs.items()
        ]

    def cache_get(self, key: str) -> Any | None:
        """Get a value from cache."""
        return self._cache.get(key)

    def cache_set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set a value in cache with optional TTL."""
        self._cache[key] = value

    def cache_delete(self, key: str) -> None:
        """Delete a value from cache."""
        self._cache.pop(key, None)

    def find(self, collection: str, **filters: Any) -> list[dict[str, Any]]:
        """Find items in a collection by filters."""
        collections = {
            "sessions": self._sessions,
            "conversations": self._conversations,
            "agent_states": self._agent_states,
            "model_configs": self._model_configs,
        }
        items = collections.get(collection, {})
        results = list(items.values())
        for key, value in filters.items():
            results = [r for r in results if r.get(key) == value]
        return results

    def clear(self) -> None:
        """Clear all data."""
        self._sessions.clear()
        self._conversations.clear()
        self._agent_states.clear()
        self._model_configs.clear()
        self._cache.clear()

    def health(self) -> dict[str, Any]:
        """Get repository health status."""
        return {
            "status": "healthy",
            "backend": self._backend_type,
            "sessions": len(self._sessions),
            "conversations": len(self._conversations),
            "agent_states": len(self._agent_states),
            "model_configs": len(self._model_configs),
            "cache_entries": len(self._cache),
            "timestamp": datetime.now(UTC).isoformat(),
        }
