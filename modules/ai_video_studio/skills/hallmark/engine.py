"""Hallmark engine — compose the hallmark components into one pipeline."""
from __future__ import annotations
from typing import Any

from modules.ai_video_studio.skills.hallmark.cache import ResultCache
from modules.ai_video_studio.skills.hallmark.context import ContextBuilder
from modules.ai_video_studio.skills.hallmark.executor import StepExecutor
from modules.ai_video_studio.skills.hallmark.learning import FeedbackLearner
from modules.ai_video_studio.skills.hallmark.memory import MemoryStore
from modules.ai_video_studio.skills.hallmark.monitor import RunMonitor
from modules.ai_video_studio.skills.hallmark.optimizer import RunOptimizer
from modules.ai_video_studio.skills.hallmark.planner import TaskPlanner
from modules.ai_video_studio.skills.hallmark.reasoning import ReasoningChain
from modules.ai_video_studio.skills.hallmark.router import SkillRouter
from modules.ai_video_studio.skills.hallmark.runtime import Runtime
from modules.ai_video_studio.skills.hallmark.statistics import RunStatistics


class HallmarkEngine:
    """Wire the hallmark subsystems behind a single run() entrypoint."""

    def __init__(self) -> None:
        self.runtime = Runtime()
        self.memory = MemoryStore()
        self.reasoning = ReasoningChain()
        self.context = ContextBuilder()
        self.router = SkillRouter()
        self.cache = ResultCache()
        self.learning = FeedbackLearner()
        self.optimizer = RunOptimizer()
        self.planner = TaskPlanner()
        self.executor = StepExecutor()
        self.monitor = RunMonitor()
        self.statistics = RunStatistics()

    def run(self, goal: str, *, steps: int = 3) -> dict[str, Any]:
        """Run the full pipeline for a goal and return a structured result."""
        self.runtime.record_step("plan", {"goal": goal})
        plan = self.planner.plan(goal, steps=steps)

        self.runtime.record_step("execute", {"steps": len(plan["plan"])})
        outcomes = self.executor.run(plan["plan"])

        self.runtime.record_step("monitor", {"outcomes": len(outcomes)})
        trace = self.reasoning.chain(goal)
        context = self.context.build(goal=goal, steps=steps, routed_to=self.router.route(goal))
        summary = self.monitor.summary()

        return {
            "goal": goal,
            "plan": plan,
            "outcomes": outcomes,
            "reasoning": trace,
            "context": context,
            "monitor": summary,
            "runtime": self.runtime.finish(),
        }
