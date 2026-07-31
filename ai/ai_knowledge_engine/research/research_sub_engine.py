"""Research subsystem engine — Intelligent research and information collection."""
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class SourceType(Enum):
    WEB = "web"
    DOCUMENT = "document"
    DATABASE = "database"
    API = "api"
    ACADEMIC = "academic"


class ResearchPhase(Enum):
    PLANNING = "planning"
    COLLECTION = "collection"
    ANALYSIS = "analysis"
    SYNTHESIS = "synthesis"
    REPORTING = "reporting"


@dataclass
class Source:
    source_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    url: str = ""
    source_type: SourceType = SourceType.WEB
    reliability: float = 0.5
    last_checked: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Information:
    info_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str = ""
    content: str = ""
    source_id: str = ""
    relevance: float = 0.0
    confidence: float = 0.5
    tags: list[str] = field(default_factory=list)
    collected_at: datetime = field(default_factory=datetime.now)


@dataclass
class ResearchSession:
    session_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    topic: str = ""
    phase: ResearchPhase = ResearchPhase.PLANNING
    sources: list[Source] = field(default_factory=list)
    findings: list[Information] = field(default_factory=list)
    report: str = ""
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: datetime | None = None


class ResearchSubEngine:
    def __init__(self):
        self._sessions: dict[str, ResearchSession] = {}
        self._sources: dict[str, Source] = {}
        self._information: dict[str, Information] = {}
        self._queries: list[dict[str, Any]] = []

    def start_session(self, topic: str) -> ResearchSession:
        session = ResearchSession(topic=topic)
        self._sessions[session.session_id] = session
        return session

    def get_session(self, session_id: str) -> ResearchSession | None:
        return self._sessions.get(session_id)

    def add_source(self, source: Source) -> Source:
        self._sources[source.source_id] = source
        return source

    def get_source(self, source_id: str) -> Source | None:
        return self._sources.get(source_id)

    def add_information(self, info: Information) -> Information:
        self._information[info.info_id] = info
        return info

    def get_information(self, info_id: str) -> Information | None:
        return self._information.get(info_id)

    def collect_information(self, session_id: str, title: str, content: str, source_id: str = "", relevance: float = 0.5) -> Information | None:
        session = self._sessions.get(session_id)
        if not session:
            return None
        info = Information(title=title, content=content, source_id=source_id, relevance=relevance)
        session.findings.append(info)
        self._information[info.info_id] = info
        return info

    def advance_phase(self, session_id: str) -> bool:
        session = self._sessions.get(session_id)
        if not session:
            return False
        phases = list(ResearchPhase)
        idx = phases.index(session.phase)
        if idx < len(phases) - 1:
            session.phase = phases[idx + 1]
            if session.phase == ResearchPhase.REPORTING:
                session.report = f"Research on {session.topic}: {len(session.findings)} findings"
            return True
        session.completed_at = datetime.now()
        return True

    def search_information(self, query: str) -> list[Information]:
        query_lower = query.lower()
        return [i for i in self._information.values() if query_lower in i.title.lower() or query_lower in i.content.lower()]

    def get_top_findings(self, session_id: str, limit: int = 5) -> list[Information]:
        session = self._sessions.get(session_id)
        if not session:
            return []
        return sorted(session.findings, key=lambda f: f.relevance, reverse=True)[:limit]

    def get_stats(self) -> dict:
        return {
            "total_sessions": len(self._sessions),
            "total_sources": len(self._sources),
            "total_information": len(self._information),
            "completed_sessions": len([s for s in self._sessions.values() if s.completed_at]),
        }
