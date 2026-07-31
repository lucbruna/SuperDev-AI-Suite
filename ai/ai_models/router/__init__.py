"""Router subsystem."""
from .ai_router import AIRouter
from .task_classifier import TaskClassifier
from .model_selector import ModelSelector
from .cost_optimizer import CostOptimizer
from .quality_optimizer import QualityOptimizer
from .latency_optimizer import LatencyOptimizer
from .fallback_manager import FallbackManager

__all__ = [
    "AIRouter", "TaskClassifier", "ModelSelector", "CostOptimizer",
    "QualityOptimizer", "LatencyOptimizer", "FallbackManager"
]
