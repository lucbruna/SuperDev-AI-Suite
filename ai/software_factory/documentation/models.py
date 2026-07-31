"""Data models for documentation."""
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class DocType(Enum):
    README = "readme"
    API = "api"
    GUIDE = "guide"
    TUTORIAL = "tutorial"
    REFERENCE = "reference"
    CHANGELOG = "changelog"
    ARCHITECTURE = "architecture"


@dataclass
class DocSection:
    """A section in a documentation page."""
    section_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str = ""
    content: str = ""
    level: int = 1
    subsections: list["DocSection"] = field(default_factory=list)

    def add_subsection(self, subsection: "DocSection") -> None:
        self.subsections.append(subsection)

    def to_markdown(self) -> str:
        prefix = "#" * self.level
        lines = [f"{prefix} {self.title}", "", self.content]
        for sub in self.subsections:
            lines.append("")
            lines.append(sub.to_markdown())
        return "\n".join(lines)


@dataclass
class DocPage:
    """A documentation page."""
    page_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str = ""
    doc_type: DocType = DocType.GUIDE
    sections: list[DocSection] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def add_section(self, section: DocSection) -> None:
        self.sections.append(section)

    def to_markdown(self) -> str:
        lines = [f"# {self.title}", ""]
        for section in self.sections:
            lines.append(section.to_markdown())
            lines.append("")
        return "\n".join(lines)


@dataclass
class ApiParameter:
    """A parameter in an API endpoint."""
    name: str = ""
    location: str = "query"
    type: str = "string"
    required: bool = False
    description: str = ""
    default: Any = None


@dataclass
class ApiEndpoint:
    """An API endpoint documentation entry."""
    endpoint_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    path: str = ""
    method: str = "GET"
    summary: str = ""
    description: str = ""
    parameters: list[ApiParameter] = field(default_factory=list)
    response_example: str = ""
    tags: list[str] = field(default_factory=list)


@dataclass
class ChangelogEntry:
    """An entry in the changelog."""
    entry_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    version: str = ""
    date: datetime = field(default_factory=datetime.utcnow)
    changes: list[str] = field(default_factory=list)
    breaking: list[str] = field(default_factory=list)
    deprecations: list[str] = field(default_factory=list)


@dataclass
class DocumentationConfig:
    """Configuration for documentation generation."""
    config_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    project_name: str = ""
    output_dir: str = "docs"
    format: str = "markdown"
    include_api: bool = True
    include_guides: bool = True
    include_changelog: bool = True
    template_vars: dict[str, Any] = field(default_factory=dict)
