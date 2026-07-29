"""
Autonomous Business Intelligence & Decision Command Center

Enterprise decision intelligence platform providing:
- Real-time business monitoring & dashboards
- KPI management & benchmarking
- Advanced analytics & pattern detection
- Business prediction & forecasting
- Strategic simulation & scenario analysis
- AI-powered recommendations & action planning
- Executive intelligence & board reporting
"""

from .decision_engine import DecisionEngine, EngineConfig, EngineState, EngineMetrics
from .command_center import CommandCenter, ManagerConfig
from .dashboard_manager import DashboardManager
from .insight_manager import InsightManager
from .strategy_engine import StrategyEngine
from .simulation_engine import SimulationEngine as SimulationEngineCore
from .decision_models import *
from .decision_config import DecisionConfig
from .decision_security import DecisionSecurityManager

from .dashboards import DashboardEngine, DashboardBuilder, VisualizationManager, RealtimeDashboard, ExecutiveDashboard
from .indicators import IndicatorEngine, KPIManager, MetricCalculator, Benchmark
from .analytics import AnalyticsEngine, PatternDetector, CorrelationAnalyzer, BusinessAnalysis
from .prediction import PredictionEngine, RevenuePrediction, DemandPrediction, RiskPrediction
from .simulation import SimulationEngine, ScenarioBuilder, ImpactAnalysis, StrategySimulator
from .recommendations import RecommendationEngine, ActionPlanner, PriorityManager, Optimization
from .executive import ExecutiveEngine, CEOAssistant, BoardReportGenerator, StrategicSummary

__version__ = "1.0.0"
__version_info__ = (1, 0, 0)

__all__ = [
    "DecisionEngine", "EngineConfig", "EngineState", "EngineMetrics",
    "CommandCenter", "ManagerConfig",
    "DashboardManager", "InsightManager", "StrategyEngine", "SimulationEngineCore",
    "DecisionSecurityManager", "DecisionConfig",
    "DashboardEngine", "DashboardBuilder", "VisualizationManager",
    "RealtimeDashboard", "ExecutiveDashboard",
    "IndicatorEngine", "KPIManager", "MetricCalculator", "Benchmark",
    "AnalyticsEngine", "PatternDetector", "CorrelationAnalyzer", "BusinessAnalysis",
    "PredictionEngine", "RevenuePrediction", "DemandPrediction", "RiskPrediction",
    "SimulationEngine", "ScenarioBuilder", "ImpactAnalysis", "StrategySimulator",
    "RecommendationEngine", "ActionPlanner", "PriorityManager", "Optimization",
    "ExecutiveEngine", "CEOAssistant", "BoardReportGenerator", "StrategicSummary",
]
