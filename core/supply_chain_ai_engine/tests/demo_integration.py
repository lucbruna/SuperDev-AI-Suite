"""Supply Chain AI Engine - Quick Integration Demo"""

import sys
sys.path.insert(0, 'C:/Users/tomga/OneDrive/Desktop/super_dev_suite/SuperDev')
import asyncio
from core.supply_chain_ai_engine import (
    SupplyChainManager, SupplyChainConfig, SupplyChainContext,
    SupplyChainEventBus, EngineConfig, ManagerConfig
)

async def main():
    config = SupplyChainConfig()
    event_bus = SupplyChainEventBus()
    context = SupplyChainContext()
    
    engine_config = EngineConfig(config=config, event_bus=event_bus, context=context)
    manager_config = ManagerConfig(engine_config=engine_config)
    manager = SupplyChainManager(manager_config)
    
    await manager.initialize()
    
    snapshot = await manager.get_inventory_snapshot()
    print(f"Inventory: {snapshot.total_items} products, total value: ${snapshot.total_value:.2f}")
    print(f"  Low stock: {snapshot.low_stock_count}, Out of stock: {snapshot.out_of_stock_count}")
    
    forecast = await manager.get_demand_forecast(7)
    print(f"Demand forecast: {forecast.horizon_days} days horizon")
    
    kpis = await manager.get_kpis()
    print(f"KPIs: {len(kpis)} metrics calculated")
    
    optimization = await manager.run_global_optimization()
    print(f"Optimization: ${optimization.cost_savings:.2f} potential savings")
    print(f"  {len(optimization.recommendations)} recommendations")
    
    plan = await manager.get_procurement_plan(30)
    print(f"Procurement plan: {len(plan.orders)} orders, total: ${plan.total_cost:.2f}")
    
    evaluations = await manager.get_supplier_evaluations()
    for e in evaluations:
        print(f"  Supplier {e.supplier_name}: score {e.overall_score}/100")
    
    logistics = await manager.get_logistics_plan()
    print(f"Logistics: {len(logistics.routes)} routes, on-time rate: {logistics.on_time_rate*100:.0f}%")
    
    status = manager.get_engine_status()
    print(f"Engine status: {status['state']}, decisions: {status['decisions_made']}")
    
    await manager.shutdown()
    print("\nSupply Chain AI Engine integrated and operational!")

if __name__ == "__main__":
    asyncio.run(main())
