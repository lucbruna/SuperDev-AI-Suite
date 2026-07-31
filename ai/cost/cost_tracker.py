from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass

from .provider_cost import calculate_cost


@dataclass
class CostEntry:
    provider: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    cost: float
    timestamp: float
    session_id: str = ""
    project_id: str = ""


class CostTracker:
    def __init__(self):
        self._entries: list[CostEntry] = []
        self._session_costs: dict[str, float] = defaultdict(float)
        self._project_costs: dict[str, float] = defaultdict(float)
        self._total_cost: float = 0.0

    def track(
        self,
        provider: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        session_id: str = "",
        project_id: str = "",
    ) -> CostEntry:
        cost = calculate_cost(provider, model, prompt_tokens, completion_tokens)
        entry = CostEntry(
            provider=provider,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cost=cost,
            timestamp=time.time(),
            session_id=session_id,
            project_id=project_id,
        )
        self._entries.append(entry)
        self._total_cost += cost
        if session_id:
            self._session_costs[session_id] += cost
        if project_id:
            self._project_costs[project_id] += cost
        return entry

    def get_session_cost(self, session_id: str) -> float:
        return self._session_costs.get(session_id, 0.0)

    def get_project_cost(self, project_id: str) -> float:
        return self._project_costs.get(project_id, 0.0)

    def get_total_cost(self) -> float:
        return self._total_cost

    def get_entries(self, limit: int = 100) -> list[CostEntry]:
        return self._entries[-limit:]

    def get_provider_cost(self, provider: str) -> float:
        return sum(e.cost for e in self._entries if e.provider == provider)

    def get_model_cost(self, model: str) -> float:
        return sum(e.cost for e in self._entries if e.model == model)

    def reset(self) -> None:
        self._entries.clear()
        self._session_costs.clear()
        self._project_costs.clear()
        self._total_cost = 0.0
