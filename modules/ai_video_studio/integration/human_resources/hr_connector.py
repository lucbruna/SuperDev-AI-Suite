"""HR Connector — facade over the human-resources generators."""
from __future__ import annotations


from modules.ai_video_studio.integration.connector_base import DomainConnector
from modules.ai_video_studio.integration.human_resources.internal_communications import (
    get_internal_communications_generator,
)
from modules.ai_video_studio.integration.human_resources.onboarding_generator import (
    get_onboarding_generator,
)
from modules.ai_video_studio.integration.human_resources.recruitment_videos import (
    get_recruitment_video_generator,
)
from modules.ai_video_studio.integration.human_resources.training_generator import (
    get_training_generator,
)


class HRConnector(DomainConnector):
    """Generates HR-domain video briefs."""

    domain = "human_resources"
    description = "Onboarding, training, internal communications and recruitment videos"

    def __init__(self) -> None:
        super().__init__()
        self._register("onboarding_video", lambda d: get_onboarding_generator().generate(**d))
        self._register("training_video", lambda d: get_training_generator().generate(**d))
        self._register("internal_communication", lambda d: get_internal_communications_generator().generate(**d))
        self._register("recruitment_video", lambda d: get_recruitment_video_generator().generate(**d))


_hr_connector: HRConnector | None = None


def get_hr_connector() -> HRConnector:
    global _hr_connector
    if _hr_connector is None:
        _hr_connector = HRConnector()
    return _hr_connector
