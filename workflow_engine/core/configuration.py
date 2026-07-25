from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class RetryMode(StrEnum):
    FIXED = "fixed"
    EXPONENTIAL = "exponential"
    LINEAR = "linear"


class RetryPolicy(BaseModel):
    max_retries: int = 3
    delay: float = 1.0
    backoff_factor: float = 2.0
    max_delay: float = 60.0
    retry_mode: RetryMode = RetryMode.EXPONENTIAL
    retry_on: list[str] = Field(default_factory=lambda: ["*"])


class WorkflowConfig(BaseModel):
    max_nodes: int = 100
    max_depth: int = 20
    default_timeout: float = 300.0
    retry_policy: RetryPolicy = Field(default_factory=RetryPolicy)
    checkpoint_enabled: bool = True
    parallel_execution: bool = True
