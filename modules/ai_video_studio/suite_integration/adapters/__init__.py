"""Suite adapters — one adapter per platform service the studio reuses."""
from __future__ import annotations

from modules.ai_video_studio.suite_integration.adapters.auth_adapter import AuthAdapter
from modules.ai_video_studio.suite_integration.adapters.base import SuiteAdapter
from modules.ai_video_studio.suite_integration.adapters.integration_adapter import (
    IntegrationAdapter,
)
from modules.ai_video_studio.suite_integration.adapters.observability_adapter import (
    ObservabilityAdapter,
)
from modules.ai_video_studio.suite_integration.adapters.plugin_adapter import PluginAdapter
from modules.ai_video_studio.suite_integration.adapters.security_adapter import (
    SecurityAdapter,
)
from modules.ai_video_studio.suite_integration.adapters.workflow_adapter import (
    WorkflowAdapter,
)

__all__ = [
    "SuiteAdapter",
    "AuthAdapter",
    "SecurityAdapter",
    "ObservabilityAdapter",
    "PluginAdapter",
    "WorkflowAdapter",
    "IntegrationAdapter",
    "get_adapters",
]


def get_adapters() -> list[SuiteAdapter]:
    """All platform adapters (order matters for the bridge report)."""
    return [
        IntegrationAdapter(),
        AuthAdapter(),
        SecurityAdapter(),
        ObservabilityAdapter(),
        PluginAdapter(),
        WorkflowAdapter(),
    ]
