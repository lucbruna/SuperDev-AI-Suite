"""
Copy Generator - Generates marketing copy
"""

from typing import Any, Dict, List


class CopyGenerator:
    """Generates marketing copy"""

    def __init__(self):
        self._templates: Dict[str, str] = {}

    def register_template(self, name: str, template: str) -> None:
        self._templates[name] = template

    def generate(
        self,
        template_name: str,
        variables: Dict[str, Any],
        tone: str = "persuasive",
    ) -> str:
        template = self._templates.get(template_name)
        if not template:
            return f"Generated copy for {template_name} with {variables}"

        for key, value in variables.items():
            template = template.replace(f"{{{key}}}", str(value))

        return template

    def generate_ad_copy(
        self,
        product: str,
        benefit: str,
        audience: str,
        platform: str = "facebook",
    ) -> Dict[str, str]:
        return {
            "headline": f"Discover {product} - {benefit}",
            "primary_text": f"Looking for {benefit}? {product} is the solution for {audience}.",
            "description": f"Join thousands of {audience} who trust {product}.",
            "cta": "Learn More",
        }

    def generate_email_sequence(
        self,
        product: str,
        audience: str,
        sequence_length: int = 5,
    ) -> List[Dict]:
        return [
            {"subject": f"Welcome to {product}", "body": f"Thanks for your interest, {audience}!"},
            {"subject": f"Why {product}?", "body": f"{product} helps you achieve..."},
            {"subject": f"Success stories", "body": f"See how {audience} benefited..."},
            {"subject": f"Special offer", "body": f"Exclusive deal for {audience}..."},
            {"subject": f"Last chance", "body": f"Don't miss out on {product}..."},
        ][:sequence_length]