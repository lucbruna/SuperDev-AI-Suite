from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from runtime_engine.sandbox.sandbox_permissions import SandboxPermissions
from runtime_engine.sandbox.sandbox_limits import SandboxLimits


class RuntimeContext(BaseModel):
    session_id: str
    work_dir: str | None = None
    env_vars: dict[str, str] = Field(default_factory=dict)
    timeout: int = 30
    resource_limits: SandboxLimits = Field(default_factory=SandboxLimits)
    permissions: SandboxPermissions = Field(default_factory=SandboxPermissions)
    metadata: dict[str, Any] = Field(default_factory=dict)
    language: str = "python"

    def ensure_work_dir(self) -> Path:
        path = Path(self.work_dir) if self.work_dir else Path.cwd() / ".runtime" / self.session_id
        path.mkdir(parents=True, exist_ok=True)
        self.work_dir = str(path)
        return path
