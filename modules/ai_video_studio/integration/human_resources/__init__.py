"""Human Resources — onboarding, training, internal communications and recruitment videos."""
from modules.ai_video_studio.integration.human_resources.hr_connector import (
    HRConnector,
    get_hr_connector,
)
from modules.ai_video_studio.integration.human_resources.onboarding_generator import (
    OnboardingGenerator,
    get_onboarding_generator,
)
from modules.ai_video_studio.integration.human_resources.recruitment_videos import (
    RecruitmentVideoGenerator,
    get_recruitment_video_generator,
)

__all__ = [
    "HRConnector",
    "get_hr_connector",
    "OnboardingGenerator",
    "get_onboarding_generator",
    "RecruitmentVideoGenerator",
    "get_recruitment_video_generator",
]
