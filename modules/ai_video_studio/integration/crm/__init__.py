"""CRM — customer campaigns, automatic ads, lead follow-ups, onboarding and promotions."""
from modules.ai_video_studio.integration.crm.crm_connector import (
    CRMConnector,
    get_crm_connector,
)
from modules.ai_video_studio.integration.crm.customer_campaigns import (
    CustomerCampaignGenerator,
    get_customer_campaign_generator,
)
from modules.ai_video_studio.integration.crm.lead_followup_video import (
    LeadFollowupGenerator,
    get_lead_followup_generator,
)

__all__ = [
    "CRMConnector",
    "get_crm_connector",
    "CustomerCampaignGenerator",
    "get_customer_campaign_generator",
    "LeadFollowupGenerator",
    "get_lead_followup_generator",
]
