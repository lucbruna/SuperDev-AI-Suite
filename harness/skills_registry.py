"""Skills registry - maps skills to agent types and domains."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .config import AgentDomain


@dataclass
class SkillMapping:
    """Maps a skill to its domain, agents, and metadata."""

    skill_id: str
    name: str
    domain: AgentDomain
    description: str
    skill_path: str  # Path to SKILL.md
    version: str = "1.0.0"
    author: str = "SuperDev Ultra Harness"
    tags: list[str] = field(default_factory=list)
    required_tools: list[str] = field(default_factory=list)
    depends_on: list[str] = field(default_factory=list)
    enabled: bool = True


class SkillsRegistry:
    """Registry of all harness skills with their mappings."""

    def __init__(self, skills_base_dir: str | Path | None = None) -> None:
        self._skills: dict[str, SkillMapping] = {}
        self._by_domain: dict[AgentDomain, list[SkillMapping]] = {d: [] for d in AgentDomain}
        if skills_base_dir:
            self._skills_base = Path(skills_base_dir)
        else:
            self._skills_base = Path.home() / ".agents" / "skills"
        self._register_defaults()

    def _register_defaults(self) -> None:
        """Register all default harness skills."""
        skills = [
            # === ENVIRONMENT ENGINEERING ===
            SkillMapping(
                skill_id="superdev-docker-orchestration",
                name="Docker Orchestration",
                domain=AgentDomain.ENVIRONMENT,
                description="Expert in Docker containerization, multi-stage builds, compose files, and container security",
                skill_path=str(self._skills_base / "superdev-docker-orchestration" / "SKILL.md"),
                tags=["docker", "containers", "devops"],
                required_tools=["read_file", "write_file", "execute_code"],
            ),
            SkillMapping(
                skill_id="superdev-kubernetes-deploy",
                name="Kubernetes Deployment",
                domain=AgentDomain.ENVIRONMENT,
                description="Expert in Kubernetes deployments, Helm charts, Kustomize, and cluster management",
                skill_path=str(self._skills_base / "superdev-kubernetes-deploy" / "SKILL.md"),
                tags=["kubernetes", "k8s", "helm", "devops"],
                required_tools=["read_file", "write_file", "execute_code"],
            ),
            SkillMapping(
                skill_id="superdev-cicd-pipeline",
                name="CI/CD Pipeline Engineering",
                domain=AgentDomain.ENVIRONMENT,
                description="Expert in GitHub Actions, GitLab CI, Jenkins, and ArgoCD pipeline design",
                skill_path=str(self._skills_base / "superdev-cicd-pipeline" / "SKILL.md"),
                tags=["ci-cd", "github-actions", "automation"],
                required_tools=["read_file", "write_file", "execute_code"],
            ),

            # === APK/MOBILE ===
            SkillMapping(
                skill_id="superdev-apk-builder",
                name="APK Builder",
                domain=AgentDomain.MOBILE,
                description="Expert in Android APK/AAB building, signing, optimization, and Play Store deployment",
                skill_path=str(self._skills_base / "superdev-apk-builder" / "SKILL.md"),
                tags=["android", "apk", "gradle", "mobile"],
                required_tools=["read_file", "write_file", "execute_code"],
            ),
            SkillMapping(
                skill_id="superdev-flutter-dev",
                name="Flutter Development",
                domain=AgentDomain.MOBILE,
                description="Expert in Flutter/Dart cross-platform development, state management, and widget architecture",
                skill_path=str(self._skills_base / "superdev-flutter-dev" / "SKILL.md"),
                tags=["flutter", "dart", "cross-platform", "mobile"],
                required_tools=["read_file", "write_file", "execute_code"],
            ),
            SkillMapping(
                skill_id="superdev-react-native-dev",
                name="React Native Development",
                domain=AgentDomain.MOBILE,
                description="Expert in React Native/Expo cross-platform mobile development and native modules",
                skill_path=str(self._skills_base / "superdev-react-native-dev" / "SKILL.md"),
                tags=["react-native", "expo", "javascript", "mobile"],
                required_tools=["read_file", "write_file", "execute_code"],
            ),

            # === ARCHITECTURE ===
            SkillMapping(
                skill_id="superdev-system-design",
                name="System Design",
                domain=AgentDomain.ARCHITECTURE,
                description="Expert in distributed system design, scalability patterns, and architecture decision records",
                skill_path=str(self._skills_base / "superdev-system-design" / "SKILL.md"),
                tags=["system-design", "distributed-systems", "architecture"],
                required_tools=["read_file", "write_file", "list_files", "search_code"],
            ),
            SkillMapping(
                skill_id="superdev-microservices",
                name="Microservices Architecture",
                domain=AgentDomain.ARCHITECTURE,
                description="Expert in microservices patterns, service boundaries, API gateways, and inter-service communication",
                skill_path=str(self._skills_base / "superdev-microservices" / "SKILL.md"),
                tags=["microservices", "api-gateway", "service-mesh"],
                required_tools=["read_file", "write_file", "list_files", "search_code"],
            ),
            SkillMapping(
                skill_id="superdev-event-driven",
                name="Event-Driven Architecture",
                domain=AgentDomain.ARCHITECTURE,
                description="Expert in event-driven systems, CQRS, event sourcing, and messaging platforms",
                skill_path=str(self._skills_base / "superdev-event-driven" / "SKILL.md"),
                tags=["event-driven", "cqrs", "kafka", "messaging"],
                required_tools=["read_file", "write_file", "list_files", "search_code"],
            ),

            # === AUTONOMOUS (AFK) ===
            SkillMapping(
                skill_id="superdev-autonomous-executor",
                name="Autonomous Task Executor",
                domain=AgentDomain.AUTONOMOUS,
                description="Self-directed task execution with planning, reasoning, goal decomposition, and self-correction",
                skill_path=str(self._skills_base / "superdev-autonomous-executor" / "SKILL.md"),
                tags=["autonomous", "planning", "reasoning", "afk"],
                required_tools=["read_file", "write_file", "execute_code", "search_code", "list_files"],
            ),
            SkillMapping(
                skill_id="superdev-self-healing",
                name="Self-Healing Systems",
                domain=AgentDomain.AUTONOMOUS,
                description="Fault detection, auto-remediation, rollback strategies, and resilience patterns",
                skill_path=str(self._skills_base / "superdev-self-healing" / "SKILL.md"),
                tags=["self-healing", "resilience", "auto-remediation"],
                required_tools=["read_file", "write_file", "execute_code", "search_code"],
            ),
            SkillMapping(
                skill_id="superdev-continuous-ops",
                name="Continuous Operations",
                domain=AgentDomain.AUTONOMOUS,
                description="SRE practices, incident response, runbook automation, and chaos engineering",
                skill_path=str(self._skills_base / "superdev-continuous-ops" / "SKILL.md"),
                tags=["sre", "incident-response", "runbook", "chaos"],
                required_tools=["read_file", "write_file", "execute_code", "search_code", "list_files"],
            ),

            # === EXPERIENCE/UX ===
            SkillMapping(
                skill_id="superdev-ux-engineering",
                name="UX Engineering",
                domain=AgentDomain.EXPERIENCE,
                description="UX best practices, interaction patterns, user research integration, and usability engineering",
                skill_path=str(self._skills_base / "superdev-ux-engineering" / "SKILL.md"),
                tags=["ux", "interaction-design", "usability"],
                required_tools=["read_file", "write_file", "search_code", "list_files"],
            ),
            SkillMapping(
                skill_id="superdev-design-system",
                name="Design System Architecture",
                domain=AgentDomain.EXPERIENCE,
                description="Design system creation, component libraries, design tokens, and Storybook documentation",
                skill_path=str(self._skills_base / "superdev-design-system" / "SKILL.md"),
                tags=["design-system", "components", "tokens", "storybook"],
                required_tools=["read_file", "write_file", "search_code", "list_files"],
            ),
            SkillMapping(
                skill_id="superdev-perf-ux",
                name="Performance UX Engineering",
                domain=AgentDomain.EXPERIENCE,
                description="Core Web Vitals optimization, bundle analysis, lazy loading, and runtime performance",
                skill_path=str(self._skills_base / "superdev-perf-ux" / "SKILL.md"),
                tags=["performance", "core-vitals", "lighthouse", "optimization"],
                required_tools=["read_file", "write_file", "execute_code", "search_code"],
            ),
        ]

        for skill in skills:
            self.register(skill)

    def register(self, skill: SkillMapping) -> None:
        self._skills[skill.skill_id] = skill
        self._by_domain[skill.domain].append(skill)

    def get(self, skill_id: str) -> SkillMapping | None:
        return self._skills.get(skill_id)

    def list_all(self) -> list[SkillMapping]:
        return list(self._skills.values())

    def list_by_domain(self, domain: AgentDomain) -> list[SkillMapping]:
        return list(self._by_domain.get(domain, []))

    def find_by_tags(self, tags: list[str]) -> list[SkillMapping]:
        tag_set = set(tags)
        return [s for s in self._skills.values() if tag_set.intersection(s.tags)]

    def get_skill_content(self, skill_id: str) -> str | None:
        """Read the SKILL.md content for a skill."""
        skill = self._skills.get(skill_id)
        if not skill:
            return None
        path = Path(skill.skill_path)
        if not path.exists():
            return None
        return path.read_text(encoding="utf-8")

    def count(self) -> int:
        return len(self._skills)

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_skills": self.count(),
            "by_domain": {
                domain.value: len(skills)
                for domain, skills in self._by_domain.items()
            },
            "skills": [
                {
                    "skill_id": s.skill_id,
                    "name": s.name,
                    "domain": s.domain.value,
                    "tags": s.tags,
                    "enabled": s.enabled,
                }
                for s in self._skills.values()
            ],
        }
