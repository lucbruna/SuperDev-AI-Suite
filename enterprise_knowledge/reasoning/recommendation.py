"""Recommendation generation from evidence."""

from __future__ import annotations

from typing import Any

_RECOMMENDATIONS: list[dict[str, Any]] = [
    {"pattern": "performance", "action": "criar índice ou otimizar consulta SQL",
     "reason": "sintomas de degradação de desempenho"},
    {"pattern": "erro", "action": "abrir bug e reproduzir com logs",
     "reason": "falha de software reportada"},
    {"pattern": "seguranca", "action": "revisar permissões e aplicar patch",
     "reason": "risco de segurança identificado"},
    {"pattern": "fiscal", "action": "atualizar o módulo para a nova regra fiscal",
     "reason": "mudança na legislação fiscal"},
    {"pattern": "cust", "action": "auditar orçamento e custos do projeto",
     "reason": "aumento de custos detectado"},
]


class RecommendationEngine:
    """Maps evidence keywords to actionable recommendations."""

    def __init__(self) -> None:
        self.recommendations = [dict(rec)
                                for rec in _RECOMMENDATIONS]

    def recommend(self, evidence: list[str],
                  limit: int = 3) -> list[dict[str, Any]]:
        text = " ".join(evidence).lower()
        hits = []
        for rec in self.recommendations:
            if rec["pattern"] in text:
                hits.append({"action": rec["action"],
                             "reason": rec["reason"]})
        return hits[:max(0, limit)]

    def always(self, action: str, reason: str = "") -> list[dict[str, Any]]:
        return [{"action": action, "reason": reason}]
