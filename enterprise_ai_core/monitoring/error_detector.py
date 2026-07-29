"""
Error Detector - Detects errors in agents
"""

from typing import Any, Dict


class ErrorDetector:
    """Detects errors"""

    def __init__(self, orchestrator):
        self.orchestrator = orchestrator

    async def detect(self, agent: str) -> Dict:
        return {}