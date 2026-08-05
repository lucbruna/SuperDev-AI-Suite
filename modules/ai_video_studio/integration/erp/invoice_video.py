"""Invoice Video Generator — explains invoice line items in video form."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.integration._brief import build_brief


class InvoiceVideoGenerator:
    """Builds narration scripts that walk through an invoice."""

    def generate(self, *, invoice_id: str = "INV-0001", amount: float = 1490.0,
                 customer: str = "ACME Corp", voice: str = "default") -> dict[str, Any]:
        title = f"Invoice {invoice_id} — {customer}"
        scenes = [
            f"Here is a summary of invoice {invoice_id} for {customer}.",
            f"The total amount due is {amount:,.2f}.",
            "Breakdown by line item, taxes and discounts is on screen.",
            "Please review and pay by the due date on the invoice.",
        ]
        return build_brief("erp", title, scenes, voice=voice,
                           invoice_id=invoice_id, amount=round(amount, 2), customer=customer).to_dict()


_invoice_video_generator: InvoiceVideoGenerator | None = None


def get_invoice_video_generator() -> InvoiceVideoGenerator:
    global _invoice_video_generator
    if _invoice_video_generator is None:
        _invoice_video_generator = InvoiceVideoGenerator()
    return _invoice_video_generator
