"""
Prompt Builder
"""
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field


@dataclass
class PromptTemplate:
    name: str
    template: str
    variables: List[str] = field(default_factory=list)
    category: str = "general"
    description: str = ""


class PromptBuilder:
    def __init__(self):
        self.templates: List[PromptTemplate] = []
        self.custom_variables: Dict[str, str] = {}
        
    def add_template(self, template: PromptTemplate) -> None:
        self.templates.append(template)
        
    def build(self, template_name: str, variables: Optional[Dict[str, str]] = None) -> str:
        template = next((t for t in self.templates if t.name == template_name), None)
        if not template:
            raise ValueError(f"Template '{template_name}' not found")
        result = template.template
        all_vars = {**self.custom_variables, **(variables or {})}
        for key, value in all_vars.items():
            result = result.replace("{" + key + "}", value)
        return result
        
    def get_templates_by_category(self, category: str) -> List[PromptTemplate]:
        return [t for t in self.templates if t.category == category]
        
    def render(self) -> Dict[str, Any]:
        return {
            "templates": [{"name": t.name, "category": t.category, "variables": t.variables} for t in self.templates],
            "variables": self.custom_variables,
        }
