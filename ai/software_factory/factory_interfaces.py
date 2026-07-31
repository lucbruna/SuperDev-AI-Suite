"""Factory Interfaces - Abstract interfaces for factory components."""

from typing import Any, Protocol


class RequirementAnalyzerProtocol(Protocol):
    def analyze(self, idea: str) -> dict[str, Any]: ...


class CodeGeneratorProtocol(Protocol):
    def generate(self, spec: dict[str, Any]) -> dict[str, Any]: ...


class TestRunnerProtocol(Protocol):
    def run(self, project_id: str) -> dict[str, Any]: ...


class DeployerProtocol(Protocol):
    def deploy(self, project_id: str, config: dict[str, Any]) -> bool: ...


class DocumentationGeneratorProtocol(Protocol):
    def generate(self, project_id: str) -> dict[str, Any]: ...


class QualityReviewerProtocol(Protocol):
    def review(self, project_id: str) -> dict[str, Any]: ...
