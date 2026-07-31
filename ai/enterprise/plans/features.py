"""Plan features."""
from __future__ import annotations
from typing import Any, Dict, List

class FeatureManager:
    def __init__(self) -> None:
        self._features: Dict[str, Dict[str, Any]] = {}
    def define(self, feature_id: str, name: str, description: str = "", feature_type: str = "boolean") -> Dict[str, Any]:
        feature = {"id": feature_id, "name": name, "description": description, "type": feature_type}
        self._features[feature_id] = feature
        return feature
    def get(self, feature_id: str) -> Dict[str, Any]:
        return self._features.get(feature_id, {})
    def list_all(self) -> List[Dict[str, Any]]:
        return list(self._features.values())
    def delete(self, feature_id: str) -> bool:
        if feature_id in self._features:
            del self._features[feature_id]
            return True
        return False
    def is_enabled(self, plan_features: List[str], feature_id: str) -> bool:
        return feature_id in plan_features
