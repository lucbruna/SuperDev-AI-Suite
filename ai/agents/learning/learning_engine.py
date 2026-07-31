"""Learning engine for agent adaptive improvement."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from .transfer import TransferLearning
from .adaptation import AdaptationEngine
from .knowledge_sharing import KnowledgeSharing
from .experience_replay import ExperienceReplay
from .meta_learning import MetaLearner


class LearningEngine:
    """Central engine for agent learning, adaptation, and knowledge transfer."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self._config = config or {}
        self._transfer = TransferLearning()
        self._adaptation = AdaptationEngine()
        self._knowledge = KnowledgeSharing()
        self._replay = ExperienceReplay()
        self._meta = MetaLearner()
        self._learning_count: int = 0

    def learn_from_experience(self, experience: Dict[str, Any]) -> Dict[str, Any]:
        self._learning_count += 1
        self._replay.store(experience)
        adapted = self._adaptation.adapt(experience)
        return {"status": "learned", "adaptation": adapted, "experience_count": self._replay.count()}

    def transfer_knowledge(self, source_domain: str, target_domain: str) -> Dict[str, Any]:
        return self._transfer.transfer(source_domain, target_domain)

    def share_knowledge(self, agent_id: str, knowledge: Dict[str, Any]) -> Dict[str, Any]:
        return self._knowledge.share(agent_id, knowledge)

    def get_shared_knowledge(self, topic: Optional[str] = None) -> List[Dict[str, Any]]:
        return self._knowledge.retrieve(topic)

    def meta_analyze(self) -> Dict[str, Any]:
        return self._meta.analyze(self._replay.get_all())

    def get_metrics(self) -> Dict[str, Any]:
        return {
            "total_learning_events": self._learning_count,
            "experiences_stored": self._replay.count(),
            "shared_knowledge_count": self._knowledge.count(),
        }
