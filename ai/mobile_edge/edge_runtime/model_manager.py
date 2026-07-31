"""Model Manager - Edge model lifecycle management."""
import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ModelLifecycle(Enum):
    DOWNLOADING = "downloading"
    READY = "ready"
    ACTIVE = "active"
    UPDATE_PENDING = "update_pending"
    RETIRED = "retired"


@dataclass
class ManagedModel:
    model_id: str
    name: str
    lifecycle: ModelLifecycle = ModelLifecycle.READY
    version: str = "1.0"
    download_url: str = ""
    checksum: str = ""
    downloaded_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class EdgeModelManager:
    def __init__(self):
        self.models: dict[str, ManagedModel] = {}
        self.download_queue: list[str] = []

    def add_model(self, name: str, version: str = "1.0", download_url: str = "") -> ManagedModel:
        model_id = hashlib.sha256(f"{name}{version}".encode()).hexdigest()[:16]
        model = ManagedModel(model_id=model_id, name=name, version=version, download_url=download_url)
        self.models[model_id] = model
        return model

    def queue_download(self, model_id: str) -> bool:
        if model_id in self.models:
            self.download_queue.append(model_id)
            self.models[model_id].lifecycle = ModelLifecycle.DOWNLOADING
            return True
        return False

    def complete_download(self, model_id: str) -> bool:
        model = self.models.get(model_id)
        if model:
            model.lifecycle = ModelLifecycle.READY
            model.downloaded_at = datetime.now()
            return True
        return False

    def activate(self, model_id: str) -> bool:
        model = self.models.get(model_id)
        if model:
            model.lifecycle = ModelLifecycle.ACTIVE
            return True
        return False

    def retire(self, model_id: str) -> bool:
        model = self.models.get(model_id)
        if model:
            model.lifecycle = ModelLifecycle.RETIRED
            return True
        return False

    def get(self, model_id: str) -> ManagedModel | None:
        return self.models.get(model_id)

    def list_models(self, lifecycle: ModelLifecycle = None) -> list[ManagedModel]:
        if lifecycle:
            return [m for m in self.models.values() if m.lifecycle == lifecycle]
        return list(self.models.values())

    def count(self) -> int:
        return len(self.models)
