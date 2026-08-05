"""Suite Integration — Volume 10: the AI Video Studio as a native module.

Connects the studio to the existing SuperDev platform instead of
duplicating it:

* ``integration``  → register the studio in the suite Integration & API Engine
* ``auth``         → reuse the platform JWT manager for token verification
* ``security``     → reuse the suite SSRF guards for URL validation
* ``observability``→ report the suite MonitoringEngine health, record metrics
* ``plugins``      → expose the studio's official plugins
* ``workflow``     → register studio pipelines as suite workflows

Every adapter reuses the platform component when importable and falls back
to a local equivalent otherwise — the studio never breaks and never
re-implements platform functionality.
"""
from modules.ai_video_studio.suite_integration.suite_bridge import (
    SuiteBridge,
    get_suite_bridge,
)
from modules.ai_video_studio.suite_integration.suite_manifest import (
    SUITE_MANIFEST,
    SuiteManifest,
)

__all__ = [
    "SuiteBridge",
    "get_suite_bridge",
    "SuiteManifest",
    "SUITE_MANIFEST",
]
