"""Review criteria per review kind."""

from __future__ import annotations

from typing import Any

from collaboration.collaboration_models import ReviewKind

CRITERIA: dict[ReviewKind, list[str]] = {
    ReviewKind.CODE: ["clareza", "testes", "desempenho", "manutenibilidade"],
    ReviewKind.DOCUMENT: ["precisao", "completude", "formato"],
    ReviewKind.SECURITY: ["autenticacao", "autorizacao", "validacao",
                          "exposicao_de_dados"],
    ReviewKind.PROCESS: ["conformidade", "rastreabilidade", "documentacao"],
}


class ReviewCriteria:
    """Checklist of criteria for each review kind."""

    def criteria_for(self, kind: ReviewKind) -> list[str]:
        return list(CRITERIA.get(kind, []))

    def checklist(self, kind: ReviewKind) -> list[dict[str, Any]]:
        return [{"criterion": c, "passed": None}
                for c in self.criteria_for(kind)]

    def all_kinds(self) -> list[str]:
        return [kind.value for kind in ReviewKind]
