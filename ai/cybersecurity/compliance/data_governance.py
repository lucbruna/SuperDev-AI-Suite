"""
Data Governance and Classification
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class DataClassification(Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class RetentionAction(Enum):
    ARCHIVE = "archive"
    DELETE = "delete"
    ANONYMIZE = "anonymize"
    REVIEW = "review"


@dataclass
class DataAsset:
    asset_id: str
    name: str
    classification: DataClassification = DataClassification.INTERNAL
    owner: str = ""
    location: str = ""
    retention_days: int = 365
    retention_action: RetentionAction = RetentionAction.DELETE
    created_at: datetime = field(default_factory=datetime.now)
    last_reviewed: datetime | None = None
    tags: list[str] = field(default_factory=list)


@dataclass
class DataPolicy:
    policy_id: str
    classification: DataClassification
    rules: dict[str, Any] = field(default_factory=dict)
    dlp_enabled: bool = True
    encryption_required: bool = False


class DataGovernance:
    def __init__(self):
        self.assets: dict[str, DataAsset] = {}
        self.policies: dict[str, DataPolicy] = {}
        self.access_logs: list[dict[str, Any]] = []

    def register_asset(
        self, name: str, classification: DataClassification = DataClassification.INTERNAL, owner: str = "", **kwargs
    ) -> DataAsset:
        asset_id = f"asset_{len(self.assets)}"
        asset = DataAsset(asset_id=asset_id, name=name, classification=classification, owner=owner, **kwargs)
        self.assets[asset_id] = asset
        return asset

    def classify_asset(self, asset_id: str, classification: DataClassification) -> bool:
        asset = self.assets.get(asset_id)
        if asset:
            asset.classification = classification
            return True
        return False

    def add_policy(self, classification: DataClassification, rules: dict[str, Any] = None) -> DataPolicy:
        policy_id = f"dp_{classification.value}"
        policy = DataPolicy(policy_id=policy_id, classification=classification, rules=rules or {})
        self.policies[policy_id] = policy
        return policy

    def log_access(self, asset_id: str, user: str, action: str) -> None:
        self.access_logs.append(
            {"asset_id": asset_id, "user": user, "action": action, "timestamp": datetime.now().isoformat()}
        )

    def get_assets_by_classification(self, classification: DataClassification) -> list[DataAsset]:
        return [a for a in self.assets.values() if a.classification == classification]

    def get_expiring_assets(self, days: int = 30) -> list[DataAsset]:
        return list(self.assets.values())

    def get_policy(self, classification: DataClassification) -> DataPolicy | None:
        return self.policies.get(f"dp_{classification.value}")

    def get_access_logs(self, asset_id: str = None) -> list[dict[str, Any]]:
        if asset_id:
            return [l for l in self.access_logs if l["asset_id"] == asset_id]
        return self.access_logs

    def count(self) -> int:
        return len(self.assets)
