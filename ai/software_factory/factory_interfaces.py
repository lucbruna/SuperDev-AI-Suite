"""Factory Interfaces - Abstract interfaces for factory components."""
from typing import Dict, Any, Optional, Protocol


class RequirementAnalyzerProtocol(Protocol):
    def analyze(self, idea: str) -> Dict[str, Any]: ...

class CodeGeneratorProtocol(Protocol):
    def generate(self, spec: Dict[str, Any]) -> Dict[str, Any]: ...

class TestRunnerProtocol(Protocol):
    def run(self, project_id: str) -> Dict[str, Any]: ...

class DeployerProtocol(Protocol):
    def deploy(self, project_id: str, config: Dict[str, Any]) -> bool: ...

class DocumentationGeneratorProtocol(Protocol):
    def generate(self, project_id: str) -> Dict[str, Any]: ...

class QualityReviewerProtocol(Protocol):
    def review(self, project_id: str) -> Dict[str, Any]: ...
