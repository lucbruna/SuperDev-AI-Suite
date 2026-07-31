from __future__ import annotations

import re
from typing import Any

from ..data_models import DataAsset, DataClassification, RetentionPolicy


class CatalogEngine:
    """Intelligent catalog — metadata, discovery, search, lineage, classification."""

    def __init__(self, engine: Any) -> None:
        self.engine = engine
        self.config = engine.config.catalog
        self._assets: dict[str, DataAsset] = {}
        self._search_index: dict[str, list[str]] = {}
        self._initialized = False

    async def initialize(self) -> None:
        self._initialized = True

    async def shutdown(self) -> None:
        self._initialized = False

    def register_asset(
        self,
        name: str,
        asset_type: str,
        owner: str = "",
        classification: DataClassification = DataClassification.INTERNAL,
        retention: RetentionPolicy = RetentionPolicy.KEEP,
        metadata: dict[str, Any] | None = None,
    ) -> DataAsset:
        asset = DataAsset(
            name=name,
            asset_type=asset_type,
            owner=owner,
            classification=classification,
            retention=retention,
            metadata=metadata or {},
        )
        self._assets[asset.asset_id] = asset
        self.engine.registry.register_asset(asset)
        self._index(asset)
        return asset

    def _index(self, asset: DataAsset) -> None:
        tokens = re.findall(r"[a-z0-9]+", f"{asset.name} {asset.asset_type} {asset.owner}".lower())
        for token in set(tokens):
            self._search_index.setdefault(token, []).append(asset.asset_id)

    def get_asset(self, asset_id: str) -> DataAsset | None:
        return self._assets.get(asset_id)

    def list_assets(self) -> list[DataAsset]:
        return list(self._assets.values())

    def search(self, query: str) -> list[DataAsset]:
        tokens = re.findall(r"[a-z0-9]+", query.lower())
        if not tokens:
            return []
        result_ids: set[str] | None = None
        for token in tokens:
            ids = set(self._search_index.get(token, []))
            result_ids = ids if result_ids is None else result_ids & ids
        if result_ids is None:
            return []
        return [self._assets[a] for a in result_ids if a in self._assets]

    def add_lineage(self, asset_id: str, parent_id: str) -> bool:
        asset = self._assets.get(asset_id)
        parent = self._assets.get(parent_id)
        if not asset or not parent:
            return False
        asset.lineage.append(parent_id)
        return True

    def lineage_of(self, asset_id: str) -> list[str]:
        asset = self._assets.get(asset_id)
        return list(asset.lineage) if asset else []

    def classify(self, asset_id: str, classification: DataClassification) -> bool:
        asset = self._assets.get(asset_id)
        if not asset:
            return False
        asset.classification = classification
        return True

    def discovery_summary(self) -> dict[str, Any]:
        by_type: dict[str, int] = {}
        for asset in self._assets.values():
            by_type[asset.asset_type] = by_type.get(asset.asset_type, 0) + 1
        return {
            "assets": len(self._assets),
            "by_type": by_type,
            "indexed_tokens": len(self._search_index),
        }

    def status(self) -> dict[str, Any]:
        return {
            "initialized": self._initialized,
            "assets": len(self._assets),
            "indexed_tokens": len(self._search_index),
        }


__all__ = ["CatalogEngine"]
