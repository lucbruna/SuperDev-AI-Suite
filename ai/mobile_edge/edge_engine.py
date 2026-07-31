"""Edge AI Runtime Engine - Local AI processing on edge devices."""
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import hashlib


class ModelStatus(Enum):
    LOADED = "loaded"
    UNLOADED = "unloaded"
    LOADING = "loading"
    ERROR = "error"


class AcceleratorType(Enum):
    CPU = "cpu"
    GPU = "gpu"
    NPU = "npu"
    TPU = "tpu"
    DSP = "dsp"


@dataclass
class EdgeModel:
    model_id: str
    name: str
    version: str = "1.0"
    size_mb: float = 0.0
    status: ModelStatus = ModelStatus.UNLOADED
    accelerator: AcceleratorType = AcceleratorType.CPU
    input_shape: List[int] = field(default_factory=list)
    output_shape: List[int] = field(default_factory=list)
    accuracy: float = 0.0
    loaded_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InferenceResult:
    result_id: str
    model_id: str
    input_data: Any = None
    output_data: Any = None
    confidence: float = 0.0
    latency_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


class EdgeEngine:
    def __init__(self):
        self.models: Dict[str, EdgeModel] = {}
        self.inference_cache: Dict[str, InferenceResult] = {}
        self.inference_log: List[InferenceResult] = []
        self.handlers: Dict[str, Callable] = {}

    def register_model(self, name: str, version: str = "1.0", size_mb: float = 0.0, accelerator: AcceleratorType = AcceleratorType.CPU) -> EdgeModel:
        model_id = hashlib.sha256(f"{name}{version}".encode()).hexdigest()[:16]
        model = EdgeModel(model_id=model_id, name=name, version=version, size_mb=size_mb, accelerator=accelerator)
        self.models[model_id] = model
        return model

    def load_model(self, model_id: str) -> bool:
        model = self.models.get(model_id)
        if not model:
            return False
        model.status = ModelStatus.LOADING
        handler = self.handlers.get(model_id)
        if handler:
            try:
                handler("load", model)
                model.status = ModelStatus.LOADED
                model.loaded_at = datetime.now()
                return True
            except Exception:
                model.status = ModelStatus.ERROR
                return False
        model.status = ModelStatus.LOADED
        model.loaded_at = datetime.now()
        return True

    def unload_model(self, model_id: str) -> bool:
        model = self.models.get(model_id)
        if model:
            model.status = ModelStatus.UNLOADED
            return True
        return False

    def register_handler(self, model_id: str, handler: Callable) -> None:
        self.handlers[model_id] = handler

    def infer(self, model_id: str, input_data: Any) -> Optional[InferenceResult]:
        model = self.models.get(model_id)
        if not model or model.status != ModelStatus.LOADED:
            return None
        handler = self.handlers.get(model_id)
        result_id = hashlib.sha256(f"{model_id}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        if handler:
            try:
                output = handler("infer", input_data)
                result = InferenceResult(result_id=result_id, model_id=model_id, input_data=input_data, output_data=output, confidence=0.95, latency_ms=10.0)
            except Exception:
                return None
        else:
            result = InferenceResult(result_id=result_id, model_id=model_id, input_data=input_data, output_data=input_data, confidence=0.0)
        self.inference_log.append(result)
        self.inference_cache[result_id] = result
        return result

    def get_model(self, model_id: str) -> Optional[EdgeModel]:
        return self.models.get(model_id)

    def list_models(self, status: ModelStatus = None) -> List[EdgeModel]:
        if status:
            return [m for m in self.models.values() if m.status == status]
        return list(self.models.values())

    def get_loaded_models(self) -> List[EdgeModel]:
        return self.list_models(status=ModelStatus.LOADED)

    def get_inference_log(self, limit: int = 100) -> List[InferenceResult]:
        return self.inference_log[-limit:]

    def count(self) -> int:
        return len(self.models)
