"""CRM engine."""
from datetime import datetime
from typing import Dict, List, Optional
from .models import (
    Account, Contact, ContactType, Opportunity, OpportunityStage, Activity, ActivityType,
)


class CRMEngine:
    def __init__(self):
        self._accounts: Dict[str, Account] = {}
        self._contacts: Dict[str, Contact] = {}
        self._opportunities: Dict[str, Opportunity] = {}
        self._activities: List[Activity] = []

    def add_account(self, account: Account) -> Account:
        self._accounts[account.account_id] = account
        return account

    def get_account(self, account_id: str) -> Optional[Account]:
        return self._accounts.get(account_id)

    def list_accounts(self) -> List[Account]:
        return list(self._accounts.values())

    def add_contact(self, contact: Contact) -> Contact:
        self._contacts[contact.contact_id] = contact
        return contact

    def get_contact(self, contact_id: str) -> Optional[Contact]:
        return self._contacts.get(contact_id)

    def get_account_contacts(self, account_id: str) -> List[Contact]:
        return [c for c in self._contacts.values() if c.account_id == account_id]

    def add_opportunity(self, opportunity: Opportunity) -> Opportunity:
        self._opportunities[opportunity.opportunity_id] = opportunity
        return opportunity

    def get_opportunity(self, opportunity_id: str) -> Optional[Opportunity]:
        return self._opportunities.get(opportunity_id)

    def update_opportunity_stage(self, opportunity_id: str, stage: OpportunityStage) -> bool:
        opp = self._opportunities.get(opportunity_id)
        if not opp:
            return False
        opp.stage = stage
        if stage == OpportunityStage.CLOSED_WON:
            opp.probability = 100
        elif stage == OpportunityStage.CLOSED_LOST:
            opp.probability = 0
        return True

    def get_pipeline_value(self) -> float:
        return sum(o.weighted_value for o in self._opportunities.values()
                   if o.stage not in (OpportunityStage.CLOSED_WON, OpportunityStage.CLOSED_LOST))

    def add_activity(self, activity: Activity) -> Activity:
        self._activities.append(activity)
        return activity

    def get_customer_activities(self, customer_id: str) -> List[Activity]:
        return [a for a in self._activities if a.customer_id == customer_id]

    def get_stats(self) -> dict:
        return {
            "accounts": len(self._accounts),
            "contacts": len(self._contacts),
            "opportunities": len(self._opportunities),
            "activities": len(self._activities),
        }
