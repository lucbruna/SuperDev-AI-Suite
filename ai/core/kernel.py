from datetime import UTC, datetime
from typing import Any

from ..providers.provider_configuration import ProviderConfig
from .configuration import AIPlatformConfig


class AIKernel:
    def __init__(self, config: AIPlatformConfig):
        self.config = config
        self._registry: dict[str, Any] = {}
        self._bootstrapped = False

    def bootstrap(self) -> list[ProviderConfig]:
        if self._bootstrapped:
            return self._registry.get("provider_configs", [])
        configs = [
            ProviderConfig(
                name="openai",
                type="openai",
                default_model=self.config.model_defaults.get("openai", "gpt-4o"),
                max_retries=self.config.max_retries,
                timeout=self.config.timeout,
            ),
            ProviderConfig(
                name="anthropic",
                type="anthropic",
                default_model=self.config.model_defaults.get("anthropic", "claude-3-5-sonnet-20241022"),
                max_retries=self.config.max_retries,
                timeout=self.config.timeout,
            ),
            ProviderConfig(
                name="gemini",
                type="gemini",
                default_model=self.config.model_defaults.get("gemini", "gemini-1.5-pro"),
                max_retries=self.config.max_retries,
                timeout=self.config.timeout,
            ),
            ProviderConfig(
                name="ollama",
                type="ollama",
                default_model=self.config.model_defaults.get("ollama", "llama3"),
                base_url="http://localhost:11434",
                max_retries=self.config.max_retries,
                timeout=self.config.timeout,
            ),
        ]
        self._registry["provider_configs"] = configs
        self._bootstrapped = True
        return configs

    def health(self) -> dict[str, Any]:
        return {
            "status": "healthy",
            "bootstrapped": self._bootstrapped,
            "timestamp": datetime.now(UTC).isoformat(),
            "config": self.config.model_dump(),
        }

    def configuration(self) -> AIPlatformConfig:
        return self.config

    def registry(self) -> dict[str, Any]:
        return dict(self._registry)

    def registry_set(self, key: str, value: Any) -> None:
        self._registry[key] = value

    def registry_get(self, key: str) -> Any:
        return self._registry.get(key)
