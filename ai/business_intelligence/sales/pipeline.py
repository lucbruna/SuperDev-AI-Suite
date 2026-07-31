"""Sales pipeline manager."""
from datetime import datetime
from typing import Dict, List, Optional
from .models import Deal, DealStage, Activity, SalesMetrics


class SalesPipeline:
    def __init__(self):
        self._deals: Dict[str, Deal] = {}
        self._activities: Dict[str, List[Activity]] = {}

    def add_deal(self, deal: Deal) -> Deal:
        self._deals[deal.deal_id] = deal
        return deal

    def get_deal(self, deal_id: str) -> Optional[Deal]:
        return self._deals.get(deal_id)

    def update_stage(self, deal_id: str, new_stage: DealStage) -> bool:
        deal = self._deals.get(deal_id)
        if not deal:
            return False
        deal.stage = new_stage
        if new_stage == DealStage.CLOSED_WON:
            deal.probability = 100
        elif new_stage == DealStage.CLOSED_LOST:
            deal.probability = 0
        return True

    def add_activity(self, activity: Activity) -> Activity:
        self._activities.setdefault(activity.deal_id, []).append(activity)
        return activity

    def get_deals(self, stage: Optional[DealStage] = None, owner: Optional[str] = None) -> List[Deal]:
        deals = list(self._deals.values())
        if stage:
            deals = [d for d in deals if d.stage == stage]
        if owner:
            deals = [d for d in deals if d.owner == owner]
        return deals

    def get_activities(self, deal_id: str) -> List[Activity]:
        return self._activities.get(deal_id, [])

    def get_metrics(self) -> SalesMetrics:
        deals = list(self._deals.values())
        won = [d for d in deals if d.stage == DealStage.CLOSED_WON]
        lost = [d for d in deals if d.stage == DealStage.CLOSED_LOST]
        open_deals = [d for d in deals if d.stage not in (DealStage.CLOSED_WON, DealStage.CLOSED_LOST)]
        total_activities = sum(len(a) for a in self._activities.values())
        won_val = sum(d.value for d in won)
        lost_val = sum(d.value for d in lost)
        total_won_lost = len(won) + len(lost)
        win_rate = (len(won) / total_won_lost * 100) if total_won_lost > 0 else 0.0
        avg_deal = (sum(d.value for d in deals) / len(deals)) if deals else 0.0
        forecast = sum(d.weighted_value for d in open_deals)
        return SalesMetrics(
            pipeline_value=sum(d.value for d in open_deals),
            won_value=won_val,
            lost_value=lost_val,
            win_rate=win_rate,
            avg_deal_size=avg_deal,
            total_deals=len(deals),
            activities_count=total_activities,
            forecast_value=forecast,
        )

    def get_pipeline_by_stage(self) -> Dict[str, List[Deal]]:
        result: Dict[str, List[Deal]] = {}
        for deal in self._deals.values():
            stage_name = deal.stage.value
            result.setdefault(stage_name, []).append(deal)
        return result
