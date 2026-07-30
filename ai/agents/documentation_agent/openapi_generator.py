from __future__ import annotations

from typing import Any


class OpenAPIGenerator:
    """Generates OpenAPI specification documentation."""

    def __init__(self) -> None:
        self._endpoints: dict[str, dict[str, Any]] = {}

    def _key(self, method: str, path: str) -> str:
        return f"{method.upper()} {path}"

    def add_endpoint(self, method: str, path: str, spec: dict[str, Any]) -> str:
        k = self._key(method, path)
        self._endpoints[k] = {"method": method.upper(), "path": path, "spec": spec}
        return k

    def get_endpoint(self, method: str, path: str) -> dict[str, Any] | None:
        return self._endpoints.get(self._key(method, path))

    def remove_endpoint(self, method: str, path: str) -> bool:
        k = self._key(method, path)
        if k in self._endpoints:
            del self._endpoints[k]
            return True
        return False

    @property
    def endpoint_count(self) -> int:
        return len(self._endpoints)

    def generate_spec(self) -> str:
        lines: list[str] = ["OpenAPI Specification", "=====================", ""]
        for ep in self._endpoints.values():
            lines.append(f"{ep['method']} {ep['path']}")
            for k, v in ep["spec"].items():
                lines.append(f"  {k}: {v}")
            lines.append("")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        return {
            "endpoints": list(self._endpoints.values()),
            "endpoint_count": self.endpoint_count,
        }
