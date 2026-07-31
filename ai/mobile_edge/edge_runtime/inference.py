"""Inference - Local inference engine."""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import hashlib


@dataclass
class InferenceRequest:
    request_id: str
    model_id: str
    input_data: Any = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class InferenceResponse:
    request_id: str
    model_id: str
    output_data: Any = None
    confidence: float = 0.0
    latency_ms: float = 0.0
    success: bool = True
    error: str = ""


class InferenceEngine:
    def __init__(self):
        self.requests: List[InferenceRequest] = []
        self.responses: List[InferenceResponse] = []
        self.handlers: Dict[str, Any] = {}

    def submit(self, model_id: str, input_data: Any, parameters: Dict[str, Any] = None) -> InferenceRequest:
        request_id = hashlib.sha256(f"{model_id}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        request = InferenceRequest(request_id=request_id, model_id=model_id, input_data=input_data, parameters=parameters or {})
        self.requests.append(request)
        return request

    def process(self, request: InferenceRequest) -> InferenceResponse:
        handler = self.handlers.get(request.model_id)
        if handler:
            try:
                output = handler(request.input_data)
                response = InferenceResponse(request_id=request.request_id, model_id=request.model_id, output_data=output, confidence=0.95, latency_ms=5.0)
            except Exception as e:
                response = InferenceResponse(request_id=request.request_id, model_id=request.model_id, success=False, error=str(e))
        else:
            response = InferenceResponse(request_id=request.request_id, model_id=request.model_id, output_data=request.input_data, confidence=0.0)
        self.responses.append(response)
        return response

    def register_handler(self, model_id: str, handler) -> None:
        self.handlers[model_id] = handler

    def get_response(self, request_id: str) -> Optional[InferenceResponse]:
        for r in self.responses:
            if r.request_id == request_id:
                return r
        return None

    def get_history(self, limit: int = 100) -> List[InferenceResponse]:
        return self.responses[-limit:]

    def count(self) -> int:
        return len(self.responses)
