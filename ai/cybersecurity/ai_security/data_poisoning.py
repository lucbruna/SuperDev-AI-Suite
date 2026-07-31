"""
Training Data Poisoning Defense
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import hashlib
import statistics


class PoisoningType(Enum):
    LABEL_FLIP = "label_flip"
    DATA_INSERTION = "data_insertion"
    BACKDOOR = "backdoor"
    GRADIENT_BASED = "gradient_based"
    CLEAN_LABEL = "clean_label"


@dataclass
class DataPoint:
    data_id: str
    content_hash: str
    label: str = ""
    source: str = ""
    added_at: datetime = field(default_factory=datetime.now)
    verified: bool = False


@dataclass
class AnomalyResult:
    data_id: str
    is_anomalous: bool
    anomaly_score: float = 0.0
    reason: str = ""
    poisoning_type: Optional[PoisoningType] = None


@dataclass
class DataLineage:
    data_id: str
    source: str
    transforms: List[str] = field(default_factory=list)
    parent_ids: List[str] = field(default_factory=list)
    verified: bool = False


class DataPoisoningDefense:
    def __init__(self):
        self.data_points: Dict[str, DataPoint] = {}
        self.lineage: Dict[str, DataLineage] = {}
        self.anomaly_log: List[AnomalyResult] = []
        self.baseline_stats: Dict[str, float] = {}

    def register_data(self, data_id: str, content: str, label: str = "", source: str = "") -> DataPoint:
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        dp = DataPoint(data_id=data_id, content_hash=content_hash, label=label, source=source, verified=True)
        self.data_points[data_id] = dp
        return dp

    def detect_anomaly(self, data_id: str, features: Dict[str, float]) -> AnomalyResult:
        is_anomalous = False
        reasons = []
        anomaly_score = 0.0
        for key, value in features.items():
            baseline_mean = self.baseline_stats.get(f"{key}_mean", 0)
            baseline_std = self.baseline_stats.get(f"{key}_std", 1)
            if baseline_std > 0:
                z_score = abs(value - baseline_mean) / baseline_std
                if z_score > 3:
                    is_anomalous = True
                    anomaly_score = max(anomaly_score, z_score / 10)
                    reasons.append(f"z_score_{key}_{z_score:.1f}")
        result = AnomalyResult(data_id=data_id, is_anomalous=is_anomalous, anomaly_score=anomaly_score, reason="; ".join(reasons))
        self.anomaly_log.append(result)
        return result

    def update_baseline(self, feature_name: str, values: List[float]) -> None:
        if values:
            self.baseline_stats[f"{feature_name}_mean"] = statistics.mean(values)
            self.baseline_stats[f"{feature_name}_std"] = statistics.stdev(values) if len(values) > 1 else 1.0

    def add_lineage(self, data_id: str, source: str, transforms: List[str] = None, parent_ids: List[str] = None) -> DataLineage:
        lineage = DataLineage(data_id=data_id, source=source, transforms=transforms or [], parent_ids=parent_ids or [])
        self.lineage[data_id] = lineage
        return lineage

    def verify_lineage(self, data_id: str) -> bool:
        lineage = self.lineage.get(data_id)
        if lineage:
            lineage.verified = True
            return True
        return False

    def get_anomalies(self) -> List[AnomalyResult]:
        return [a for a in self.anomaly_log if a.is_anomalous]

    def get_lineage(self, data_id: str) -> Optional[DataLineage]:
        return self.lineage.get(data_id)

    def count(self) -> int:
        return len(self.data_points)
