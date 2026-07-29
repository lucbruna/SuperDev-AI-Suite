"""
Enterprise Integration Demo - Supply Chain + Financial AI Engines working together.
"""

import sys
sys.path.insert(0, "C:/Users/tomga/OneDrive/Desktop/super_dev_suite/SuperDev")
import asyncio
from core.supply_chain_ai_engine import (
    SupplyChainManager, SupplyChainConfig, SupplyChainContext,
    SupplyChainEventBus, EngineConfig as SCConfig, ManagerConfig as SCManagerConfig,
)
from core.financial_ai_engine import (
    TreasuryManager, FinancialConfig, FinanceContext,
    FinancialEventBus, EngineConfig as FinConfig, ManagerConfig as FinManagerConfig,
)


async def run_integration():
    print("=" * 60)
    print("SuperDev Enterprise AI Suite - Integration Demo")
    print("Supply Chain AI Engine + Financial AI Engine")
    print("=" * 60)

    # Initialize Supply Chain AI Engine
    sc_config = SupplyChainConfig()
    sc_event_bus = SupplyChainEventBus()
    sc_context = SupplyChainContext()
    sc_engine_config = SCConfig(config=sc_config, event_bus=sc_event_bus, context=sc_context)
    sc_manager = SupplyChainManager(SCManagerConfig(engine_config=sc_engine_config))
    await sc_manager.initialize()

    # Initialize Financial AI Engine
    fin_config = FinancialConfig()
    fin_event_bus = FinancialEventBus()
    fin_context = FinanceContext()
    fin_engine_config = FinConfig(config=fin_config, event_bus=fin_event_bus, context=fin_context)
    fin_manager = TreasuryManager(FinManagerConfig(engine_config=fin_engine_config))
    await fin_manager.initialize()

    # Supply Chain Operations
    print("\n[1] Supply Chain Intelligence")
    inventory = await sc_manager.get_inventory_snapshot()
    print(f"  Inventory: {inventory.total_items} products, ${inventory.total_value:.2f}")
    print(f"  Low stock items: {inventory.low_stock_count}")

    forecast = await sc_manager.get_demand_forecast(30)
    print(f"  Demand forecast: {forecast.horizon_days}d horizon")

    optimization = await sc_manager.run_global_optimization()
    print(f"  Cost savings identified: ${optimization.cost_savings:.2f}")

    # Financial Operations
    print("\n[2] Financial Intelligence")
    position = await fin_manager.get_cash_position()
    print(f"  Cash balance: ${position.cash_balance:,.2f}")
    print(f"  Total liquidity: ${position.total_liquidity:,.2f}")

    cashflow = await fin_manager.get_cashflow_forecast(90)
    print(f"  Cashflow: ${cashflow.total_inflow:,.2f} in / ${cashflow.total_outflow:,.2f} out")
    print(f"  Projected ending: ${cashflow.ending_balance:,.2f}")

    kpis = await fin_manager.get_kpis()
    print(f"  Financial KPIs: {len(kpis)} metrics tracked")

    budget = await fin_manager.get_budget_report("monthly")
    print(f"  Budget: ${budget.total_planned:,.2f} planned, ${budget.total_actual:,.2f} actual")

    # Cross-Domain Integration
    print("\n[3] Cross-Domain Intelligence")
    sc_suppliers = await sc_manager.get_supplier_evaluations()
    for s in sc_suppliers:
        print(f"  Supplier {s.supplier_name}: score {s.overall_score}/100")

    investment = await fin_manager.analyze_investment({
        "name": "Supply Chain Automation",
        "investment": 500000.0,
        "expected_return": 150000.0,
    })
    print(f"  SC Automation Investment: ROI {investment.roi_percent}%, NPV ${investment.npv:,.2f}")

    risk = await fin_manager.get_risk_assessment()
    print(f"  Financial risk score: {risk.overall_score}/100, level: {risk.risk_level.value}")

    audit = await fin_manager.run_audit()
    print(f"  Audit: {audit.total_transactions_reviewed} transactions, {audit.anomalies_found} anomalies")

    # Health Status
    print("\n[4] System Health")
    sc_health = sc_manager.get_engine_status()
    fin_health = fin_manager.get_engine_status()
    print(f"  Supply Chain Engine: {sc_health['state']}, decisions: {sc_health['decisions_made']}")
    print(f"  Financial Engine: {fin_health['state']}, forecasts: {fin_health['forecasts']}")

    # Cleanup
    await sc_manager.shutdown()
    await fin_manager.shutdown()
    print("\n" + "=" * 60)
    print("Enterprise AI Suite fully operational!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_integration())
