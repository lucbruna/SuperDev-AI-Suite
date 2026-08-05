"""Automation — workflow building, triggers, scheduling and event listeners."""
from modules.ai_video_studio.integration.automation.automation_connector import (
    AutomationConnector,
    get_automation_connector,
)
from modules.ai_video_studio.integration.automation.scheduler_bridge import (
    SchedulerBridge,
    get_scheduler_bridge,
)
from modules.ai_video_studio.integration.automation.workflow_builder import (
    WorkflowBuilder,
    get_workflow_builder,
)

__all__ = [
    "AutomationConnector",
    "get_automation_connector",
    "SchedulerBridge",
    "get_scheduler_bridge",
    "WorkflowBuilder",
    "get_workflow_builder",
]
