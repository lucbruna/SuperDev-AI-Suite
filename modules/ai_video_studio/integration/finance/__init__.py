"""Finance — financial/investment reports, accounting dashboards and management presentations."""
from modules.ai_video_studio.integration.finance.finance_connector import (
    FinanceConnector,
    get_finance_connector,
)
from modules.ai_video_studio.integration.finance.financial_reports import (
    FinancialReportGenerator,
    get_financial_report_generator,
)
from modules.ai_video_studio.integration.finance.investment_reports import (
    InvestmentReportGenerator,
    get_investment_report_generator,
)

__all__ = [
    "FinanceConnector",
    "get_finance_connector",
    "FinancialReportGenerator",
    "get_financial_report_generator",
    "InvestmentReportGenerator",
    "get_investment_report_generator",
]
