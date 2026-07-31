"""
Access Control
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum


class AccessLevel(Enum):
    NONE = "none"
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"
    OWNER = "owner"


@dataclass
class AccessEntry:
    subject: str
    resource: str
    level: AccessLevel
    granted_by: str = ""
    expires_at: Optional[str] = None


class AccessControl:
    def __init__(self):
        self.entries: List[AccessEntry] = []
        
    def grant(self, subject: str, resource: str, level: AccessLevel, granted_by: str = "") -> AccessEntry:
        entry = AccessEntry(subject=subject, resource=resource, level=level, granted_by=granted_by)
        self.entries.append(entry)
        return entry
        
    def revoke(self, subject: str, resource: str) -> bool:
        for i, entry in enumerate(self.entries):
            if entry.subject == subject and entry.resource == resource:
                self.entries.pop(i)
                return True
        return False
        
    def check(self, subject: str, resource: str, required_level: AccessLevel) -> bool:
        level_order = [AccessLevel.NONE, AccessLevel.READ, AccessLevel.WRITE, AccessLevel.ADMIN, AccessLevel.OWNER]
        required_idx = level_order.index(required_level)
        for entry in self.entries:
            if entry.subject == subject and entry.resource == resource:
                entry_idx = level_order.index(entry.level)
                if entry_idx >= required_idx:
                    return True
        return False
        
    def get_access(self, subject: str, resource: str) -> Optional[AccessLevel]:
        for entry in reversed(self.entries):
            if entry.subject == subject and entry.resource == resource:
                return entry.level
        return None
        
    def list_entries(self, subject: str = None, resource: str = None) -> List[AccessEntry]:
        entries = self.entries
        if subject:
            entries = [e for e in entries if e.subject == subject]
        if resource:
            entries = [e for e in entries if e.resource == resource]
        return entries
        
    def count(self) -> int:
        return len(self.entries)
