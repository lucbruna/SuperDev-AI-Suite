"""
Enterprise Full Integration Demo - All 6 AI Engines working together.
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
from core.human_resources_ai import (
    TalentManager, HRConfig, EmployeeContext,
    HREventBus, EngineConfig as HRConfig_EC, ManagerConfig as HRManagerConfig,
)
from core.legal_compliance_engine import (
    LegalManager, LegalConfig, LegalContext,
    LegalEventBus, EngineConfig as LGLConfig_EC, ManagerConfig as LGLManagerConfig,
)
from core.customer_ai_engine import (
    ExperienceManager, CustomerConfig, CustomerContext,
    CustomerEventBus, EngineConfig as CXConfig_EC, ManagerConfig as CXManagerConfig,
)
from core.decision_command_center import (
    CommandCenter, DecisionConfig, DecisionSecurityManager,
    EngineConfig as DCCConfig_EC, ManagerConfig as DCCManagerConfig,
)
from core.physical_ai_engine import (
    RoboticsManager, PhysicalConfig, PhysicalContext,
    PhysicalEventBus, PhysicalSecurityManager,
    EngineConfig as PHYConfig_EC, ManagerConfig as PHYManagerConfig,
)
from core.multimodal_ai import (
    InteractionManager, MultimodalConfig, MultimodalSecurityManager,
    InputType, ManagerConfig as MMConfig,
    EngineConfig as MMConfig_EC,
)
from core.ai_knowledge_engine import (
    KnowledgeManager, KnowledgeConfig, KnowledgeSecurityManager,
    KnowledgeEventBus, KnowledgeContext, KnowledgeLogger, KnowledgeRegistry,
    KnowledgeType,
    ManagerConfig as KWMConfig,
    KnowledgeEngineConfig as KWMConfig_EC,
)


async def run_full_integration():
    print("=" * 60)
    print("SuperDev Enterprise AI Suite - Full Integration")
    print("Supply Chain + Financial + HR + Legal + Customer + Decision Center + Physical World + Multimodal AI + Knowledge Engine")
    print("=" * 60)

    sc_config = SupplyChainConfig()
    sc_event_bus = SupplyChainEventBus()
    sc_context = SupplyChainContext()
    sc_engine_config = SCConfig(config=sc_config, event_bus=sc_event_bus, context=sc_context)
    sc_manager = SupplyChainManager(SCManagerConfig(engine_config=sc_engine_config))
    await sc_manager.initialize()

    fin_config = FinancialConfig()
    fin_event_bus = FinancialEventBus()
    fin_context = FinanceContext()
    fin_engine_config = FinConfig(config=fin_config, event_bus=fin_event_bus, context=fin_context)
    fin_manager = TreasuryManager(FinManagerConfig(engine_config=fin_engine_config))
    await fin_manager.initialize()

    hr_config = HRConfig()
    hr_event_bus = HREventBus()
    hr_context = EmployeeContext()
    hr_engine_config = HRConfig_EC(config=hr_config, event_bus=hr_event_bus, context=hr_context)
    hr_manager = TalentManager(HRManagerConfig(engine_config=hr_engine_config))
    await hr_manager.initialize()

    lgl_config = LegalConfig()
    lgl_event_bus = LegalEventBus()
    lgl_context = LegalContext()
    lgl_engine_config = LGLConfig_EC(config=lgl_config, event_bus=lgl_event_bus, context=lgl_context)
    lgl_manager = LegalManager(LGLManagerConfig(engine_config=lgl_engine_config))
    await lgl_manager.initialize()

    cx_config = CustomerConfig()
    cx_event_bus = CustomerEventBus()
    cx_context = CustomerContext()
    cx_engine_config = CXConfig_EC(config=cx_config, event_bus=cx_event_bus, context=cx_context)
    cx_manager = ExperienceManager(CXManagerConfig(engine_config=cx_engine_config))
    await cx_manager.initialize()

    dcc_config = DecisionConfig()
    dcc_security = DecisionSecurityManager(dcc_config)
    dcc_engine_config = DCCConfig_EC(config=dcc_config, security=dcc_security)
    dcc_manager = CommandCenter(DCCManagerConfig(engine_config=dcc_engine_config))
    await dcc_manager.initialize()

    phy_config = PhysicalConfig()
    phy_event_bus = PhysicalEventBus()
    phy_context = PhysicalContext()
    phy_security = PhysicalSecurityManager(phy_config)
    phy_engine_config = PHYConfig_EC(config=phy_config, event_bus=phy_event_bus, context=phy_context, security=phy_security)
    phy_manager = RoboticsManager(PHYManagerConfig(engine_config=phy_engine_config))
    await phy_manager.initialize()

    mm_config = MultimodalConfig()
    mm_security = MultimodalSecurityManager(mm_config)
    mm_security.access.set_user_role("admin", "admin")
    mm_engine_config = MMConfig_EC(config=mm_config, security=mm_security)
    mm_manager = InteractionManager(MMConfig(engine_config=mm_engine_config))
    await mm_manager.initialize()

    kw_config = KnowledgeConfig()
    kw_event_bus = KnowledgeEventBus()
    kw_context = KnowledgeContext()
    kw_security = KnowledgeSecurityManager(kw_config)
    kw_security.access.set_user_role("system", "admin")
    kw_logger = KnowledgeLogger()
    kw_registry = KnowledgeRegistry()
    from core.ai_knowledge_engine.knowledge_metrics import MetricsCollector
    kw_metrics = MetricsCollector(kw_context)
    kw_engine_config = KWMConfig_EC(
        config=kw_config, event_bus=kw_event_bus, context=kw_context,
        security=kw_security, logger=kw_logger, registry=kw_registry,
        metrics_collector=kw_metrics,
    )
    kw_manager = KnowledgeManager(KWMConfig(engine_config=kw_engine_config))
    await kw_manager.initialize()

    # Supply Chain
    print("\n[1] Supply Chain Intelligence")
    inv = await sc_manager.get_inventory_snapshot()
    print(f"  Inventory: {inv.total_items} products, ${inv.total_value:.2f}")

    # Financial
    print("\n[2] Financial Intelligence")
    pos = await fin_manager.get_cash_position()
    print(f"  Cash: ${pos.cash_balance:,.2f} | Liquidity: ${pos.total_liquidity:,.2f}")
    fin_kpis = await fin_manager.get_kpis()
    print(f"  Financial KPIs: {len(fin_kpis)} metrics")

    # HR
    print("\n[3] Human Resources Intelligence")
    profile = await hr_manager.get_candidate_profile("C-001")
    print(f"  Candidate: {profile.name} | Match: {profile.match_score}%")
    culture = await hr_manager.get_culture_report()
    print(f"  Culture: engagement {culture.engagement_score}/100, satisfaction {culture.satisfaction_score}/100")
    payroll = await hr_manager.get_payroll_summary("monthly")
    print(f"  Payroll: {payroll.total_employees} employees, ${payroll.total_gross_pay:,.2f} gross")
    hr_kpis = await hr_manager.get_kpis()
    print(f"  HR KPIs: {len(hr_kpis)} metrics")

    # Legal
    print("\n[4] Legal & Compliance Intelligence")
    contract = await lgl_manager.get_contract("CT-001")
    print(f"  Contract: {contract.title} | Risk: {contract.risk_level.value}")
    compliance = await lgl_manager.get_compliance_report()
    print(f"  Compliance: score {compliance.overall_score}/100, {compliance.violations_count} violations")
    risk = await lgl_manager.get_risk_assessment()
    print(f"  Legal Risk: score {risk.overall_score}/100, level: {risk.risk_level.value}")
    lgl_kpis = await lgl_manager.get_kpis()
    print(f"  Legal KPIs: {len(lgl_kpis)} metrics")

    # Customer
    print("\n[5] Customer Experience Intelligence")
    cx_profile = await cx_manager.get_customer_profile("CXP-001")
    print(f"  Customer: {cx_profile.name} | Tier: {cx_profile.tier.value}")
    cx_kpis = await cx_manager.get_kpis()
    print(f"  CX KPIs: {len(cx_kpis)} metrics")
    cx_health = await cx_manager.get_cx_health_score()
    print(f"  CX Health: {cx_health['score']:.1f}/100 ({cx_health['status']})")
    ticket = await cx_manager.open_ticket("CXP-001", "Order delay", "My order is late")
    print(f"  Ticket: {ticket.id} - {ticket.subject}")

    # Decision Command Center
    print("\n[6] Decision Command Center")
    dcc_kpis = await dcc_manager.get_kpis()
    print(f"  Enterprise KPIs: {len(dcc_kpis)} indicators")
    insights = await dcc_manager.get_insights()
    print(f"  Active Insights: {len(insights)}")
    predictions = await dcc_manager.get_predictions()
    print(f"  Active Predictions: {len(predictions)}")
    recs = await dcc_manager.get_recommendations()
    print(f"  Recommendations: {len(recs)}")
    health = await dcc_manager.get_business_health()
    print(f"  Enterprise Health: {health['health_score']}/100 ({health['status']})")
    answer = await dcc_manager.ask_ceo_assistant("Qual o maior problema da empresa hoje?")
    print(f"  CEO Assistant: {answer['answer'][:80]}...")

    # Physical World
    print("\n[7] Physical World Intelligence")
    phy_robots = await phy_manager.get_robots()
    print(f"  Robots in fleet: {len(phy_robots)}")
    phy_task = await phy_manager.assign_task("R-001", "inspect", "Inspect product line")
    print(f"  Task assigned: {phy_task.robot_id} - {phy_task.description}")
    phy_kpis = await phy_manager.get_physical_kpis()
    print(f"  Physical KPIs: {phy_kpis['robots_active']:.0f} active robots, {phy_kpis['uptime_hours']:.1f}h uptime")
    phy_health = await phy_manager.get_factory_health()
    print(f"  Factory Health: {phy_health['health_score']:.0f}/100")
    phy_status = phy_manager.get_engine_status()
    print(f"  Engine: {phy_status['state']}")

    # Multimodal AI
    print("\n[8] Multimodal AI Intelligence")
    mm_result = await mm_manager.process_input("Analyze quarterly sales performance", input_type=InputType.TEXT, user_id="admin")
    print(f"  Text Input: {mm_result.type.value} - {mm_result.content[:80]}...")
    mm_stats = await mm_manager.get_modality_stats()
    print(f"  Modality Stats: {mm_stats}")
    mm_status = await mm_manager.get_engine_status()
    print(f"  Engine: {mm_status['state']} | Inputs: {mm_status['inputs_processed']}")
    mm_healthy = mm_manager.is_healthy()
    print(f"  Healthy: {mm_healthy}")

    # Knowledge Engine
    print("\n[9] Knowledge Engine Intelligence")
    kw_entry = await kw_manager.store_knowledge("Market Analysis 2026", "Comprehensive market analysis for enterprise growth", knowledge_type=KnowledgeType.RESEARCH)
    print(f"  Stored: {kw_entry.title} (id: {kw_entry.id})")
    kw_results = await kw_manager.search_knowledge("Market")
    print(f"  Search results: {len(kw_results)} entries")
    kw_stats = await kw_manager.get_knowledge_stats()
    print(f"  Knowledge Stats: {kw_stats.total_entries} total entries")
    kw_status = await kw_manager.get_engine_status()
    print(f"  Engine: {kw_status['state']} | Knowledge: {kw_status.get('total_entries', 0)}")
    kw_healthy = kw_manager.is_healthy()
    print(f"  Healthy: {kw_healthy}")

    # Cross-domain
    print("\n[10] Cross-Domain Health")
    sc_health = sc_manager.get_engine_status()
    fin_health = fin_manager.get_engine_status()
    hr_health = hr_manager.get_engine_status()
    lgl_health = lgl_manager.get_engine_status()
    cx_health = cx_manager.get_engine_status()
    dcc_health = dcc_manager.get_engine_status()
    phy_health = phy_manager.get_engine_status()
    mm_health = await mm_manager.get_engine_status()
    kw_health = await kw_manager.get_engine_status()
    print(f"  Supply Chain:       {sc_health['state']}")
    print(f"  Financial:          {fin_health['state']}")
    print(f"  HR:                 {hr_health['state']}")
    print(f"  Legal:              {lgl_health['state']}")
    print(f"  Customer:           {cx_health['state']}")
    print(f"  Decision Center:    {dcc_health['state']}")
    print(f"  Physical World:     {phy_health['state']}")
    print(f"  Multimodal AI:      {mm_health['state']}")
    print(f"  Knowledge Engine:   {kw_health['state']}")
    healthy = all(h['state'] == 'running' for h in [sc_health, fin_health, hr_health, lgl_health, cx_health, dcc_health, phy_health, mm_health, kw_health])
    print(f"\n  All systems {'OPERATIONAL' if healthy else 'DEGRADED'}")

    await sc_manager.shutdown()
    await fin_manager.shutdown()
    await hr_manager.shutdown()
    await lgl_manager.shutdown()
    await cx_manager.shutdown()
    await dcc_manager.shutdown()
    await phy_manager.shutdown()
    await mm_manager.shutdown()
    await kw_manager.shutdown()
    print("\n" + "=" * 60)
    print("Enterprise AI Suite - All 9 Engines Fully Operational!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_full_integration())
