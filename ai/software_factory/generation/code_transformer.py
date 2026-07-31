"""Code transformer for modifying generated code."""

import re

from .models import TemplateLanguage, TransformRule


class CodeTransformer:
    """Applies transformation rules to code."""

    def __init__(self):
        self._rules: list[TransformRule] = []

    def add_rule(self, rule: TransformRule) -> None:
        self._rules.append(rule)

    def apply_rules(self, code: str, language: TemplateLanguage = TemplateLanguage.PYTHON) -> str:
        result = code
        for rule in self._rules:
            if rule.enabled and rule.language == language:
                result = re.sub(rule.pattern, rule.replacement, result)
        return result

    def rename_variable(self, code: str, old_name: str, new_name: str) -> str:
        return re.sub(r"\b" + old_name + r"\b", new_name, code)

    def add_import(self, code: str, import_statement: str) -> str:
        lines = code.split("\n")
        insert_at = 0
        for i, line in enumerate(lines):
            if line.startswith("import ") or line.startswith("from "):
                insert_at = i + 1
        lines.insert(insert_at, import_statement)
        return "\n".join(lines)

    def remove_comments(self, code: str) -> str:
        lines = code.split("\n")
        return "\n".join(line for line in lines if not line.strip().startswith("#"))

    def format_code(self, code: str) -> str:
        lines = code.split("\n")
        formatted = []
        for line in lines:
            stripped = line.strip()
            if stripped:
                formatted.append(stripped)
            else:
                formatted.append("")
        return "\n".join(formatted)

    def get_rules(self) -> list[TransformRule]:
        return list(self._rules)

    def clear_rules(self) -> None:
        self._rules.clear()
