from __future__ import annotations

import os
from collections.abc import Mapping
from typing import Any

from .llm_interfaces import ILLMFactory, ILLMProvider


class LLMFactory(ILLMFactory):
    """Creates LLM provider instances by type name.

    Use ``register_class()`` or ``auto_register()`` to populate.
    """

    def __init__(self) -> None:
        self._provider_classes: dict[str, type[ILLMProvider]] = {}

    # ── Registration ────────────────────────────────────────────────

    def register_class(self, provider_type: str, cls: type[ILLMProvider]) -> str:
        self._provider_classes[provider_type] = cls
        return provider_type

    def register_all(self, class_map: Mapping[str, type[ILLMProvider]]) -> None:
        """Bulk register providers from a dict {name: class}."""
        for name, cls in class_map.items():
            self._provider_classes[name] = cls  # type: ignore[assignment]

    def auto_register(
        self,
        class_map: dict[str, type[ILLMProvider]],
        env_map: dict[str, dict[str, str]],
        default_models: dict[str, str],
    ) -> list[str]:
        """Auto-register providers whose API key env vars are set.

        Returns the list of successfully registered provider names.
        """
        registered: list[str] = []
        for name, cls in class_map.items():
            env_keys = env_map.get(name, {})
            # Check if any required env var is set
            has_key = any(os.getenv(k) for k in env_keys.values())
            if has_key:
                self._provider_classes[name] = cls
                registered.append(name)
        return registered

    # ── ILLMFactory ─────────────────────────────────────────────────

    def create(self, provider_type: str, **kwargs: Any) -> ILLMProvider:
        cls = self._provider_classes.get(provider_type)
        if cls is None:
            raise ValueError(
                f"Unknown provider type: {provider_type}. Available: {', '.join(sorted(self._provider_classes))}"
            )
        return cls(**kwargs)

    def create_with_defaults(
        self, provider_type: str, env_map: dict[str, dict[str, str]], default_models: dict[str, str]
    ) -> ILLMProvider:
        """Create a provider instance reading config from environment."""
        cls = self._provider_classes.get(provider_type)
        if cls is None:
            raise ValueError(f"Unknown provider type: {provider_type}")

        env_config = env_map.get(provider_type, {})
        kwargs: dict[str, Any] = {}

        # Read API key & base_url from env
        for param, env_var in env_config.items():
            val = os.getenv(env_var)
            if val:
                kwargs[param] = val

        # Set default model
        if "model" not in kwargs:
            kwargs["model"] = default_models.get(provider_type, "")

        return cls(**kwargs)

    # ── Introspection ───────────────────────────────────────────────

    def list_types(self) -> list[str]:
        return list(self._provider_classes.keys())

    @property
    def type_count(self) -> int:
        return len(self._provider_classes)

    def to_dict(self) -> dict[str, Any]:
        return {
            "types": list(self._provider_classes.keys()),
            "type_count": self.type_count,
        }
