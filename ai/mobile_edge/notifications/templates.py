"""Templates - Notification templates."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class NotificationTemplate:
    template_id: str
    name: str
    title_template: str = ""
    message_template: str = ""
    variables: list[str] = field(default_factory=list)
    default_data: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


class TemplateManager:
    def __init__(self):
        self.templates: dict[str, NotificationTemplate] = {}

    def create(self, template_id: str, name: str, title_template: str = "", message_template: str = "", variables: list[str] = None) -> NotificationTemplate:
        template = NotificationTemplate(template_id=template_id, name=name, title_template=title_template, message_template=message_template, variables=variables or [])
        self.templates[template_id] = template
        return template

    def render(self, template_id: str, context: dict[str, Any]) -> dict[str, str]:
        template = self.templates.get(template_id)
        if not template:
            return {"title": "", "message": ""}
        title = template.title_template
        message = template.message_template
        for key, value in context.items():
            title = title.replace(f"{{{{{key}}}}}", str(value))
            message = message.replace(f"{{{{{key}}}}}", str(value))
        return {"title": title, "message": message}

    def get(self, template_id: str) -> NotificationTemplate | None:
        return self.templates.get(template_id)

    def list_templates(self) -> list[NotificationTemplate]:
        return list(self.templates.values())

    def count(self) -> int:
        return len(self.templates)
