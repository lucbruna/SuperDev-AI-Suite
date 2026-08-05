"""Business skills bundle — deterministic planning skills for business work."""
from __future__ import annotations

from modules.ai_video_studio.skills.business.business_plan_skill import BusinessPlanSkill
from modules.ai_video_studio.skills.business.contract_draft_skill import ContractDraftSkill
from modules.ai_video_studio.skills.business.financial_report_skill import FinancialReportSkill
from modules.ai_video_studio.skills.business.meeting_summary_skill import MeetingSummarySkill
from modules.ai_video_studio.skills.business.pitch_deck_skill import PitchDeckSkill
from modules.ai_video_studio.skills.business.proposal_skill import ProposalSkill

__all__ = [
    "BusinessPlanSkill",
    "ContractDraftSkill",
    "FinancialReportSkill",
    "MeetingSummarySkill",
    "PitchDeckSkill",
    "ProposalSkill",
]
