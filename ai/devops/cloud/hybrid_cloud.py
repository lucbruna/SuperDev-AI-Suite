"""Hybrid cloud manager."""

from __future__ import annotations

from typing import Any


class HybridCloudManager:
    def __init__(self) -> None:
        self._providers: dict[str, Any] = {}
        self._workloads: dict[str, dict[str, Any]] = {}

    def register_provider(self, name: str, provider: Any) -> dict[str, Any]:
        self._providers[name] = provider
        return {"name": name, "registered": True}

    def distribute_workload(self, workload_name: str, distribution: dict[str, str]) -> dict[str, Any]:
        workload = {"name": workload_name, "distribution": distribution}
        self._workloads[workload_name] = workload
        return workload

    def list_providers(self) -> list[str]:
        return list(self._providers.keys())

    def list_workloads(self) -> list[dict[str, Any]]:
        return list(self._workloads.values())

    def count(self) -> int:
        return len(self._workloads)
