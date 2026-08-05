"""CRM Connector — facade over the CRM generators."""
from __future__ import annotations


from modules.ai_video_studio.integration.connector_base import DomainConnector
from modules.ai_video_studio.integration.crm.automatic_ads import (
    get_automatic_ads_generator,
)
from modules.ai_video_studio.integration.crm.customer_campaigns import (
    get_customer_campaign_generator,
)
from modules.ai_video_studio.integration.crm.lead_followup_video import (
    get_lead_followup_generator,
)
from modules.ai_video_studio.integration.crm.onboarding_video import (
    get_onboarding_video_generator,
)
from modules.ai_video_studio.integration.crm.promotional_campaigns import (
    get_promotional_campaigns_generator,
)


class CRMConnector(DomainConnector):
    """Generates CRM-domain video briefs."""

    domain = "crm"
    description = "Customer campaigns, automatic ads, lead follow-ups, onboarding and promotions"

    def __init__(self) -> None:
        super().__init__()
        self._register("customer_campaign", lambda d: get_customer_campaign_generator().generate(**d))
        self._register("automatic_ad", lambda d: get_automatic_ads_generator().generate(**d))
        self._register("lead_followup", lambda d: get_lead_followup_generator().generate(**d))
        self._register("onboarding_video", lambda d: get_onboarding_video_generator().generate(**d))
        self._register("promotional_campaign", lambda d: get_promotional_campaigns_generator().generate(**d))


_crm_connector: CRMConnector | None = None


def get_crm_connector() -> CRMConnector:
    global _crm_connector
    if _crm_connector is None:
        _crm_connector = CRMConnector()
    return _crm_connector
