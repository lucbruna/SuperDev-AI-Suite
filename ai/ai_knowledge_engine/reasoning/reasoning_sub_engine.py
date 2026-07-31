"""Reasoning subsystem engine — Inference, hypothesis building, and conclusion generation."""
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass, field


class ReasoningType(Enum):
    DEDUCTIVE = "deductive"
    INDUCTIVE = "inductive"
    ABDUCTIVE = "abductive"
    ANALOGICAL = "analogical"


class HypothesisStatus(Enum):
    PROPOSED = "proposed"
    TESTING = "testing"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"


@dataclass
class Observation:
    observation_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    description: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    source: str = ""
    confidence: float = 0.5
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Hypothesis:
    hypothesis_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    statement: str = ""
    reasoning_type: ReasoningType = ReasoningType.INDUCTIVE
    evidence_for: List[str] = field(default_factory=list)
    evidence_against: List[str] = field(default_factory=list)
    status: HypothesisStatus = HypothesisStatus.PROPOSED
    confidence: float = 0.3
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Conclusion:
    conclusion_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    statement: str = ""
    reasoning_type: ReasoningType = ReasoningType.DEDUCTIVE
    supporting_evidence: List[str] = field(default_factory=list)
    confidence: float = 0.5
    implications: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


class ReasoningSubEngine:
    def __init__(self):
        self._observations: Dict[str, Observation] = {}
        self._hypotheses: Dict[str, Hypothesis] = {}
        self._conclusions: Dict[str, Conclusion] = {}
        self._inference_rules: List[Dict[str, Any]] = []

    def add_observation(self, description: str, data: Optional[Dict[str, Any]] = None, source: str = "") -> Observation:
        obs = Observation(description=description, data=data or {}, source=source)
        self._observations[obs.observation_id] = obs
        return obs

    def get_observation(self, observation_id: str) -> Optional[Observation]:
        return self._observations.get(observation_id)

    def add_hypothesis(self, statement: str, reasoning_type: str = "inductive") -> Hypothesis:
        rt = ReasoningType(reasoning_type) if reasoning_type in [e.value for e in ReasoningType] else ReasoningType.INDUCTIVE
        hyp = Hypothesis(statement=statement, reasoning_type=rt)
        self._hypotheses[hyp.hypothesis_id] = hyp
        return hyp

    def get_hypothesis(self, hypothesis_id: str) -> Optional[Hypothesis]:
        return self._hypotheses.get(hypothesis_id)

    def add_evidence(self, hypothesis_id: str, evidence: str, is_for: bool = True) -> bool:
        hyp = self._hypotheses.get(hypothesis_id)
        if not hyp:
            return False
        if is_for:
            hyp.evidence_for.append(evidence)
        else:
            hyp.evidence_against.append(evidence)
        total = len(hyp.evidence_for) + len(hyp.evidence_against)
        if total > 0:
            hyp.confidence = len(hyp.evidence_for) / total
        return True

    def test_hypothesis(self, hypothesis_id: str) -> HypothesisStatus:
        hyp = self._hypotheses.get(hypothesis_id)
        if not hyp:
            return HypothesisStatus.PROPOSED
        hyp.status = HypothesisStatus.TESTING
        if hyp.confidence > 0.7 and len(hyp.evidence_for) > len(hyp.evidence_against):
            hyp.status = HypothesisStatus.CONFIRMED
        elif hyp.confidence < 0.3:
            hyp.status = HypothesisStatus.REJECTED
        return hyp.status

    def add_rule(self, name: str, condition: Dict[str, Any], conclusion: str) -> None:
        self._inference_rules.append({"name": name, "condition": condition, "conclusion": conclusion})

    def infer(self, context: Dict[str, Any]) -> List[str]:
        results = []
        for rule in self._inference_rules:
            match = all(context.get(k) == v for k, v in rule["condition"].items())
            if match:
                results.append(rule["conclusion"])
        return results

    def create_conclusion(self, statement: str, evidence: Optional[List[str]] = None, reasoning_type: str = "deductive") -> Conclusion:
        rt = ReasoningType(reasoning_type) if reasoning_type in [e.value for e in ReasoningType] else ReasoningType.DEDUCTIVE
        conc = Conclusion(statement=statement, reasoning_type=rt, supporting_evidence=evidence or [])
        self._conclusions[conc.conclusion_id] = conc
        return conc

    def get_conclusion(self, conclusion_id: str) -> Optional[Conclusion]:
        return self._conclusions.get(conclusion_id)

    def analyze_problem(self, problem: str, observations: Optional[List[str]] = None) -> Dict[str, Any]:
        hypotheses = []
        for obs_id, obs in self._observations.items():
            if any(word in obs.description.lower() for word in problem.lower().split()):
                hyp = self.add_hypothesis(f"Possible cause: {obs.description}")
                hypotheses.append(hyp.hypothesis_id)
        return {
            "problem": problem,
            "observations_used": len(observations or []),
            "hypotheses_generated": len(hypotheses),
            "hypothesis_ids": hypotheses,
        }

    def get_stats(self) -> dict:
        return {
            "total_observations": len(self._observations),
            "total_hypotheses": len(self._hypotheses),
            "total_conclusions": len(self._conclusions),
            "confirmed_hypotheses": len([h for h in self._hypotheses.values() if h.status == HypothesisStatus.CONFIRMED]),
            "inference_rules": len(self._inference_rules),
        }
