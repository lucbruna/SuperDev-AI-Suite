"""Training Material — creates training video briefs for ERP workflows."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.integration._brief import build_brief

_WORKFLOWS: dict[str, str] = {
    "purchase_order": "creating and approving purchase orders",
    "invoice_entry": "entering and posting supplier invoices",
    "stock_transfer": "transferring stock between warehouses",
    "reconciliation": "running monthly reconciliations",
}


class TrainingMaterialGenerator:
    """Builds step-by-step training video briefs for ERP workflows."""

    def generate(self, *, workflow: str = "invoice_entry", audience: str = "new users",
                 voice: str = "default") -> dict[str, Any]:
        workflow = workflow if workflow in _WORKFLOWS else "invoice_entry"
        title = f"Training — {workflow.replace('_', ' ')}"
        scenes = [
            f"Training for {audience}: {_WORKFLOWS[workflow]}.",
            "Step 1: open the module and locate the action button.",
            "Step 2: fill the required fields and validate.",
            "Step 3: submit, then check the confirmation screen.",
            "Practice the flow and open the written guide when needed.",
        ]
        return build_brief("erp", title, scenes, voice=voice,
                           workflow=workflow, audience=audience).to_dict()


_training_material_generator: TrainingMaterialGenerator | None = None


def get_training_material_generator() -> TrainingMaterialGenerator:
    global _training_material_generator
    if _training_material_generator is None:
        _training_material_generator = TrainingMaterialGenerator()
    return _training_material_generator
