"""Harness configuration - master config for all agent domains."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AgentDomain(Enum):
    """The five core agent domains in the Ultra Harness."""

    ENVIRONMENT = "environment"
    MOBILE = "mobile"
    ARCHITECTURE = "architecture"
    AUTONOMOUS = "autonomous"
    EXPERIENCE = "experience"


@dataclass
class DomainConfig:
    """Configuration for a single agent domain."""

    domain: AgentDomain
    display_name: str
    description: str
    skills: list[str] = field(default_factory=list)
    capabilities: list[str] = field(default_factory=list)
    max_concurrent_agents: int = 5
    timeout_seconds: int = 300
    retry_count: int = 3
    enabled: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class HarnessConfig:
    """Master configuration for the Ultra Harness."""

    version: str = "1.0.0"
    project_name: str = "SuperDev Ultra Harness"
    max_total_agents: int = 25
    default_timeout: int = 600
    log_level: str = "INFO"
    domains: dict[str, DomainConfig] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.domains:
            self.domains = self._default_domains()

    def _default_domains(self) -> dict[str, DomainConfig]:
        return {
            AgentDomain.ENVIRONMENT.value: DomainConfig(
                domain=AgentDomain.ENVIRONMENT,
                display_name="Environment Engineering",
                description="Container orchestration, infrastructure as code, and deployment pipelines",
                skills=[
                    "superdev-docker-orchestration",
                    "superdev-kubernetes-deploy",
                    "superdev-cicd-pipeline",
                ],
                capabilities=[
                    "docker", "kubernetes", "helm", "terraform", "ansible",
                    "github-actions", "gitlab-ci", "jenkins", "argocd",
                    "containerization", "service-mesh", "monitoring",
                ],
                max_concurrent_agents=5,
            ),
            AgentDomain.MOBILE.value: DomainConfig(
                domain=AgentDomain.MOBILE,
                display_name="APK/Mobile Development",
                description="Android APK building, cross-platform mobile development, and app store deployment",
                skills=[
                    "superdev-apk-builder",
                    "superdev-flutter-dev",
                    "superdev-react-native-dev",
                ],
                capabilities=[
                    "android", "ios", "flutter", "react-native", "kotlin",
                    "swift", "dart", "apk", "aab", "ipa", "gradle",
                    "xcode", "play-store", "app-store", "mobile-ui",
                ],
                max_concurrent_agents=4,
            ),
            AgentDomain.ARCHITECTURE.value: DomainConfig(
                domain=AgentDomain.ARCHITECTURE,
                display_name="Architecture Design",
                description="System design, microservices patterns, and architectural decision records",
                skills=[
                    "superdev-system-design",
                    "superdev-microservices",
                    "superdev-event-driven",
                ],
                capabilities=[
                    "system-design", "microservices", "event-driven", "cqrs",
                    "event-sourcing", "domain-driven-design", "hexagonal",
                    "clean-architecture", "saga-pattern", "api-gateway",
                    "service-discovery", "circuit-breaker",
                ],
                max_concurrent_agents=3,
            ),
            AgentDomain.AUTONOMOUS.value: DomainConfig(
                domain=AgentDomain.AUTONOMOUS,
                display_name="Autonomous Operations (AFK)",
                description="Self-directed task execution, self-healing systems, and continuous operations",
                skills=[
                    "superdev-autonomous-executor",
                    "superdev-self-healing",
                    "superdev-continuous-ops",
                ],
                capabilities=[
                    "autonomous", "self-healing", "auto-remediation",
                    "monitoring", "alerting", "incident-response",
                    "runbook-automation", "chaos-engineering", "sre",
                    "observability", "tracing", "logging",
                ],
                max_concurrent_agents=4,
            ),
            AgentDomain.EXPERIENCE.value: DomainConfig(
                domain=AgentDomain.EXPERIENCE,
                display_name="Experience/UX Engineering",
                description="UX engineering, design systems, accessibility, and performance optimization",
                skills=[
                    "superdev-ux-engineering",
                    "superdev-design-system",
                    "superdev-perf-ux",
                ],
                capabilities=[
                    "ux", "ui", "accessibility", "a11y", "design-system",
                    "component-library", "responsive", "animation",
                    "performance", "core-vitals", "lighthouse", "wcag",
                    "figma", "design-tokens", "storybook",
                ],
                max_concurrent_agents=4,
            ),
        }

    def get_domain(self, domain: AgentDomain) -> DomainConfig | None:
        return self.domains.get(domain.value)

    def get_all_skills(self) -> list[str]:
        skills = []
        for domain_config in self.domains.values():
            skills.extend(domain_config.skills)
        return skills

    def get_all_capabilities(self) -> list[str]:
        caps = []
        for domain_config in self.domains.values():
            caps.extend(domain_config.capabilities)
        return caps

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "project_name": self.project_name,
            "max_total_agents": self.max_total_agents,
            "domains": {
                name: {
                    "display_name": dc.display_name,
                    "description": dc.description,
                    "skills": dc.skills,
                    "capabilities": dc.capabilities,
                    "enabled": dc.enabled,
                }
                for name, dc in self.domains.items()
            },
        }
