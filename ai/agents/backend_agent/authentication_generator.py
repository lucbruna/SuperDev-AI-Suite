from __future__ import annotations

from typing import Any

STRATEGIES = {"jwt", "oauth", "session", "api_key"}


class AuthenticationGenerator:
    """Generates and manages authentication provider configurations."""

    def __init__(self) -> None:
        self._providers: dict[str, dict[str, Any]] = {}

    def add_provider(
        self,
        name: str,
        strategy: str,
        config: dict[str, Any] | None = None,
    ) -> str:
        strategy = strategy.lower()
        if strategy not in STRATEGIES:
            strategy = "jwt"
        self._providers[name] = {
            "name": name,
            "strategy": strategy,
            "config": config or {},
        }
        return name

    def get_provider(self, name: str) -> dict[str, Any] | None:
        return self._providers.get(name)

    def remove_provider(self, name: str) -> bool:
        if name in self._providers:
            del self._providers[name]
            return True
        return False

    def list_providers(self) -> list[dict[str, Any]]:
        return list(self._providers.values())

    @property
    def provider_count(self) -> int:
        return len(self._providers)

    def generate_login_code(self, provider: str) -> str:
        prov = self._providers.get(provider)
        if prov is None:
            return f"# Provider '{provider}' not found"
        strategy = prov["strategy"]
        templates = {
            "jwt": (
                "from __future__ import annotations\n\nimport jwt\nfrom datetime import datetime, timedelta\n\n\n"
                f"def login_{provider}(username: str, password: str) -> str:\n"
                f'    """Authenticate and return JWT token."""\n    ...\n    return token\n'
            ),
            "oauth": (
                f"from __future__ import annotations\n\n\n"
                f"class {provider}OAuth:\n\n"
                f'    """OAuth2 authentication for {provider}."""\n\n'
                f"    async def authorize(self) -> str:\n        ...\n"
                f"    async def callback(self, code: str) -> dict:\n        ...\n"
            ),
            "session": (
                f"from __future__ import annotations\n\n\n"
                f"class {provider}Session:\n\n"
                f'    """Session-based authentication."""\n\n'
                f"    async def login(self, credentials: dict) -> str:\n        ...\n"
                f"    async def logout(self, session_id: str) -> None:\n        ...\n"
            ),
            "api_key": (
                f"from __future__ import annotations\n\n\n"
                f"class {provider}APIKey:\n\n"
                f'    """API key authentication."""\n\n'
                f"    def validate_key(self, api_key: str) -> bool:\n        ...\n"
                f"    def generate_key(self) -> str:\n        ...\n"
            ),
        }
        return templates.get(strategy, templates["jwt"])

    def to_dict(self) -> dict[str, Any]:
        return {
            "providers": list(self._providers.values()),
            "provider_count": self.provider_count,
        }
