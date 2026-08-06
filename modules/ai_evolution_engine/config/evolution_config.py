"""Root configuration for the AI Evolution Engine."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from modules.ai_evolution_engine.config._env import env_bool, env_int, env_str
from modules.ai_evolution_engine.config.forecast_config import ForecastConfig
from modules.ai_evolution_engine.config.governance_config import GovernanceConfig
from modules.ai_evolution_engine.config.learning_config import LearningConfig
from modules.ai_evolution_engine.config.optimization_config import (
    OptimizationConfig,
)
from modules.ai_evolution_engine.config.recommendation_config import (
    RecommendationConfig,
)


@dataclass(slots=True)
class EvolutionConfig:
    """Deterministic configuration of the AI Evolution Engine."""

    name: str = "ai_evolution_engine"
    version: int = 1
    enabled: bool = True
    analysis_interval_ticks: int = 24
    forecast_horizon: int = 12
    max_recommendations_per_cycle: int = 20
    learning_enabled: bool = True
    project_root: str = ""
    data_dir: str = ""
    logs_dir: str = ""
    memory_file: str = ""
    forecast: ForecastConfig = field(default_factory=ForecastConfig)
    governance: GovernanceConfig = field(default_factory=GovernanceConfig)
    learning: LearningConfig = field(default_factory=LearningConfig)
    optimization: OptimizationConfig = field(default_factory=OptimizationConfig)
    recommendation: RecommendationConfig = field(
        default_factory=RecommendationConfig
    )

    def resolve(self, project_root: str | Path | None = None) -> None:
        """Resolve filesystem paths. Deterministic when inputs are given."""
        root = str(project_root) if project_root else env_str("SUPERDEV_ROOT")
        if not root:
            root = str(Path.cwd())
        self.project_root = root

        base = Path(root) / ".superdev" / "ai_evolution_engine"
        if env_str("SUPERDEV_DATA_DIR"):
            base = Path(env_str("SUPERDEV_DATA_DIR")) / "ai_evolution_engine"

        self.data_dir = env_str(
            "AI_EVOLUTION_DATA_DIR", str(base)
        )
        self.logs_dir = env_str(
            "AI_EVOLUTION_LOGS_DIR", str(base / "logs")
        )
        self.memory_file = env_str(
            "AI_EVOLUTION_MEMORY_FILE", str(base / "evolution_memory.json")
        )
