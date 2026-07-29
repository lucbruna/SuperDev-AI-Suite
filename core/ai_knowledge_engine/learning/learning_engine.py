from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from .feedback_manager import FeedbackManager
from .experience_analyzer import ExperienceAnalyzer
from .improvement_engine import ImprovementEngine

logger = logging.getLogger(__name__)


class EngineState(Enum):
    STOPPED = "stopped"
    INITIALIZING = "initializing"
    RUNNING = "running"
    ERROR = "error"


@dataclass
class EngineConfig:
    max_learning_iterations: int = 10
    feedback_threshold: float = 0.5
    enable_auto_improve: bool = True
    experience_history_size: int = 100


@dataclass
class EngineMetrics:
    total_learning_cycles: int = 0
    active_learnings: int = 0
    completed_learnings: int = 0
    failed_learnings: int = 0
    improvements_applied: int = 0
    average_improvement_impact: float = 0.0


class LearningSession:
    def __init__(self, session_id: str, context: dict[str, Any]) -> None:
        self.session_id = session_id
        self.context = context
        self.feedback_log: list[dict[str, Any]] = []
        self.experiences: list[dict[str, Any]] = []
        self.improvements: list[dict[str, Any]] = []
        self.completed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "context": self.context,
            "feedback_count": len(self.feedback_log),
            "experience_count": len(self.experiences),
            "improvement_count": len(self.improvements),
            "completed": self.completed,
        }


class LearningEngine:
    def __init__(self, config: Optional[EngineConfig] = None) -> None:
        self.config = config or EngineConfig()
        self.state = EngineState.STOPPED
        self.metrics = EngineMetrics()
        self.feedback_manager = FeedbackManager()
        self.experience_analyzer = ExperienceAnalyzer()
        self.improvement_engine = ImprovementEngine()
        self._sessions: dict[str, LearningSession] = {}

    async def initialize(self) -> None:
        self.state = EngineState.INITIALIZING
        await self.feedback_manager.initialize()
        await self.experience_analyzer.initialize()
        await self.improvement_engine.initialize()
        self.state = EngineState.RUNNING
        logger.info("LearningEngine initialized")

    async def stop(self) -> None:
        self.state = EngineState.STOPPED
        self._sessions.clear()
        await self.feedback_manager.stop()
        await self.experience_analyzer.stop()
        await self.improvement_engine.stop()
        logger.info("LearningEngine stopped")

    async def learn(self, context: dict[str, Any], data: Any) -> dict[str, Any]:
        if self.state != EngineState.RUNNING:
            raise RuntimeError("LearningEngine is not running")

        session_id = str(uuid.uuid4())
        session = LearningSession(session_id=session_id, context=context)

        feedback = await self.feedback_manager.collect_feedback(context.get("source", "unknown"), data)
        session.feedback_log.append(feedback)

        experience = await self.experience_analyzer.analyze_experience(data, context)
        session.experiences.append(experience)

        improvements = await self.improvement_engine.identify_improvements(feedback, experience)
        session.improvements.extend(improvements)

        session.completed = True
        self._sessions[session_id] = session
        self.metrics.total_learning_cycles += 1
        self.metrics.completed_learnings += 1

        return {
            "session_id": session_id,
            "feedback": feedback,
            "experience": experience,
            "improvements": improvements,
        }

    async def apply_feedback(self, feedback_data: dict[str, Any]) -> dict[str, Any]:
        feedback_id = await self.feedback_manager.register_feedback(feedback_data)
        analysis = await self.feedback_manager.analyze_feedback(feedback_id)
        return {"feedback_id": feedback_id, "analysis": analysis}

    async def analyze_experience(self, experience_data: dict[str, Any]) -> dict[str, Any]:
        return await self.experience_analyzer.analyze_experience(
            experience_data.get("data"),
            experience_data.get("context", {}),
        )

    async def improve(self, target: str, changes: dict[str, Any]) -> dict[str, Any]:
        improvement = await self.improvement_engine.apply_improvement(target, changes)
        self.metrics.improvements_applied += 1
        return improvement

    async def get_learning_stats(self) -> dict[str, Any]:
        feedback_summary = await self.feedback_manager.get_feedback_summary()
        improvement_history = await self.improvement_engine.get_improvement_history()
        return {
            "metrics": {
                "total_learning_cycles": self.metrics.total_learning_cycles,
                "completed_learnings": self.metrics.completed_learnings,
                "improvements_applied": self.metrics.improvements_applied,
            },
            "feedback_summary": feedback_summary,
            "improvement_history": improvement_history,
            "active_sessions": len(self._sessions),
        }

    def get_session(self, session_id: str) -> Optional[LearningSession]:
        return self._sessions.get(session_id)
