"""
Campaign Engine - Core campaign management
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID

from marketing_growth_ai.marketing_models import (
    Campaign,
    CampaignStatus,
    CampaignType,
    Channel,
)


class CampaignEngine:
    """Core campaign engine"""

    def __init__(self, engine):
        self.engine = engine
        self.config = engine.config.campaigns
        self._campaigns: Dict[UUID, Campaign] = {}

    async def initialize(self) -> None:
        pass

    async def shutdown(self) -> None:
        pass

    async def create_campaign(
        self,
        name: str,
        campaign_type: CampaignType,
        objective: str,
        target_audience: Dict[str, Any],
        channels: List[Channel],
        budget: float,
        start_date: datetime = None,
        end_date: Optional[datetime] = None,
        duration_days: int = 30,
    ) -> Campaign:
        if start_date is None:
            start_date = datetime.utcnow()
        if end_date is None:
            end_date = start_date + timedelta(days=duration_days)
            
        campaign = Campaign(
            name=name,
            type=campaign_type,
            objective=objective,
            target_audience=target_audience,
            channels=channels,
            budget=budget,
            start_date=start_date,
            end_date=end_date,
        )
        self._campaigns[campaign.id] = campaign
        return campaign

    async def get_campaign(self, campaign_id: UUID) -> Optional[Campaign]:
        return self._campaigns.get(campaign_id)

    async def list_campaigns(self, status: Optional[CampaignStatus] = None) -> List[Campaign]:
        campaigns = list(self._campaigns.values())
        if status:
            campaigns = [c for c in campaigns if c.status == status]
        return campaigns

    async def update_campaign(self, campaign_id: UUID, updates: Dict[str, Any]) -> bool:
        campaign = self._campaigns.get(campaign_id)
        if not campaign:
            return False
        for key, value in updates.items():
            if hasattr(campaign, key):
                setattr(campaign, key, value)
        return True

    async def launch_campaign(self, campaign_id: UUID) -> bool:
        campaign = self._campaigns.get(campaign_id)
        if not campaign:
            return False
        campaign.status = CampaignStatus.ACTIVE
        return True

    async def pause_campaign(self, campaign_id: UUID) -> bool:
        campaign = self._campaigns.get(campaign_id)
        if not campaign:
            return False
        campaign.status = CampaignStatus.PAUSED
        return True

    async def get_performance(self, campaign_id: UUID) -> Dict[str, Any]:
        return {"campaign_id": str(campaign_id), "metrics": {}}

    def get_status(self) -> Dict[str, Any]:
        return {"initialized": True, "campaigns": len(self._campaigns)}