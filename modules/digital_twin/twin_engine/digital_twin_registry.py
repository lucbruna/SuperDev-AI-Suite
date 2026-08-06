"""Registry of named twins for the Digital Twin module."""
from __future__ import annotations

from modules.digital_twin.core.digital_twin_registry import TwinRegistryError
from modules.digital_twin.twin_engine.digital_twin_builder import TwinModel
from modules.digital_twin.twin_engine.digital_twin_snapshot import (
    TwinSnapshot,
    TwinSnapshotter,
)


class TwinModelRegistry:
    """Stores named twins and their snapshot history.

    Fresh per instance — never shared across tests or runtimes.
    """

    def __init__(self) -> None:
        self._twins: dict[str, TwinModel] = {}
        self._snapshots: dict[str, list[TwinSnapshot]] = {}
        self._snapshotter = TwinSnapshotter()

    def register(self, model: TwinModel, *, overwrite: bool = False) -> None:
        if model.name in self._twins and not overwrite:
            raise TwinRegistryError(f"twin already registered: {model.name}")
        self._twins[model.name] = model

    def get(self, name: str) -> TwinModel:
        try:
            return self._twins[name]
        except KeyError:
            raise TwinRegistryError(f"twin not found: {name}") from None

    def has(self, name: str) -> bool:
        return name in self._twins

    def names(self) -> list[str]:
        return sorted(self._twins)

    def unregister(self, name: str) -> None:
        self._twins.pop(name, None)
        self._snapshots.pop(name, None)

    def clear(self) -> None:
        self._twins.clear()
        self._snapshots.clear()

    def snapshot(self, name: str) -> TwinSnapshot:
        model = self.get(name)
        snap = self._snapshotter.capture(model)
        self._snapshots.setdefault(name, []).append(snap)
        return snap

    def snapshots(self, name: str) -> list[TwinSnapshot]:
        return list(self._snapshots.get(name, []))

    def latest_snapshot(self, name: str) -> TwinSnapshot | None:
        snaps = self._snapshots.get(name, [])
        return snaps[-1] if snaps else None

    def __len__(self) -> int:
        return len(self._twins)
