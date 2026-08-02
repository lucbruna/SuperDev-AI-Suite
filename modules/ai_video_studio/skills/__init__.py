"""Skills package — blueprint Volume 11 core (AI Skills Framework).

Self-contained skill system: definitions, registry, loader, validator,
runtime with timeout, permissions, security allowlist, lifecycle
(install/update/uninstall), marketplace, scheduler, statistics and a
manager facade. Lifecycle and execution events are published onto the
Vol 10 integration event bus, and activity is logged through the Vol 10
integration logger. Concrete, service-backed skills ship in ``video`` and
``voice`` bundles and are registered via ``bundles.register_all_concrete``.
"""
from __future__ import annotations

from modules.ai_video_studio.skills.bundles import (
    CONCRETE_SKILL_CLASSES,
    register_all_concrete,
)
from modules.ai_video_studio.skills.skill_engine import (
    SkillEngine,
    SkillNotFoundError,
    get_skill_engine,
)
from modules.ai_video_studio.skills.skill_installer import (
    SkillInstallError,
    SkillInstaller,
    get_skill_installer,
)
from modules.ai_video_studio.skills.skill_loader import load
from modules.ai_video_studio.skills.skill_manager import SkillManager, get_skill_manager
from modules.ai_video_studio.skills.skill_marketplace import (
    MarketplaceEntry,
    SkillMarketplace,
    get_skill_marketplace,
)
from modules.ai_video_studio.skills.skill_permissions import (
    PermissionDeniedError,
    SkillPermissions,
    get_skill_permissions,
)
from modules.ai_video_studio.skills.skill_registry import (
    SkillDefinition,
    SkillRegistry,
    get_skill_registry,
)
from modules.ai_video_studio.skills.skill_runtime import (
    SkillResult,
    SkillRuntime,
    get_skill_runtime,
)
from modules.ai_video_studio.skills.skill_scheduler import (
    SkillScheduler,
    get_skill_scheduler,
)
from modules.ai_video_studio.skills.skill_security import (
    SkillBlockedError,
    SkillSecurity,
    get_skill_security,
)
from modules.ai_video_studio.skills.skill_statistics import (
    SkillStatistics,
    get_skill_statistics,
)
from modules.ai_video_studio.skills.skill_updater import (
    SkillUpdateError,
    SkillUpdater,
    get_skill_updater,
)
from modules.ai_video_studio.skills.skill_validator import (
    SkillValidationError,
    assert_valid,
    is_valid,
    validate,
)

__all__ = [
    "CONCRETE_SKILL_CLASSES",
    "register_all_concrete",
    "SkillEngine",
    "SkillNotFoundError",
    "get_skill_engine",
    "SkillInstallError",
    "SkillInstaller",
    "get_skill_installer",
    "load",
    "SkillManager",
    "get_skill_manager",
    "MarketplaceEntry",
    "SkillMarketplace",
    "get_skill_marketplace",
    "PermissionDeniedError",
    "SkillPermissions",
    "get_skill_permissions",
    "SkillDefinition",
    "SkillRegistry",
    "get_skill_registry",
    "SkillResult",
    "SkillRuntime",
    "get_skill_runtime",
    "SkillScheduler",
    "get_skill_scheduler",
    "SkillBlockedError",
    "SkillSecurity",
    "get_skill_security",
    "SkillStatistics",
    "get_skill_statistics",
    "SkillUpdateError",
    "SkillUpdater",
    "get_skill_updater",
    "SkillValidationError",
    "assert_valid",
    "is_valid",
    "validate",
]
