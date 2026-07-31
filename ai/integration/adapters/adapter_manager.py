"""
Adapter Manager - Adapter lifecycle
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import hashlib


@dataclass
class AdapterInfo:
    adapter_id: str
    name: str
    adapter_type: str
    source_format: str
    target_format: str
    status: str = "active"
    created_at: datetime = field(default_factory=datetime.now)
    use_count: int = 0


class AdapterManager:
    def __init__(self):
        self.adapters: Dict[str, AdapterInfo] = {}

    def register(self, name: str, adapter_type: str, source_format: str, target_format: str) -> AdapterInfo:
        adapter_id = hashlib.sha256(f"{name}{adapter_type}".encode()).hexdigest()[:16]
        info = AdapterInfo(adapter_id=adapter_id, name=name, adapter_type=adapter_type, source_format=source_format, target_format=target_format)
        self.adapters[adapter_id] = info
        return info

    def unregister(self, adapter_id: str) -> bool:
        if adapter_id in self.adapters:
            del self.adapters[adapter_id]
            return True
        return False

    def get_adapter(self, adapter_id: str) -> Optional[AdapterInfo]:
        return self.adapters.get(adapter_id)

    def find_by_formats(self, source: str, target: str) -> List[AdapterInfo]:
        return [a for a in self.adapters.values() if a.source_format == source and a.target_format == target]

    def list_all(self) -> List[AdapterInfo]:
        return list(self.adapters.values())

    def count(self) -> int:
        return len(self.adapters)
