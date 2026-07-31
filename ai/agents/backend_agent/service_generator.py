from __future__ import annotations

from typing import Any


class ServiceGenerator:
    """Generates and manages service layer classes."""

    def __init__(self) -> None:
        self._services: dict[str, dict[str, Any]] = {}

    def add_service(
        self,
        name: str,
        methods: list[str],
        dependencies: list[str] | None = None,
    ) -> str:
        self._services[name] = {
            "name": name,
            "methods": methods,
            "dependencies": dependencies or [],
        }
        return name

    def get_service(self, name: str) -> dict[str, Any] | None:
        return self._services.get(name)

    def list_services(self) -> list[dict[str, Any]]:
        return list(self._services.values())

    @property
    def service_count(self) -> int:
        return len(self._services)

    def generate_service_code(self, name: str) -> str:
        svc = self._services.get(name)
        if svc is None:
            return f"# Service '{name}' not found"
        methods_code = "\n".join(f"    async def {m}(self, request: Any) -> Any:\n        ..." for m in svc["methods"])
        return f"from __future__ import annotations\n\nfrom typing import Any\n\n\nclass {name}:\n\n    def __init__(self) -> None:\n        ...\n\n{methods_code}\n"

    def to_dict(self) -> dict[str, Any]:
        return {
            "services": list(self._services.values()),
            "service_count": self.service_count,
        }
