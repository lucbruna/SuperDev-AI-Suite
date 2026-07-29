from __future__ import annotations

import time
import uuid
from typing import Any

PLAN_TEMPLATES: dict[str, list[dict[str, str]]] = {
    "machine learning": [
        {"order": "1", "description": "survey existing ML frameworks", "estimated_minutes": 15},
        {"order": "2", "description": "analyze training methodologies", "estimated_minutes": 20},
        {"order": "3", "description": "evaluate performance metrics", "estimated_minutes": 10},
    ],
    "quantum computing": [
        {"order": "1", "description": "review quantum algorithms", "estimated_minutes": 20},
        {"order": "2", "description": "analyze hardware platforms", "estimated_minutes": 15},
        {"order": "3", "description": "compare error correction schemes", "estimated_minutes": 15},
    ],
}


class ResearchPlanner:
    def __init__(self) -> None:
        self._plans: dict[str, dict[str, Any]] = {}

    async def create_plan(self, topic: str) -> dict[str, Any]:
        plan_id = f"plan_{uuid.uuid4().hex[:8]}"
        normalized = topic.lower().strip()
        steps = PLAN_TEMPLATES.get(normalized)

        if steps is None:
            for key, template in PLAN_TEMPLATES.items():
                if any(word in normalized for word in key.split()):
                    steps = template
                    break

        if steps is None:
            steps = [
                {"order": "1", "description": f"gather information about {topic}", "estimated_minutes": 10},
                {"order": "2", "description": f"analyze findings on {topic}", "estimated_minutes": 10},
                {"order": "3", "description": f"synthesize results for {topic}", "estimated_minutes": 10},
            ]

        plan = {
            "plan_id": plan_id,
            "topic": topic,
            "steps": steps,
            "status": "created",
            "created_at": time.time(),
            "completed_steps": 0,
        }
        self._plans[plan_id] = plan
        return plan

    async def add_step(self, plan_id: str, description: str, estimated_minutes: int = 10) -> dict[str, Any]:
        plan = self._plans.get(plan_id)
        if plan is None:
            raise KeyError(f"Plan '{plan_id}' not found")
        new_step = {
            "order": str(len(plan["steps"]) + 1),
            "description": description,
            "estimated_minutes": estimated_minutes,
        }
        plan["steps"].append(new_step)
        return plan

    async def execute_plan(self, plan_id: str) -> dict[str, Any]:
        plan = self._plans.get(plan_id)
        if plan is None:
            raise KeyError(f"Plan '{plan_id}' not found")
        plan["status"] = "completed"
        plan["completed_steps"] = len(plan["steps"])
        plan["completed_at"] = time.time()
        return plan

    async def get_plan_status(self, plan_id: str) -> dict[str, Any]:
        plan = self._plans.get(plan_id)
        if plan is None:
            raise KeyError(f"Plan '{plan_id}' not found")
        return {
            "plan_id": plan["plan_id"],
            "status": plan["status"],
            "total_steps": len(plan["steps"]),
            "completed_steps": plan["completed_steps"],
            "progress_pct": round(plan["completed_steps"] / len(plan["steps"]) * 100, 1) if plan["steps"] else 100.0,
        }

    async def estimate_completion(self, plan_id: str) -> dict[str, Any]:
        plan = self._plans.get(plan_id)
        if plan is None:
            raise KeyError(f"Plan '{plan_id}' not found")
        remaining = plan["steps"][plan["completed_steps"]:]
        total_minutes = sum(s.get("estimated_minutes", 10) for s in remaining)
        return {
            "plan_id": plan_id,
            "remaining_steps": len(remaining),
            "estimated_minutes": total_minutes,
        }