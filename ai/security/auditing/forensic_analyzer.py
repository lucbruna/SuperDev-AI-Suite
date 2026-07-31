"""Forensic analysis tools."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import time, uuid

class ForensicCase:
    def __init__(self, case_id: str, title: str, investigator: str = "") -> None:
        self.case_id = case_id
        self.title = title
        self.investigator = investigator
        self.created_at = time.time()
        self.evidence: List[Dict[str, Any]] = []
        self.findings: List[Dict[str, Any]] = []
        self.status = "open"

class ForensicAnalyzer:
    def __init__(self) -> None:
        self._cases: Dict[str, ForensicCase] = {}
    def create_case(self, title: str, investigator: str = "") -> ForensicCase:
        cid = str(uuid.uuid4())[:8]
        case = ForensicCase(cid, title, investigator)
        self._cases[cid] = case
        return case
    def add_evidence(self, case_id: str, evidence_type: str, source: str, data: str = "") -> bool:
        case = self._cases.get(case_id)
        if case:
            case.evidence.append({"type": evidence_type, "source": source, "data": data, "timestamp": time.time()})
            return True
        return False
    def add_finding(self, case_id: str, finding: str, confidence: float = 1.0) -> bool:
        case = self._cases.get(case_id)
        if case:
            case.findings.append({"finding": finding, "confidence": confidence, "timestamp": time.time()})
            return True
        return False
    def close_case(self, case_id: str) -> bool:
        case = self._cases.get(case_id)
        if case:
            case.status = "closed"
            return True
        return False
    def get_case(self, case_id: str) -> Optional[Dict[str, Any]]:
        case = self._cases.get(case_id)
        if case:
            return {"id": case.case_id, "title": case.title, "status": case.status, "evidence_count": len(case.evidence), "findings_count": len(case.findings)}
        return None
    def list_cases(self, status: str = "") -> List[str]:
        if status:
            return [c.case_id for c in self._cases.values() if c.status == status]
        return list(self._cases.keys())
    def timeline(self, case_id: str) -> List[Dict[str, Any]]:
        case = self._cases.get(case_id)
        if not case:
            return []
        events = [(e["timestamp"], "evidence", e) for e in case.evidence] + [(f["timestamp"], "finding", f) for f in case.findings]
        events.sort(key=lambda x: x[0])
        return [{"time": t, "type": tp, "detail": d} for t, tp, d in events]
