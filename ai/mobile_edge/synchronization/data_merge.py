"""Data Merge - Intelligent data merging."""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class MergeResult:
    merged_data: Dict[str, Any] = field(default_factory=dict)
    fields_updated: int = 0
    conflicts_found: int = 0
    timestamp: datetime = field(default_factory=datetime.now)


class DataMerger:
    def __init__(self):
        self.merge_log: List[MergeResult] = []

    def merge(self, source: Dict[str, Any], target: Dict[str, Any], strategy: str = "source_wins") -> MergeResult:
        result = MergeResult()
        merged = dict(target)
        for key, value in source.items():
            if key in target:
                if strategy == "source_wins":
                    merged[key] = value
                    result.fields_updated += 1
                elif strategy == "target_wins":
                    pass
                elif strategy == "newest":
                    merged[key] = value
                    result.fields_updated += 1
                elif strategy == "merge":
                    if isinstance(value, dict) and isinstance(target[key], dict):
                        merged[key] = {**target[key], **value}
                        result.fields_updated += 1
                    else:
                        merged[key] = value
                        result.fields_updated += 1
                result.conflicts_found += 1
            else:
                merged[key] = value
                result.fields_updated += 1
        result.merged_data = merged
        self.merge_log.append(result)
        return result

    def deep_merge(self, source: Dict[str, Any], target: Dict[str, Any]) -> Dict[str, Any]:
        result = dict(target)
        for key, value in source.items():
            if key in result and isinstance(value, dict) and isinstance(result[key], dict):
                result[key] = self.deep_merge(value, result[key])
            else:
                result[key] = value
        return result

    def get_log(self, limit: int = 100) -> List[MergeResult]:
        return self.merge_log[-limit:]
