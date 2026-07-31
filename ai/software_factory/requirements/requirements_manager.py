"""Manager for requirement sets and lifecycle operations."""
from typing import List, Dict, Any, Optional
from datetime import datetime
from .models import (
    Requirement, RequirementSet, RequirementType, Priority,
    RequirementStatus, RequirementLink, RequirementChange,
)


class RequirementsManager:
    """Manages requirement sets, links, and change history."""

    def __init__(self):
        self._sets: Dict[str, RequirementSet] = {}
        self._links: List[RequirementLink] = []
        self._changes: List[RequirementChange] = []

    def create_set(self, name: str, description: str = "") -> RequirementSet:
        rs = RequirementSet(name=name, description=description)
        self._sets[rs.set_id] = rs
        return rs

    def get_set(self, set_id: str) -> Optional[RequirementSet]:
        return self._sets.get(set_id)

    def add_requirement(self, set_id: str, req: Requirement) -> bool:
        rs = self._sets.get(set_id)
        if not rs:
            return False
        rs.add_requirement(req)
        return True

    def create_link(self, source_id: str, target_id: str, link_type: str = "depends_on") -> RequirementLink:
        link = RequirementLink(source_id=source_id, target_id=target_id, link_type=link_type)
        self._links.append(link)
        return link

    def get_links_for(self, req_id: str) -> List[RequirementLink]:
        return [l for l in self._links if l.source_id == req_id or l.target_id == req_id]

    def record_change(self, change: RequirementChange) -> None:
        self._changes.append(change)

    def get_changes_for(self, req_id: str) -> List[RequirementChange]:
        return [c for c in self._changes if c.requirement_id == req_id]

    def approve_requirement(self, req: Requirement) -> None:
        old_status = req.status
        req.approve()
        self.record_change(RequirementChange(
            requirement_id=req.requirement_id,
            field_name="status",
            old_value=old_status.value,
            new_value=req.status.value,
        ))

    def get_all_sets(self) -> List[RequirementSet]:
        return list(self._sets.values())

    def get_statistics(self) -> Dict[str, Any]:
        total_reqs = sum(rs.total_count() for rs in self._sets.values())
        approved = sum(rs.approved_count() for rs in self._sets.values())
        return {
            "total_sets": len(self._sets),
            "total_requirements": total_reqs,
            "approved": approved,
            "pending": total_reqs - approved,
            "links": len(self._links),
            "changes": len(self._changes),
        }
