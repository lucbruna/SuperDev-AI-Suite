"""Finance Connector — facade over the finance generators."""
from __future__ import annotations


from modules.ai_video_studio.integration.connector_base import DomainConnector
from modules.ai_video_studio.integration.finance.accounting_dashboard import (
    get_accounting_dashboard_generator,
)
from modules.ai_video_studio.integration.finance.financial_reports import (
    get_financial_report_generator,
)
from modules.ai_video_studio.integration.finance.investment_reports import (
    get_investment_report_generator,
)
from modules.ai_video_studio.integration.finance.management_presentations import (
    get_management_presentation_generator,
)


class FinanceConnector(DomainConnector):
    """Generates finance-domain video briefs."""

    domain = "finance"
    description = "Financial and investment reports, accounting dashboards and management presentations"

    def __init__(self) -> None:
        super().__init__()
        self._register("financial_report", lambda d: get_financial_report_generator().generate(**d))
        self._register("investment_report", lambda d: get_investment_report_generator().generate(**d))
        self._register("accounting_dashboard", lambda d: get_accounting_dashboard_generator().generate(**d))
        self._register("management_presentation", lambda d: get_management_presentation_generator().generate(**d))


_finance_connector: FinanceConnector | None = None


def get_finance_connector() -> FinanceConnector:
    global _finance_connector
    if _finance_connector is None:
        _finance_connector = FinanceConnector()
    return _finance_connector
