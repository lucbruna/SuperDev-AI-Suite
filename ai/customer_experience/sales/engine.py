"""Sales engine."""
import uuid

from .models import LeadSource, SalesActivity, SalesLead, SalesPrediction, SalesStage


class SalesEngine:
    def __init__(self):
        self._leads: dict[str, SalesLead] = {}
        self._predictions: dict[str, SalesPrediction] = {}
        self._activities: dict[str, list[SalesActivity]] = {}

    def add_lead(self, lead: SalesLead) -> SalesLead:
        self._leads[lead.lead_id] = lead
        return lead

    def get_lead(self, lead_id: str) -> SalesLead | None:
        return self._leads.get(lead_id)

    def score_lead(self, lead_id: str) -> float:
        lead = self._leads.get(lead_id)
        if not lead:
            return 0.0
        score = 50.0
        if lead.source == LeadSource.REFERRAL:
            score += 20
        elif lead.source == LeadSource.WEBSITE:
            score += 10
        if lead.value > 10000:
            score += 15
        elif lead.value > 1000:
            score += 5
        score = min(100.0, score)
        lead.score = score
        return score

    def predict_conversion(self, lead_id: str) -> SalesPrediction:
        lead = self._leads.get(lead_id)
        if not lead:
            return SalesPrediction(prediction_id=str(uuid.uuid4())[:8], lead_id=lead_id)
        prob = lead.score / 100.0
        factors = []
        if lead.score >= 70:
            factors.append("high_lead_score")
        if lead.value > 5000:
            factors.append("high_value")
        if lead.source == LeadSource.REFERRAL:
            factors.append("referral_source")
        pred = SalesPrediction(
            prediction_id=str(uuid.uuid4())[:8],
            lead_id=lead_id,
            conversion_probability=prob,
            predicted_value=lead.value * prob,
            confidence=0.75,
            factors=factors,
        )
        self._predictions[lead_id] = pred
        return pred

    def get_leads(self, stage: SalesStage | None = None, min_score: float | None = None) -> list[SalesLead]:
        leads = list(self._leads.values())
        if stage:
            leads = [l for l in leads if l.stage == stage]
        if min_score is not None:
            leads = [l for l in leads if l.score >= min_score]
        return leads

    def add_activity(self, activity: SalesActivity) -> SalesActivity:
        self._activities.setdefault(activity.lead_id, []).append(activity)
        return activity

    def get_activities(self, lead_id: str) -> list[SalesActivity]:
        return self._activities.get(lead_id, [])

    def get_prediction(self, lead_id: str) -> SalesPrediction | None:
        return self._predictions.get(lead_id)

    def get_pipeline_summary(self) -> dict[str, Any]:
        leads = list(self._leads.values())
        total_value = sum(l.value for l in leads)
        qualified = [l for l in leads if l.is_qualified]
        return {
            "total_leads": len(leads),
            "qualified_leads": len(qualified),
            "total_pipeline_value": total_value,
            "avg_score": sum(l.score for l in leads) / len(leads) if leads else 0.0,
        }
