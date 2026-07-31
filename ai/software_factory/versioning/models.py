"""Data models for version management."""
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class VersionType(Enum):
    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"
    PRE_RELEASE = "pre_release"
    BUILD = "build"


@dataclass
class Version:
    major: int = 0
    minor: int = 0
    patch: int = 0
    pre_release: str = ""
    build: str = ""

    def __str__(self) -> str:
        v = f"{self.major}.{self.minor}.{self.patch}"
        if self.pre_release:
            v += f"-{self.pre_release}"
        if self.build:
            v += f"+{self.build}"
        return v

    def bump_major(self) -> "Version":
        return Version(major=self.major + 1)

    def bump_minor(self) -> "Version":
        return Version(major=self.major, minor=self.minor + 1)

    def bump_patch(self) -> "Version":
        return Version(major=self.major, minor=self.minor, patch=self.patch + 1)

    def to_tuple(self) -> tuple[int, int, int]:
        return (self.major, self.minor, self.patch)

    def __lt__(self, other: "Version") -> bool:
        return self.to_tuple() < other.to_tuple()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Version):
            return False
        return self.to_tuple() == other.to_tuple()

    @classmethod
    def parse(cls, version_str: str) -> "Version":
        v = cls()
        base_part = version_str.split("-")[0].split("+")[0]
        parts = base_part.split(".")
        if len(parts) >= 1:
            v.major = int(parts[0])
        if len(parts) >= 2:
            v.minor = int(parts[1])
        if len(parts) >= 3:
            v.patch = int(parts[2])
        if "-" in version_str:
            v.pre_release = version_str.split("-")[1].split("+")[0]
        if "+" in version_str:
            v.build = version_str.split("+")[1]
        return v


@dataclass
class Branch:
    branch_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    source_branch: str = ""
    is_protected: bool = False
    is_merged: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Tag:
    tag_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    version: str = ""
    message: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DependencyGraph:
    graph_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    nodes: list[str] = field(default_factory=list)
    edges: list[dict[str, str]] = field(default_factory=list)

    def add_node(self, name: str) -> None:
        if name not in self.nodes:
            self.nodes.append(name)

    def add_edge(self, source: str, target: str, constraint: str = "") -> None:
        self.edges.append({"source": source, "target": target, "constraint": constraint})

    def get_dependencies(self, name: str) -> list[str]:
        return [e["target"] for e in self.edges if e["source"] == name]

    def get_dependents(self, name: str) -> list[str]:
        return [e["source"] for e in self.edges if e["target"] == name]


@dataclass
class VersionConstraint:
    name: str = ""
    min_version: str = ""
    max_version: str = ""
    exact_version: str = ""
    allowed_versions: list[str] = field(default_factory=list)

    def satisfies(self, version_str: str) -> bool:
        if self.exact_version:
            return version_str == self.exact_version
        if self.allowed_versions:
            return version_str in self.allowed_versions
        ver = Version.parse(version_str)
        if self.min_version and ver < Version.parse(self.min_version):
            return False
        return not (self.max_version and ver > Version.parse(self.max_version))
