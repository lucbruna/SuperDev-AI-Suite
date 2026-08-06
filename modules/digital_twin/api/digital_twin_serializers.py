"""Serializers converting core results into JSON-safe dicts."""
from __future__ import annotations

from modules.digital_twin.core.digital_twin_engine import EngineResult
from modules.digital_twin.core.digital_twin_kernel import KernelStatus
from modules.digital_twin.core.digital_twin_manager import ManagerState


class TwinSerializers:
    """Static serializers for core result objects."""

    @staticmethod
    def engine_result(result: EngineResult) -> dict[str, object]:
        return result.to_dict()

    @staticmethod
    def manager_state(state: ManagerState) -> dict[str, object]:
        return state.to_dict()

    @staticmethod
    def kernel_status(status: KernelStatus) -> dict[str, object]:
        return status.to_dict()

    @staticmethod
    def config(cfg) -> dict[str, object]:
        return {
            "name": cfg.name,
            "enabled": cfg.enabled,
            "snapshot_retention": cfg.snapshot_retention,
            "sync_interval_seconds": cfg.sync.interval_seconds,
            "simulation_enabled": cfg.simulation.enabled,
            "prediction_enabled": cfg.prediction.enabled,
            "monitoring_enabled": cfg.monitoring.enabled,
        }
