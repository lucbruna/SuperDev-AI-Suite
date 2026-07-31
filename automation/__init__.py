"""Autonomous Workflow & Automation Engine (Volume 20).

Public API for creating, executing, and optimizing automated business
processes: workflows, orchestration, scheduling, triggers, actions,
decisions, rules, pipelines, templates, monitoring, and optimization.
"""
from __future__ import annotations

from .automation_config import AutomationConfig
from .automation_engine import AutomationEngine
from .automation_events import AutomationEventType, AutomationEvents
from .automation_factory import AutomationFactory
from .automation_manager import AutomationManager
from .automation_metrics import AutomationMetrics
from .automation_models import (AutomationDefinition, AutomationResult,
                               ExecutionRecord, ScheduleSpec, TaskRecord,
                               TriggerSpec, TriggerType, WorkflowDefinition,
                               WorkflowStatus, WorkflowStep)
from .automation_protocols import coerce_bool, coerce_number, new_id, safe_get
from .automation_registry import AutomationRegistry
from .automation_runtime import AutomationRuntime
from .automation_security import AutomationSecurity

# Subsystem engines (Volumes 20 — Fases 2-7)
from .actions import (ActionBuilder, ActionDefinition, ActionEngine,
                      ActionPolicy, ActionRegistry, ActionResult, ActionRouter,
                      ActionRunner, ActionValidator)
from .decisions import (DecisionBranch, DecisionBuilder, DecisionEngine,
                        DecisionHistory, DecisionNode, DecisionResult,
                        DecisionTree, DecisionValidator)
from .monitoring import (MonitorAlert, MonitorAlerting, MonitorCheck,
                         MonitorChecker, MonitorEngine, MonitorHistory,
                         MonitorStatus)
from .optimization import (OptimizationReport, OptimizationSuggestion,
                           OptimizerAnalyzer, OptimizerEngine, OptimizerHistory,
                           OptimizerSuggester)
from .orchestration import (OrchestrationAgent, OrchestrationCoordinator,
                            OrchestrationDispatcher, OrchestrationEngine,
                            OrchestrationMonitor, OrchestrationPlan,
                            OrchestrationPlanner, OrchestrationTask,
                            TaskStatus)
from .pipelines import (PipelineBuilder, PipelineDefinition, PipelineEngine,
                        PipelineExecutor, PipelineHistory, PipelineRun,
                        PipelineStage, PipelineValidator, StageStatus)
from .rules import (RuleCondition, RuleDefinition, RuleEngine, RuleHistory,
                    RuleManager, RulePrioritizer, RuleResult)
from .scheduler import (CronParser, SchedulerCalendar, SchedulerEngine,
                        SchedulerExecutor, SchedulerJob, SchedulerPlanner)
from .templates import (TemplateBuilder, TemplateEngine, TemplateHistory,
                        TemplateParameter, TemplateRenderer, TemplateValidator,
                        WorkflowTemplate)
from .triggers import (TriggerCondition, TriggerDefinition, TriggerEngine,
                       TriggerEvaluator, TriggerEvent, TriggerHistory,
                       TriggerRegistry, TriggerRouter, TriggerScheduler)
from .workflow import (WorkflowBuilder, WorkflowEngine, WorkflowExecutor,
                       WorkflowManager, WorkflowState, WorkflowValidator,
                       WorkflowVersion, WorkflowVersioner)

__all__ = [
    "ActionBuilder",
    "ActionDefinition",
    "ActionEngine",
    "ActionPolicy",
    "ActionRegistry",
    "ActionResult",
    "ActionRouter",
    "ActionRunner",
    "ActionValidator",
    "AutomationConfig",
    "AutomationDefinition",
    "AutomationEngine",
    "AutomationEventType",
    "AutomationEvents",
    "AutomationFactory",
    "AutomationManager",
    "AutomationMetrics",
    "AutomationRegistry",
    "AutomationResult",
    "AutomationRuntime",
    "AutomationSecurity",
    "CronParser",
    "DecisionBranch",
    "DecisionBuilder",
    "DecisionEngine",
    "DecisionHistory",
    "DecisionNode",
    "DecisionResult",
    "DecisionTree",
    "DecisionValidator",
    "ExecutionRecord",
    "MonitorAlert",
    "MonitorAlerting",
    "MonitorCheck",
    "MonitorChecker",
    "MonitorEngine",
    "MonitorHistory",
    "MonitorStatus",
    "OptimizationReport",
    "OptimizationSuggestion",
    "OptimizerAnalyzer",
    "OptimizerEngine",
    "OptimizerHistory",
    "OptimizerSuggester",
    "OrchestrationAgent",
    "OrchestrationCoordinator",
    "OrchestrationDispatcher",
    "OrchestrationEngine",
    "OrchestrationMonitor",
    "OrchestrationPlan",
    "OrchestrationPlanner",
    "OrchestrationTask",
    "PipelineBuilder",
    "PipelineDefinition",
    "PipelineEngine",
    "PipelineExecutor",
    "PipelineHistory",
    "PipelineRun",
    "PipelineStage",
    "PipelineValidator",
    "RuleCondition",
    "RuleDefinition",
    "RuleEngine",
    "RuleHistory",
    "RuleManager",
    "RulePrioritizer",
    "RuleResult",
    "ScheduleSpec",
    "SchedulerCalendar",
    "SchedulerEngine",
    "SchedulerExecutor",
    "SchedulerJob",
    "SchedulerPlanner",
    "StageStatus",
    "TaskRecord",
    "TaskStatus",
    "TemplateBuilder",
    "TemplateEngine",
    "TemplateHistory",
    "TemplateParameter",
    "TemplateRenderer",
    "TemplateValidator",
    "TriggerCondition",
    "TriggerDefinition",
    "TriggerEngine",
    "TriggerEvaluator",
    "TriggerEvent",
    "TriggerHistory",
    "TriggerRegistry",
    "TriggerRouter",
    "TriggerScheduler",
    "TriggerSpec",
    "TriggerType",
    "WorkflowBuilder",
    "WorkflowDefinition",
    "WorkflowEngine",
    "WorkflowExecutor",
    "WorkflowManager",
    "WorkflowState",
    "WorkflowStatus",
    "WorkflowStep",
    "WorkflowTemplate",
    "WorkflowValidator",
    "WorkflowVersion",
    "WorkflowVersioner",
    "coerce_bool",
    "coerce_number",
    "new_id",
    "safe_get",
]
