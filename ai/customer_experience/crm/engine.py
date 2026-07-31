"""CRM engine."""

from .models import (
    Account,
    Activity,
    Contact,
    Opportunity,
    OpportunityStage,
)


class CRMEngine:
    def __init__(self):
        self._accounts: dict[str, Account] = {}
        self._contacts: dict[str, Contact] = {}
        self._opportunities: dict[str, Opportunity] = {}
        self._activities: list[Activity] = []

    def add_account(self, account: Account) -> Account:
        self._accounts[account.account_id] = account
        return account

    def get_account(self, account_id: str) -> Account | None:
        return self._accounts.get(account_id)

    def list_accounts(self) -> list[Account]:
        return list(self._accounts.values())

    def add_contact(self, contact: Contact) -> Contact:
        self._contacts[contact.contact_id] = contact
        return contact

    def get_contact(self, contact_id: str) -> Contact | None:
        return self._contacts.get(contact_id)

    def get_account_contacts(self, account_id: str) -> list[Contact]:
        return [c for c in self._contacts.values() if c.account_id == account_id]

    def add_opportunity(self, opportunity: Opportunity) -> Opportunity:
        self._opportunities[opportunity.opportunity_id] = opportunity
        return opportunity

    def get_opportunity(self, opportunity_id: str) -> Opportunity | None:
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
        return sum(
            o.weighted_value
            for o in self._opportunities.values()
            if o.stage not in (OpportunityStage.CLOSED_WON, OpportunityStage.CLOSED_LOST)
        )

    def add_activity(self, activity: Activity) -> Activity:
        self._activities.append(activity)
        return activity

    def get_customer_activities(self, customer_id: str) -> list[Activity]:
        return [a for a in self._activities if a.customer_id == customer_id]

    def get_stats(self) -> dict:
        return {
            "accounts": len(self._accounts),
            "contacts": len(self._contacts),
            "opportunities": len(self._opportunities),
            "activities": len(self._activities),
        }
