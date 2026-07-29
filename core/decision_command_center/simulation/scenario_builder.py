from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, List, Optional

from ..decision_config import DecisionConfig

logger = logging.getLogger(__name__)

SCENARIO_TEMPLATES = {
    "nova_filial": {
        "name": "Abertura de Nova Filial",
        "params": ["investimento_inicial", "cidade", "equipe_tamanho", "projecao_receita"],
        "description": "Simular impacto de abrir uma nova filial",
    },
    "mudanca_preco": {
        "name": "Mudança de Preço",
        "params": ["produto", "preco_atual", "novo_preco", "elasticidade"],
        "description": "Simular impacto de alteração de preço",
    },
    "contratacao": {
        "name": "Contratação de Equipe",
        "params": ["quantidade", "cargo", "salario_medio", "impacto_receita"],
        "description": "Simular impacto de novas contratações",
    },
    "investimento": {
        "name": "Novo Investimento",
        "params": ["valor", "area", "retorno_esperado", "prazo"],
        "description": "Simular impacto de novo investimento",
    },
}


class ScenarioBuilder:
    def __init__(self, config: DecisionConfig):
        self._config = config

    def build(self, name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": str(uuid.uuid4()),
            "name": name,
            "parameters": params,
            "type": "custom",
            "status": "ready",
        }

    def list_templates(self) -> List[Dict[str, Any]]:
        return [
            {"id": k, **v}
            for k, v in SCENARIO_TEMPLATES.items()
        ]

    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        template = SCENARIO_TEMPLATES.get(template_id)
        if template:
            return {"id": template_id, **template}
        return None
