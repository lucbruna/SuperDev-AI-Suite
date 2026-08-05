"""Concrete skill bundles — register real, service-backed skills on the engine.

Each bundle class is registered as an *instance* entrypoint so the runtime
calls ``instance(**kwargs)`` → ``__call__``, letting concrete skills keep a
plain ``__init__`` and a clean async ``__call__`` signature.
"""
from __future__ import annotations
from typing import Any

from modules.ai_video_studio.skills.skill_loader import load
from modules.ai_video_studio.skills.skill_registry import SkillDefinition
from modules.ai_video_studio.skills.ai import (
    AgentOrchestratorSkill,
    FineTunerSkill,
    LlmGatewaySkill,
    MlPipelineSkill,
    ModelEvaluatorSkill,
    PromptEngineerSkill,
    RagBuilderSkill,
)
from modules.ai_video_studio.skills.avatar import (
    DoctorSkill,
    EngineerSkill,
    FarmerSkill,
    LawyerSkill,
    PresenterSkill,
    SalespersonSkill,
    TeacherSkill,
)
from modules.ai_video_studio.skills.business import (
    BusinessPlanSkill,
    ContractDraftSkill,
    FinancialReportSkill,
    MeetingSummarySkill,
    PitchDeckSkill,
    ProposalSkill,
)
from modules.ai_video_studio.skills.development import (
    ApiBuilderSkill,
    CodeReviewerSkill,
    DebuggerSkill,
    DependencyAuditorSkill,
    DocWriterSkill,
    RefactorerSkill,
    TestWriterSkill,
)
from modules.ai_video_studio.skills.hallmark import HallmarkSkill
from modules.ai_video_studio.skills.marketing import (
    AdCopywriterSkill,
    BrandStrategySkill,
    CampaignAnalyticsSkill,
    EmailCampaignSkill,
    LandingPageSkill,
    SeoOptimizerSkill,
    SocialPlannerSkill,
)
from modules.ai_video_studio.skills.security import (
    DependencyCheckerSkill,
    PolicyWriterSkill,
    SecretsScannerSkill,
    SecurityAuditSkill,
    VulnerabilityScannerSkill,
)
from modules.ai_video_studio.skills.video import (
    AdvertisingSkill,
    AgricultureSkill,
    CinematicSkill,
    CorporateSkill,
    DocumentarySkill,
    EducationalSkill,
    MedicalSkill,
    TikTokSkill,
    YouTubeSkill,
)
from modules.ai_video_studio.skills.voice import (
    AudiobookSkill,
    DubbingSkill,
    InterviewSkill,
    NarratorSkill,
    PodcastSkill,
    StorytellerSkill,
    TranslatorSkill,
)
from modules.ai_video_studio.skills.workflow import (
    ApproverSkill,
    BackupSkill,
    NotifierSkill,
    SchedulerSkill,
    VersionerSkill,
    WorkflowOrchestratorSkill,
)

# All concrete skill classes shipped with the studio.
CONCRETE_SKILL_CLASSES: list[type] = [
    # Video (9)
    CinematicSkill,
    YouTubeSkill,
    TikTokSkill,
    DocumentarySkill,
    AdvertisingSkill,
    EducationalSkill,
    CorporateSkill,
    AgricultureSkill,
    MedicalSkill,
    # Voice (7)
    NarratorSkill,
    DubbingSkill,
    TranslatorSkill,
    PodcastSkill,
    AudiobookSkill,
    InterviewSkill,
    StorytellerSkill,
    # Avatar (7)
    PresenterSkill,
    TeacherSkill,
    DoctorSkill,
    LawyerSkill,
    FarmerSkill,
    EngineerSkill,
    SalespersonSkill,
    # Marketing (7)
    AdCopywriterSkill,
    SeoOptimizerSkill,
    SocialPlannerSkill,
    EmailCampaignSkill,
    BrandStrategySkill,
    LandingPageSkill,
    CampaignAnalyticsSkill,
    # Business (6)
    PitchDeckSkill,
    BusinessPlanSkill,
    FinancialReportSkill,
    ProposalSkill,
    MeetingSummarySkill,
    ContractDraftSkill,
    # AI (7)
    PromptEngineerSkill,
    ModelEvaluatorSkill,
    FineTunerSkill,
    RagBuilderSkill,
    AgentOrchestratorSkill,
    LlmGatewaySkill,
    MlPipelineSkill,
    # Development (7)
    CodeReviewerSkill,
    TestWriterSkill,
    ApiBuilderSkill,
    DebuggerSkill,
    RefactorerSkill,
    DocWriterSkill,
    DependencyAuditorSkill,
    # Security (5)
    VulnerabilityScannerSkill,
    SecretsScannerSkill,
    SecurityAuditSkill,
    DependencyCheckerSkill,
    PolicyWriterSkill,
    # Workflow (6)
    WorkflowOrchestratorSkill,
    NotifierSkill,
    SchedulerSkill,
    ApproverSkill,
    VersionerSkill,
    BackupSkill,
    # Hallmark (1)
    HallmarkSkill,
]


def _definition_with_instance(cls: type) -> SkillDefinition:
    """Build a definition whose entrypoint is a fresh instance of ``cls``."""
    definition = load(cls)
    return SkillDefinition(
        id=definition.id,
        name=definition.name,
        version=definition.version,
        description=definition.description,
        category=definition.category,
        entrypoint=cls(),
        permissions=definition.permissions,
        tags=definition.tags,
        metadata=definition.metadata,
    )


def register_all_concrete(
    engine: Any,
    *,
    categories: tuple[str, ...] | None = None,
) -> dict[str, bool]:
    """Register every concrete skill (optionally filtered by category) on ``engine``.

    Returns a mapping of ``skill_id -> registered``.
    """
    results: dict[str, bool] = {}
    for cls in CONCRETE_SKILL_CLASSES:
        category = getattr(cls, "skill_category", "general")
        if categories and category not in categories:
            continue
        engine.register(_definition_with_instance(cls))
        results[getattr(cls, "skill_id", cls.__name__.lower())] = True
    return results
