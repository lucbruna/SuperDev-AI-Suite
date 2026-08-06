"""Connector base: detection, contract and graceful degradation."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Callable

Handler = Callable[..., dict[str, Any]]


@dataclass(frozen=True, slots=True)
class ConnectorInfo:
    """Static description of a connector."""

    name: str
    display: str
    tools: tuple[str, ...]
    available: bool
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["tools"] = list(self.tools)
        return data


@dataclass(slots=True)
class Connector:
    """A graceful connector to a sibling module or toolchain capability.

    ``available`` is determined at construction (module importable via
    ``find_spec``, binary on PATH, ...). Calls never raise: when a connector
    is unavailable or has no handler, ``execute`` returns a structured
    degradation result instead.
    """

    name: str
    display: str
    tools: tuple[str, ...]
    available: bool
    note: str = ""
    handler: Handler | None = None

    def info(self) -> ConnectorInfo:
        return ConnectorInfo(
            name=self.name,
            display=self.display,
            tools=self.tools,
            available=self.available,
            note=self.note,
        )

    def to_dict(self) -> dict[str, Any]:
        return self.info().to_dict()

    def execute(self, action: str = "invoke", **kwargs: Any) -> dict[str, Any]:
        """Run an action on this connector, degrading gracefully.

        Returns:
            ``{"available": False, ...}`` when the connector is unavailable;
            ``{"available": True, "status": "delegated", ...}`` when the
            orchestrator delegates to the sibling capability (no handler);
            otherwise the handler's structured result.
        """
        if not self.available:
            return {
                "available": False,
                "connector": self.name,
                "action": action,
                "status": "unavailable",
                "note": self.note,
            }
        if self.handler is None:
            return {
                "available": True,
                "connector": self.name,
                "action": action,
                "status": "delegated",
                "note": f"delegated to {self.display}; no in-process handler",
            }
        try:
            result: dict[str, Any] = self.handler(action=action, **kwargs)
            if not isinstance(result, dict):
                result = {"result": result}
            if "available" not in result:
                result["available"] = True
            if "connector" not in result:
                result["connector"] = self.name
            if "action" not in result:
                result["action"] = action
            return result
        except Exception as exc:  # never let a connector break the pipeline
            return {
                "available": True,
                "connector": self.name,
                "action": action,
                "status": "error",
                "error": str(exc),
            }
