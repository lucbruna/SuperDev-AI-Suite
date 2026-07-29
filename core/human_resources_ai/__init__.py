"""
Autonomous Human Resources & Talent Intelligence Engine

Enterprise HR intelligence system providing:
- Intelligent recruitment & candidate analysis
- Employee onboarding & integration
- Performance evaluation & goal tracking
- Personalized learning & development
- Talent mapping & career planning
- Culture analytics & engagement monitoring
- Workforce planning & demand prediction
- Payroll intelligence & compensation analysis
- Employee digital twin simulation
"""

from .hr_engine import HREngine, EngineConfig, EngineState, EngineMetrics
from .talent_manager import TalentManager, ManagerConfig
from .employee_context import EmployeeContext
from .hr_events import HREventBus, HREvent, EventType
from .hr_metrics import HRMetrics, KPICalculator
from .hr_security import HRSecurityManager
from .hr_models import *
from .hr_config import HRConfig

from .recruitment import RecruitmentEngine, CandidateAnalyzer, ResumeParser, SkillMatcher, InterviewAssistant
from .onboarding import OnboardingEngine, EmployeeSetup, TrainingPlan, DocumentManager
from .performance import PerformanceEngine, GoalTracker, ProductivityAnalysis, FeedbackManager
from .learning import LearningEngine, TrainingRecommender, KnowledgePath, SkillDevelopment
from .talent import TalentEngine, SkillGraph, CareerPlanner, SuccessionPlanner
from .culture import CultureEngine, SentimentAnalysis, EngagementMonitor, FeedbackAnalysis
from .workforce import WorkforceEngine, DemandPrediction, SchedulingEngine, CapacityAnalysis
from .payroll import PayrollEngine, SalaryAnalysis, BenefitsManager, CompensationEngine

__version__ = "1.0.0"
__version_info__ = (1, 0, 0)

__all__ = [
    "HREngine", "EngineConfig", "EngineState", "EngineMetrics",
    "TalentManager", "ManagerConfig",
    "EmployeeContext", "HREventBus", "HREvent", "EventType",
    "HRMetrics", "KPICalculator", "HRSecurityManager",
    "HRConfig",
    "RecruitmentEngine", "CandidateAnalyzer", "ResumeParser",
    "SkillMatcher", "InterviewAssistant",
    "OnboardingEngine", "EmployeeSetup", "TrainingPlan", "DocumentManager",
    "PerformanceEngine", "GoalTracker", "ProductivityAnalysis", "FeedbackManager",
    "LearningEngine", "TrainingRecommender", "KnowledgePath", "SkillDevelopment",
    "TalentEngine", "SkillGraph", "CareerPlanner", "SuccessionPlanner",
    "CultureEngine", "SentimentAnalysis", "EngagementMonitor", "FeedbackAnalysis",
    "WorkforceEngine", "DemandPrediction", "SchedulingEngine", "CapacityAnalysis",
    "PayrollEngine", "SalaryAnalysis", "BenefitsManager", "CompensationEngine",
]
