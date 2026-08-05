"""Customer Campaigns — video briefs for segmented customer campaigns."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.integration._brief import build_brief


class CustomerCampaignGenerator:
    """Builds campaign narration scripts for a customer segment."""

    def generate(self, *, segment: str = "loyal customers", offer: str = "20% off",
                 product: str = "our new collection", voice: str = "default") -> dict[str, Any]:
        title = f"Campaign for {segment}"
        scenes = [
            f"Hi {segment}, this offer is made for you.",
            f"Enjoy {offer} on {product}.",
            "Limited time — act before the campaign ends.",
            "Tap the link to take advantage today.",
        ]
        return build_brief("crm", title, scenes, voice=voice,
                           segment=segment, offer=offer, product=product).to_dict()


_customer_campaign_generator: CustomerCampaignGenerator | None = None


def get_customer_campaign_generator() -> CustomerCampaignGenerator:
    global _customer_campaign_generator
    if _customer_campaign_generator is None:
        _customer_campaign_generator = CustomerCampaignGenerator()
    return _customer_campaign_generator
