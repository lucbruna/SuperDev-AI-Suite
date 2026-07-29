from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime


@dataclass
class PluginManifest:
    name: str
    version: str
    description: str
    author: str
    license: str = "MIT"
    entry_point: str = ""
    dependencies: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)
    min_sdk_version: str = "1.0.0"
    tags: List[str] = field(default_factory=list)
    repository: Optional[str] = None
    homepage: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "license": self.license,
            "entry_point": self.entry_point,
            "dependencies": self.dependencies,
            "permissions": self.permissions,
            "min_sdk_version": self.min_sdk_version,
            "tags": self.tags,
            "repository": self.repository,
            "homepage": self.homepage,
        }
