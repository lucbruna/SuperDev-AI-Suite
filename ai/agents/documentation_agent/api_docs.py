from __future__ import annotations

from typing import Any


class APIDocs:
    """Generates API endpoint documentation."""

    def __init__(self) -> None:
        self._endpoints: dict[str, dict[str, Any]] = {}

    def _key(self, method: str, path: str) -> str:
        return f"{method.upper()} {path}"

    def add_endpoint(self, method: str, path: str, params: list[dict[str, Any]]) -> str:
        k = self._key(method, path)
        self._endpoints[k] = {"method": method.upper(), "path": path, "params": params}
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

    def generate_docs(self) -> str:
        lines: list[str] = ["# API Documentation", ""]
        for ep in self._endpoints.values():
            lines.append(f"## {ep['method']} {ep['path']}")
            for param in ep["params"]:
                name = param.get("name", "?")
                ptype = param.get("type", "string")
                desc = param.get("description", "")
                required = param.get("required", False)
                req_str = "required" if required else "optional"
                lines.append(f"- `{name}` ({ptype}, {req_str}): {desc}")
            lines.append("")
        return "\n".join(lines).strip()

    def to_dict(self) -> dict[str, Any]:
        return {
            "endpoints": list(self._endpoints.values()),
            "endpoint_count": self.endpoint_count,
        }
