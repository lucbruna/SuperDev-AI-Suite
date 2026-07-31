"""Hybrid cloud manager."""
from __future__ import annotations
from typing import Any, Dict, List

class HybridCloudManager:
    def __init__(self) -> None:
        self._providers: Dict[str, Any] = {}
        self._workloads: Dict[str, Dict[str, Any]] = {}
    def register_provider(self, name: str, provider: Any) -> Dict[str, Any]:
        self._providers[name] = provider
        return {"name": name, "registered": True}
    def distribute_workload(self, workload_name: str, distribution: Dict[str, str]) -> Dict[str, Any]:
        workload = {"name": workload_name, "distribution": distribution}
        self._workloads[workload_name] = workload
        return workload
    def list_providers(self) -> List[str]:
        return list(self._providers.keys())
    def list_workloads(self) -> List[Dict[str, Any]]:
        return list(self._workloads.values())
    def count(self) -> int:
        return len(self._workloads)
