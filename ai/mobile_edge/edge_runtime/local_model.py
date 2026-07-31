"""Local Model - Edge model management."""
import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


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
    loaded_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class LocalModelManager:
    def __init__(self):
        self.models: dict[str, LocalModel] = {}
        self.load_order: list[str] = []

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

    def get(self, model_id: str) -> LocalModel | None:
        return self.models.get(model_id)

    def list_models(self, status: LocalModelStatus = None) -> list[LocalModel]:
        if status:
            return [m for m in self.models.values() if m.status == status]
        return list(self.models.values())

    def get_total_size(self) -> float:
        return sum(m.size_mb for m in self.models.values())

    def count(self) -> int:
        return len(self.models)
