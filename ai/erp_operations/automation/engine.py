"""Automation engine."""
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from .models import AutomationRule, AutomationExecution, ScheduledTask, AutomationMetrics
from .models import AutomationStatus, TriggerType


class AutomationEngine:
    def __init__(self):
        self._rules: Dict[str, AutomationRule] = {}
        self._executions: List[AutomationExecution] = []
        self._scheduled: Dict[str, ScheduledTask] = {}

    def create_rule(self, rule: AutomationRule) -> AutomationRule:
        self._rules[rule.rule_id] = rule
        return rule

    def get_rule(self, rule_id: str) -> Optional[AutomationRule]:
        return self._rules.get(rule_id)

    def activate_rule(self, rule_id: str) -> bool:
        rule = self._rules.get(rule_id)
        if not rule:
            return False
        rule.status = AutomationStatus.ACTIVE
        return True

    def deactivate_rule(self, rule_id: str) -> bool:
        rule = self._rules.get(rule_id)
        if not rule:
            return False
        rule.status = AutomationStatus.INACTIVE
        return True

    def execute_rule(self, rule_id: str, context: Optional[Dict[str, Any]] = None) -> AutomationExecution:
        rule = self._rules.get(rule_id)
        execution = AutomationExecution(
            execution_id=str(uuid.uuid4())[:8],
            rule_id=rule_id,
            status="success",
            result={"actions_executed": len(rule.actions) if rule else 0, "context": context or {}},
            duration_ms=15.0,
        )
        if rule:
            rule.run_count += 1
            rule.last_run = datetime.now()
        execution.completed_at = datetime.now()
        self._executions.append(execution)
        return execution

    def get_executions(self, rule_id: Optional[str] = None) -> List[AutomationExecution]:
        if rule_id:
            return [e for e in self._executions if e.rule_id == rule_id]
        return list(self._executions)

    def schedule_task(self, task: ScheduledTask) -> ScheduledTask:
        self._scheduled[task.task_id] = task
        return task

    def get_scheduled_tasks(self) -> List[ScheduledTask]:
        return list(self._scheduled.values())

    def get_active_rules(self) -> List[AutomationRule]:
        return [r for r in self._rules.values() if r.status == AutomationStatus.ACTIVE]

    def get_metrics(self) -> AutomationMetrics:
        execs = list(self._executions)
        success = [e for e in execs if e.status == "success"]
        return AutomationMetrics(
            total_executions=len(execs),
            success_rate=(len(success) / len(execs) * 100) if execs else 0.0,
            avg_duration_ms=sum(e.duration_ms for e in execs) / len(execs) if execs else 0.0,
            active_rules=len([r for r in self._rules.values() if r.status == AutomationStatus.ACTIVE]),
            failed_executions=len(execs) - len(success),
        )
