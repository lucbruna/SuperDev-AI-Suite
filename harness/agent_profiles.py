"""Agent profiles - defines specialized agents for each domain."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .config import AgentDomain


@dataclass
class AgentProfile:
    """A specialized agent profile within a domain."""

    agent_id: str
    name: str
    domain: AgentDomain
    role: str
    description: str
    primary_skills: list[str] = field(default_factory=list)
    secondary_skills: list[str] = field(default_factory=list)
    tools_allowed: list[str] = field(default_factory=list)
    max_concurrent_tasks: int = 1
    priority: int = 5  # 1=highest, 10=lowest
    auto_scale: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    def matches_capabilities(self, task_capabilities: list[str]) -> float:
        """Calculate how well this agent matches the required capabilities (0.0-1.0)."""
        if not task_capabilities:
            return 0.5
        all_skills = set(self.primary_skills + self.secondary_skills)
        matched = all_skills.intersection(set(task_capabilities))
        return len(matched) / len(task_capabilities) if task_capabilities else 0.0


class DomainProfileRegistry:
    """Registry of all agent profiles organized by domain."""

    def __init__(self) -> None:
        self._profiles: dict[str, AgentProfile] = {}
        self._by_domain: dict[AgentDomain, list[AgentProfile]] = {d: [] for d in AgentDomain}
        self._register_defaults()

    def _register_defaults(self) -> None:
        """Register all default agent profiles for each domain."""
        # === ENVIRONMENT ENGINEERING ===
        self.register(AgentProfile(
            agent_id="env-docker-specialist",
            name="Docker Specialist",
            domain=AgentDomain.ENVIRONMENT,
            role="Docker containerization expert",
            description="Builds, optimizes, and manages Docker containers and multi-stage builds",
            primary_skills=["docker", "containerization", "dockerfile", "docker-compose"],
            secondary_skills=["container-orchestration", "image-scanning", "registry-management"],
            tools_allowed=["read_file", "write_file", "search_code", "execute_code", "list_files"],
            priority=2,
        ))
        self.register(AgentProfile(
            agent_id="env-k8s-specialist",
            name="Kubernetes Specialist",
            domain=AgentDomain.ENVIRONMENT,
            role="Kubernetes deployment and orchestration expert",
            description="Manages K8s clusters, deployments, services, and Helm charts",
            primary_skills=["kubernetes", "helm", "kustomize", "kubectl"],
            secondary_skills=["service-mesh", "istio", "ingress", "rbac"],
            tools_allowed=["read_file", "write_file", "search_code", "execute_code", "list_files"],
            priority=2,
        ))
        self.register(AgentProfile(
            agent_id="env-cicd-engineer",
            name="CI/CD Pipeline Engineer",
            domain=AgentDomain.ENVIRONMENT,
            role="Continuous integration and deployment specialist",
            description="Designs and maintains CI/CD pipelines, automates testing and deployment",
            primary_skills=["github-actions", "gitlab-ci", "jenkins", "argocd"],
            secondary_skills=["pipeline-optimization", "artifact-management", "environment-protection"],
            tools_allowed=["read_file", "write_file", "search_code", "execute_code", "list_files"],
            priority=3,
        ))
        self.register(AgentProfile(
            agent_id="env-terraform-architect",
            name="Infrastructure as Code Architect",
            domain=AgentDomain.ENVIRONMENT,
            role="Terraform and IaC specialist",
            description="Designs and implements infrastructure as code with Terraform, Pulumi, and Ansible",
            primary_skills=["terraform", "pulumi", "ansible", "infrastructure-as-code"],
            secondary_skills=["cloud-provisioning", "state-management", "module-design"],
            tools_allowed=["read_file", "write_file", "search_code", "execute_code", "list_files"],
            priority=3,
        ))
        self.register(AgentProfile(
            agent_id="env-monitoring-specialist",
            name="Observability Specialist",
            domain=AgentDomain.ENVIRONMENT,
            role="Monitoring, logging, and tracing expert",
            description="Implements full observability stack with Prometheus, Grafana, ELK, and Jaeger",
            primary_skills=["monitoring", "prometheus", "grafana", "elk-stack"],
            secondary_skills=["distributed-tracing", "jaeger", "alerting", "slo-management"],
            tools_allowed=["read_file", "write_file", "search_code", "execute_code", "list_files"],
            priority=4,
        ))

        # === APK/MOBILE ===
        self.register(AgentProfile(
            agent_id="mobile-android-specialist",
            name="Android APK Specialist",
            domain=AgentDomain.MOBILE,
            role="Android development and APK building expert",
            description="Builds, signs, and optimizes Android APKs and AABs with Gradle",
            primary_skills=["android", "kotlin", "gradle", "apk", "aab"],
            secondary_skills=["android-studio", "play-store", "proguard", "r8"],
            tools_allowed=["read_file", "write_file", "search_code", "execute_code", "list_files"],
            priority=2,
        ))
        self.register(AgentProfile(
            agent_id="mobile-flutter-specialist",
            name="Flutter Development Specialist",
            domain=AgentDomain.MOBILE,
            role="Flutter cross-platform development expert",
            description="Builds cross-platform mobile apps with Flutter and Dart",
            primary_skills=["flutter", "dart", "cross-platform", "mobile-ui"],
            secondary_skills=["flutter-web", "flutter-desktop", "state-management", "bloc"],
            tools_allowed=["read_file", "write_file", "search_code", "execute_code", "list_files"],
            priority=2,
        ))
        self.register(AgentProfile(
            agent_id="mobile-react-native-specialist",
            name="React Native Specialist",
            domain=AgentDomain.MOBILE,
            role="React Native cross-platform development expert",
            description="Builds cross-platform mobile apps with React Native and TypeScript",
            primary_skills=["react-native", "javascript", "typescript", "mobile-ui"],
            secondary_skills=["expo", "native-modules", "navigation", "state-management"],
            tools_allowed=["read_file", "write_file", "search_code", "execute_code", "list_files"],
            priority=2,
        ))
        self.register(AgentProfile(
            agent_id="mobile-ios-specialist",
            name="iOS Specialist",
            domain=AgentDomain.MOBILE,
            role="iOS development and App Store deployment expert",
            description="Builds iOS apps with Swift/SwiftUI and manages App Store deployment",
            primary_skills=["ios", "swift", "swiftui", "xcode"],
            secondary_skills=["cocoapods", "spm", "app-store", "testflight"],
            tools_allowed=["read_file", "write_file", "search_code", "execute_code", "list_files"],
            priority=3,
        ))

        # === ARCHITECTURE ===
        self.register(AgentProfile(
            agent_id="arch-system-designer",
            name="System Design Architect",
            domain=AgentDomain.ARCHITECTURE,
            role="High-level system architecture designer",
            description="Designs distributed systems, defines service boundaries, and creates ADRs",
            primary_skills=["system-design", "distributed-systems", "architecture-decision-records"],
            secondary_skills=["scalability", "high-availability", "disaster-recovery"],
            tools_allowed=["read_file", "write_file", "search_code", "list_files"],
            priority=1,
        ))
        self.register(AgentProfile(
            agent_id="arch-microservices-expert",
            name="Microservices Architect",
            domain=AgentDomain.ARCHITECTURE,
            role="Microservices pattern expert",
            description="Designs microservices architectures with proper service boundaries and communication",
            primary_skills=["microservices", "api-gateway", "service-discovery", "circuit-breaker"],
            secondary_skills=["saga-pattern", "choreography", "orchestration", "grpc"],
            tools_allowed=["read_file", "write_file", "search_code", "list_files"],
            priority=1,
        ))
        self.register(AgentProfile(
            agent_id="arch-ddd-specialist",
            name="Domain-Driven Design Specialist",
            domain=AgentDomain.ARCHITECTURE,
            role="DDD and clean architecture expert",
            description="Applies Domain-Driven Design, CQRS, and Event Sourcing patterns",
            primary_skills=["domain-driven-design", "cqrs", "event-sourcing", "clean-architecture"],
            secondary_skills=["bounded-contexts", "aggregates", "value-objects", "repositories"],
            tools_allowed=["read_file", "write_file", "search_code", "list_files"],
            priority=2,
        ))
        self.register(AgentProfile(
            agent_id="arch-event-driven-specialist",
            name="Event-Driven Architecture Specialist",
            domain=AgentDomain.ARCHITECTURE,
            role="Event-driven and messaging expert",
            description="Designs event-driven systems with Kafka, RabbitMQ, and event streams",
            primary_skills=["event-driven", "kafka", "rabbitmq", "event-streaming"],
            secondary_skills=["event-schemas", "schema-registry", "dead-letter-queues", "exactly-once"],
            tools_allowed=["read_file", "write_file", "search_code", "list_files"],
            priority=2,
        ))

        # === AUTONOMOUS (AFK) ===
        self.register(AgentProfile(
            agent_id="afk-autonomous-executor",
            name="Autonomous Task Executor",
            domain=AgentDomain.AUTONOMOUS,
            role="Self-directed task execution agent",
            description="Executes complex tasks autonomously with planning, reasoning, and self-correction",
            primary_skills=["autonomous", "task-planning", "self-correction", "reasoning"],
            secondary_skills=["goal-decomposition", "dependency-resolution", "progress-tracking"],
            tools_allowed=["read_file", "write_file", "search_code", "execute_code", "list_files", "clone_github_repository"],
            priority=1,
            max_concurrent_tasks=3,
        ))
        self.register(AgentProfile(
            agent_id="afk-self-healing",
            name="Self-Healing Agent",
            domain=AgentDomain.AUTONOMOUS,
            role="Self-healing and auto-remediation specialist",
            description="Detects failures and automatically applies remediation strategies",
            primary_skills=["self-healing", "auto-remediation", "fault-detection", "recovery"],
            secondary_skills=["root-cause-analysis", "rollback", "circuit-breaker", "fallback"],
            tools_allowed=["read_file", "write_file", "search_code", "execute_code", "list_files"],
            priority=2,
        ))
        self.register(AgentProfile(
            agent_id="afk-incident-responder",
            name="Incident Response Agent",
            domain=AgentDomain.AUTONOMOUS,
            role="Automated incident response and runbook execution",
            description="Responds to incidents by executing runbooks and coordinating remediation",
            primary_skills=["incident-response", "runbook-automation", "alerting", "escalation"],
            secondary_skills=["post-mortem", "blameless-analysis", "slo-tracking", "error-budgets"],
            tools_allowed=["read_file", "write_file", "search_code", "execute_code", "list_files"],
            priority=2,
        ))
        self.register(AgentProfile(
            agent_id="afk-chaos-engineer",
            name="Chaos Engineering Agent",
            domain=AgentDomain.AUTONOMOUS,
            role="Chaos engineering and resilience testing specialist",
            description="Designs and executes chaos experiments to validate system resilience",
            primary_skills=["chaos-engineering", "resilience-testing", "fault-injection", "game-day"],
            secondary_skills=["blast-radius", "steady-state-hypothesis", "experiment-design"],
            tools_allowed=["read_file", "write_file", "search_code", "execute_code", "list_files"],
            priority=3,
        ))

        # === EXPERIENCE/UX ===
        self.register(AgentProfile(
            agent_id="ux-engineer",
            name="UX Engineer",
            domain=AgentDomain.EXPERIENCE,
            role="User experience engineering specialist",
            description="Implements UX best practices, interaction patterns, and user research insights",
            primary_skills=["ux", "interaction-design", "user-research", "prototyping"],
            secondary_skills=["usability", "information-architecture", "user-flows", "wireframing"],
            tools_allowed=["read_file", "write_file", "search_code", "list_files"],
            priority=2,
        ))
        self.register(AgentProfile(
            agent_id="ux-accessibility-specialist",
            name="Accessibility Specialist",
            domain=AgentDomain.EXPERIENCE,
            role="WCAG compliance and accessibility expert",
            description="Ensures WCAG 2.1 AA compliance and implements accessible components",
            primary_skills=["accessibility", "a11y", "wcag", "screen-readers"],
            secondary_skills=["aria", "keyboard-navigation", "color-contrast", "semantic-html"],
            tools_allowed=["read_file", "write_file", "search_code", "list_files"],
            priority=2,
        ))
        self.register(AgentProfile(
            agent_id="ux-design-system-architect",
            name="Design System Architect",
            domain=AgentDomain.EXPERIENCE,
            role="Design system creation and management expert",
            description="Builds and maintains design systems with components, tokens, and documentation",
            primary_skills=["design-system", "component-library", "design-tokens", "storybook"],
            secondary_skills=["theming", "responsive-design", "animation", "figma"],
            tools_allowed=["read_file", "write_file", "search_code", "list_files"],
            priority=2,
        ))
        self.register(AgentProfile(
            agent_id="ux-performance-engineer",
            name="Performance UX Engineer",
            domain=AgentDomain.EXPERIENCE,
            role="Web performance optimization specialist",
            description="Optimizes Core Web Vitals, bundle size, and runtime performance",
            primary_skills=["performance", "core-vitals", "lighthouse", "bundle-optimization"],
            secondary_skills=["code-splitting", "lazy-loading", "caching", "cdn"],
            tools_allowed=["read_file", "write_file", "search_code", "execute_code", "list_files"],
            priority=3,
        ))

    def register(self, profile: AgentProfile) -> None:
        self._profiles[profile.agent_id] = profile
        self._by_domain[profile.domain].append(profile)

    def get(self, agent_id: str) -> AgentProfile | None:
        return self._profiles.get(agent_id)

    def list_all(self) -> list[AgentProfile]:
        return list(self._profiles.values())

    def list_by_domain(self, domain: AgentDomain) -> list[AgentProfile]:
        return list(self._by_domain.get(domain, []))

    def find_best_match(self, capabilities: list[str], domain: AgentDomain | None = None) -> AgentProfile | None:
        """Find the agent profile with the best capability match."""
        candidates = self.list_by_domain(domain) if domain else self.list_all()
        if not candidates:
            return None
        scored = [(p, p.matches_capabilities(capabilities)) for p in candidates]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[0][0] if scored[0][1] > 0 else None

    def count(self) -> int:
        return len(self._profiles)

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_profiles": self.count(),
            "by_domain": {
                domain.value: len(profiles)
                for domain, profiles in self._by_domain.items()
            },
            "profiles": [
                {
                    "agent_id": p.agent_id,
                    "name": p.name,
                    "domain": p.domain.value,
                    "role": p.role,
                }
                for p in self._profiles.values()
            ],
        }
