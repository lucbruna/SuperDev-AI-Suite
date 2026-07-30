from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class WorkflowConfig:
    max_concurrent_steps: int = 10
    default_timeout: float = 300.0
    max_retries: int = 3
    history_size: int = 1000
    enable_metrics: bool = True
    enable_audit: bool = True
    storage_backend: str = "memory"
    db_path: str = "workflow.db"
    auto_resume: bool = True
    notify_on_failure: bool = True
    tags: list[str] = field(default_factory=list)
