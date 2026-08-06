"""Workflow parser — CI/CD workflow descriptors (workflows/*.yml|yaml)."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from modules.ai_code_knowledge_graph.ast.entities import file_entity, make_entity
from modules.ai_code_knowledge_graph.ast.entities import KIND_WORKFLOW
from modules.ai_code_knowledge_graph.parsers.base_parser import (
    line_count,
    load_yaml,
    parse_result,
    walk_mapping,
)


def _triggers(data: dict[Any, Any]) -> list[Any]:
    # PyYAML (YAML 1.1) coerces the ``on`` key to boolean True.
    triggers = data.get("on") or data.get("triggers") or data.get(True) or []
    if isinstance(triggers, dict):
        return list(triggers)
    if isinstance(triggers, str):
        return [triggers]
    return triggers if isinstance(triggers, list) else []


def parse(text: str, rel_path: str = "") -> dict[str, Any]:
    """Parse a workflow descriptor into a workflow entity + config entities."""
    total_lines = line_count(text)
    entities: list[dict[str, Any]] = [file_entity(rel_path or "<string>", total_lines)]

    data = load_yaml(text)
    if isinstance(data, dict):
        jobs = data.get("jobs") or data.get("workflows") or {}
        job_names = list(jobs) if isinstance(jobs, dict) else []
        steps = 0
        if isinstance(jobs, dict):
            for job in jobs.values():
                if isinstance(job, dict):
                    steps += len(job.get("steps") or [])
        entities.append(
            make_entity(
                KIND_WORKFLOW,
                str(data.get("name") or Path(rel_path).stem),
                1,
                max(total_lines, 1),
                triggers=_triggers(data),
                jobs=job_names,
                steps=steps,
            )
        )
        walk_mapping("", data, entities)
    else:
        entities.append(make_entity(KIND_WORKFLOW, Path(rel_path).stem, 1, max(total_lines, 1)))

    return parse_result("workflow", rel_path, entities)
