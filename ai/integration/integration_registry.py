"""
Integration Registry - Central registry for all integrations
"""
import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class RegistryEntry:
    entry_id: str
    name: str
    integration_type: str
    endpoint: str = ""
    status: str = "registered"
    capabilities: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    registered_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime | None = None
    access_count: int = 0


class IntegrationRegistry:
    def __init__(self):
        self.entries: dict[str, RegistryEntry] = {}
        self.categories: dict[str, list[str]] = {}
        self.aliases: dict[str, str] = {}

    def register(self, name: str, integration_type: str, endpoint: str = "", capabilities: list[str] = None, **kwargs) -> RegistryEntry:
        entry_id = hashlib.sha256(f"{name}{integration_type}".encode()).hexdigest()[:16]
        entry = RegistryEntry(entry_id=entry_id, name=name, integration_type=integration_type, endpoint=endpoint, capabilities=capabilities or [], metadata=kwargs)
        self.entries[entry_id] = entry
        return entry

    def unregister(self, entry_id: str) -> bool:
        if entry_id in self.entries:
            del self.entries[entry_id]
            return True
        return False

    def lookup(self, name: str) -> RegistryEntry | None:
        aliased = self.aliases.get(name, name)
        for entry in self.entries.values():
            if entry.name == aliased:
                entry.last_accessed = datetime.now()
                entry.access_count += 1
                return entry
        return None

    def lookup_by_id(self, entry_id: str) -> RegistryEntry | None:
        entry = self.entries.get(entry_id)
        if entry:
            entry.last_accessed = datetime.now()
            entry.access_count += 1
        return entry

    def add_alias(self, alias: str, canonical_name: str) -> None:
        self.aliases[alias] = canonical_name

    def categorize(self, entry_id: str, category: str) -> None:
        self.categories.setdefault(category, [])
        if entry_id not in self.categories[category]:
            self.categories[category].append(entry_id)

    def get_by_category(self, category: str) -> list[RegistryEntry]:
        ids = self.categories.get(category, [])
        return [self.entries[i] for i in ids if i in self.entries]

    def search(self, query: str) -> list[RegistryEntry]:
        return [e for e in self.entries.values() if query.lower() in e.name.lower() or query.lower() in e.integration_type.lower()]

    def list_all(self) -> list[RegistryEntry]:
        return list(self.entries.values())

    def get_by_type(self, integration_type: str) -> list[RegistryEntry]:
        return [e for e in self.entries.values() if e.integration_type == integration_type]

    def count(self) -> int:
        return len(self.entries)
