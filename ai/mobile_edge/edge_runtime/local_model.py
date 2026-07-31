"""Local Model - Edge model management."""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import hashlib


class LocalModelStatus(Enum):
    AVAILABLE = "available"
    LOADED = "loaded"
    RUNNING = "running"
    UNLOADED = "unloaded"
    ERROR = "error"


@dataclass
class LocalModel:
    model_id: str
    name: str
    version: str = "1.0"
    size_mb: float = 0.0
    status: LocalModelStatus = LocalModelStatus.AVAILABLE
    accuracy: float = 0.0
    loaded_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class LocalModelManager:
    def __init__(self):
        self.models: Dict[str, LocalModel] = {}
        self.load_order: List[str] = []

    def register(self, name: str, version: str = "1.0", size_mb: float = 0.0) -> LocalModel:
        model_id = hashlib.sha256(f"{name}{version}".encode()).hexdigest()[:16]
        model = LocalModel(model_id=model_id, name=name, version=version, size_mb=size_mb)
        self.models[model_id] = model
        return model

    def load(self, model_id: str) -> bool:
        model = self.models.get(model_id)
        if model:
            model.status = LocalModelStatus.LOADED
            model.loaded_at = datetime.now()
            self.load_order.append(model_id)
            return True
        return False

    def unload(self, model_id: str) -> bool:
        model = self.models.get(model_id)
        if model:
            model.status = LocalModelStatus.UNLOADED
            return True
        return False

    def get(self, model_id: str) -> Optional[LocalModel]:
        return self.models.get(model_id)

    def list_models(self, status: LocalModelStatus = None) -> List[LocalModel]:
        if status:
            return [m for m in self.models.values() if m.status == status]
        return list(self.models.values())

    def get_total_size(self) -> float:
        return sum(m.size_mb for m in self.models.values())

    def count(self) -> int:
        return len(self.models)
