from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class ModelInfo:
    model_id: str
    name: str
    dimension: int
    model_type: str
    loaded: bool = False
    loaded_at: Optional[float] = None


class ModelManager:
    def __init__(self) -> None:
        self._models: dict[str, ModelInfo] = {}
        self._active_model_id: Optional[str] = None

    def load_model(self, name: str, dimension: int = 128, model_type: str = "mock") -> ModelInfo:
        model_id = str(uuid.uuid4())
        info = ModelInfo(
            model_id=model_id,
            name=name,
            dimension=dimension,
            model_type=model_type,
            loaded=True,
            loaded_at=time.time(),
        )
        self._models[model_id] = info
        self._active_model_id = model_id
        return info

    def unload_model(self, model_id: str) -> bool:
        if model_id not in self._models:
            return False
        self._models[model_id].loaded = False
        self._models[model_id].loaded_at = None
        if self._active_model_id == model_id:
            self._active_model_id = None
        return True

    def list_models(self) -> list[ModelInfo]:
        return list(self._models.values())

    def get_model_info(self, model_id: str) -> Optional[ModelInfo]:
        return self._models.get(model_id)

    def switch_model(self, model_id: str) -> bool:
        if model_id not in self._models:
            return False
        if not self._models[model_id].loaded:
            self._models[model_id].loaded = True
            self._models[model_id].loaded_at = time.time()
        self._active_model_id = model_id
        return True

    def get_active_model(self) -> Optional[ModelInfo]:
        if self._active_model_id is None:
            return None
        return self._models.get(self._active_model_id)
