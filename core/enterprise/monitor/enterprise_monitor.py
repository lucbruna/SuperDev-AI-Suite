from typing import Any, Dict, List, Optional

from core.enterprise.monitor.engine_adapters import (
    CustomerAdapter,
    DecisionCenterAdapter,
    EngineAdapter,
    FinancialAdapter,
    HRAdapter,
    KnowledgeAdapter,
    LegalAdapter,
    MultimodalAdapter,
    PhysicalAdapter,
    SupplyChainAdapter,
)


class EnterpriseMonitor:
    def __init__(self, config: Optional[Dict] = None) -> None:
        self._config = config or {}
        self._adapters: List[EngineAdapter] = [
            SupplyChainAdapter(),
            FinancialAdapter(),
            HRAdapter(),
            LegalAdapter(),
            CustomerAdapter(),
            DecisionCenterAdapter(),
            PhysicalAdapter(),
            MultimodalAdapter(),
            KnowledgeAdapter(),
        ]

    async def initialize(self) -> None:
        for adapter in self._adapters:
            await adapter.initialize()

    async def shutdown(self) -> None:
        for adapter in self._adapters:
            await adapter.shutdown()

    async def get_enterprise_health(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for adapter in self._adapters:
            result[adapter.get_adapter_name()] = adapter.get_health()
        return result

    async def get_enterprise_kpis(self) -> Dict[str, Dict[str, Any]]:
        result: Dict[str, Dict[str, Any]] = {}
        for adapter in self._adapters:
            result[adapter.get_adapter_name()] = adapter.extract_kpis()
        return result

    async def get_enterprise_summary(self) -> Dict[str, Any]:
        health = await self.get_enterprise_health()
        kpis = await self.get_enterprise_kpis()

        total_engines = len(self._adapters)
        healthy_count = sum(
            1 for h in health.values() if h.get("healthy", False)
        )
        total_kpis = sum(len(k) for k in kpis.values())

        return {
            "total_engines": total_engines,
            "healthy_engines": healthy_count,
            "unhealthy_engines": total_engines - healthy_count,
            "all_healthy": healthy_count == total_engines,
            "total_kpis": total_kpis,
            "engine_names": self.get_engine_names(),
        }

    async def get_unified_dashboard(self) -> Dict[str, Any]:
        health = await self.get_enterprise_health()
        kpis = await self.get_enterprise_kpis()
        summary = await self.get_enterprise_summary()

        return {
            "health": health,
            "kpis": kpis,
            "summary": summary,
        }

    def get_engine_names(self) -> List[str]:
        return [adapter.get_adapter_name() for adapter in self._adapters]

    def is_healthy(self) -> bool:
        return all(
            adapter.get_health().get("healthy", False)
            for adapter in self._adapters
        )
