"""
Skill Graph - Map skills relationships and talent networks.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Set

from ..employee_context import EmployeeContext
from ..hr_events import HREventBus
from ..hr_models import Skill, SkillLevel
from ..hr_config import HRConfig

logger = logging.getLogger(__name__)


class SkillGraph:
    def __init__(self, config: HRConfig, context: EmployeeContext, event_bus: HREventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self._graph: Dict[str, Set[str]] = {}

    def add_relationship(self, skill_a: str, skill_b: str) -> None:
        if skill_a not in self._graph:
            self._graph[skill_a] = set()
        if skill_b not in self._graph:
            self._graph[skill_b] = set()
        self._graph[skill_a].add(skill_b)
        self._graph[skill_b].add(skill_a)

    def find_related_skills(self, skill: str, depth: int = 2) -> List[str]:
        visited = {skill}
        related = []
        queue = [skill]
        for _ in range(depth):
            next_queue = []
            for s in queue:
                for neighbor in self._graph.get(s, set()):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        related.append(neighbor)
                        next_queue.append(neighbor)
            queue = next_queue
        return related

    def get_skill_gap_analysis(self, employee_skills: List[str], required_skills: List[str]) -> Dict[str, Any]:
        missing = [s for s in required_skills if s not in employee_skills]
        return {
            "current_skills": employee_skills,
            "required_skills": required_skills,
            "missing_skills": missing,
            "gap_percent": (len(missing) / max(len(required_skills), 1)) * 100,
        }
