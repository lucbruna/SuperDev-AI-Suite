from pydantic import BaseModel, Field
from typing import Optional


class ObservabilityConfig(BaseModel):
    service_name: str = Field(default="superdev")
    log_level: str = Field(default="INFO")
    tracing_enabled: bool = Field(default=True)
    metrics_enabled: bool = Field(default=True)
    otlp_endpoint: Optional[str] = Field(default=None)
    sample_rate: float = Field(default=1.0, ge=0.0, le=1.0)