"""Marketing engine."""
from .models import (
    Campaign,
    CampaignStatus,
    ConversionEvent,
    Lead,
    MarketingMetrics,
    Segment,
)


class MarketingEngine:
    def __init__(self):
        self._campaigns: dict[str, Campaign] = {}
        self._leads: dict[str, Lead] = {}
        self._conversions: list[ConversionEvent] = []
        self._metrics: dict[str, MarketingMetrics] = {}
        self._segments: dict[str, Segment] = {}

    def create_campaign(self, campaign: Campaign) -> Campaign:
        self._campaigns[campaign.campaign_id] = campaign
        self._metrics[campaign.campaign_id] = MarketingMetrics(campaign_id=campaign.campaign_id)
        return campaign

    def update_campaign(self, campaign_id: str, updates: dict) -> Campaign | None:
        c = self._campaigns.get(campaign_id)
        if not c:
            return None
        for k, v in updates.items():
            if hasattr(c, k):
                setattr(c, k, v)
        return c

    def activate_campaign(self, campaign_id: str) -> bool:
        c = self._campaigns.get(campaign_id)
        if not c:
            return False
        c.status = CampaignStatus.ACTIVE
        return True

    def pause_campaign(self, campaign_id: str) -> bool:
        c = self._campaigns.get(campaign_id)
        if not c:
            return False
        c.status = CampaignStatus.PAUSED
        return True

    def add_lead(self, lead: Lead) -> Lead:
        self._leads[lead.lead_id] = lead
        return lead

    def score_lead(self, lead_id: str, score: float) -> bool:
        lead = self._leads.get(lead_id)
        if not lead:
            return False
        lead.score = score
        return True

    def record_conversion(self, conversion: ConversionEvent) -> ConversionEvent:
        self._conversions.append(conversion)
        m = self._metrics.get(conversion.campaign_id)
        if m:
            m.conversions += 1
            m.revenue += conversion.value
            if m.impressions > 0:
                m.conversion_rate = m.conversions / m.impressions * 100
        lead = self._leads.get(conversion.lead_id)
        if lead:
            lead.status = "converted"
        return conversion

    def update_impressions(self, campaign_id: str, impressions: int) -> bool:
        m = self._metrics.get(campaign_id)
        if not m:
            return False
        m.impressions += impressions
        if m.clicks > 0:
            m.ctr = m.clicks / m.impressions * 100
        return True

    def update_clicks(self, campaign_id: str, clicks: int) -> bool:
        m = self._metrics.get(campaign_id)
        if not m:
            return False
        m.clicks += clicks
        if m.impressions > 0:
            m.ctr = m.clicks / m.impressions * 100
        return True

    def get_metrics(self, campaign_id: str) -> MarketingMetrics | None:
        return self._metrics.get(campaign_id)

    def get_leads(self, status: str | None = None) -> list[Lead]:
        leads = list(self._leads.values())
        if status:
            leads = [l for l in leads if l.status == status]
        return leads

    def create_segment(self, segment: Segment) -> Segment:
        self._segments[segment.segment_id] = segment
        return segment

    def get_segment(self, segment_id: str) -> Segment | None:
        return self._segments.get(segment_id)

    def get_campaigns(self, status: CampaignStatus | None = None) -> list[Campaign]:
        campaigns = list(self._campaigns.values())
        if status:
            campaigns = [c for c in campaigns if c.status == status]
        return campaigns
