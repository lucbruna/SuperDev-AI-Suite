"""
Campaign Builder - Builds campaigns from templates
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from marketing_growth_ai.marketing_models import (
    Campaign,
    CampaignType,
    Channel,
)


class CampaignBuilder:
    """Builds campaigns from templates"""

    def __init__(self):
        self._templates: Dict[str, Dict] = {}

    def register_template(self, name: str, template: Dict) -> None:
        self._templates[name] = template

    def build_from_template(
        self,
        template_name: str,
        variables: Dict[str, Any],
    ) -> Campaign:
        template = self._templates.get(template_name)
        if not template:
            raise ValueError(f"Template {template_name} not found")

        return Campaign(
            name=template.get("name", template_name).format(**variables),
            campaign_type=CampaignType(template.get("type", "acquisition")),
            objective=template.get("objective", "").format(**variables),
            target_audience=template.get("target_audience", {}),
            channels=[Channel(c) for c in template.get("channels", [])],
            budget=template.get("budget", 0.0),
            start_date=datetime.utcnow(),
        )

    def build_custom(self, config: Dict[str, Any]) -> Campaign:
        return Campaign(**config)

    def validate(self, campaign: Campaign) -> List[str]:
        errors = []
        if not campaign.name:
            errors.append("Campaign name is required")
        if campaign.budget <= 0:
            errors.append("Budget must be positive")
        if not campaign.channels:
            errors.append("At least one channel is required")
        return errors