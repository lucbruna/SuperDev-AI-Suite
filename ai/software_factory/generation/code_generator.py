"""Code generator for producing source files."""
from typing import List, Dict, Any, Optional
from .models import GeneratedFile, Template, TemplateLanguage


class CodeGenerator:
    """Generates code from templates and specifications."""

    def __init__(self):
        self._generators: Dict[str, Any] = {}

    def generate_class(self, class_name: str, attributes: List[Dict[str, str]],
                       methods: List[str], language: TemplateLanguage = TemplateLanguage.PYTHON) -> str:
        if language == TemplateLanguage.PYTHON:
            return self._generate_python_class(class_name, attributes, methods)
        elif language == TemplateLanguage.TYPESCRIPT:
            return self._generate_typescript_class(class_name, attributes, methods)
        return f"// Class: {class_name}"

    def _generate_python_class(self, class_name: str, attributes: List[Dict[str, str]],
                                methods: List[str]) -> str:
        lines = [f"class {class_name}:"]
        lines.append(f'    """Auto-generated class."""')
        lines.append("")
        lines.append("    def __init__(self):")
        for attr in attributes:
            name = attr.get("name", "item")
            default = attr.get("default", "None")
            lines.append(f"        self.{name} = {default}")
        for method in methods:
            lines.append("")
            lines.append(f"    def {method}(self) -> None:")
            lines.append(f"        pass")
        return "\n".join(lines)

    def _generate_typescript_class(self, class_name: str, attributes: List[Dict[str, str]],
                                    methods: List[str]) -> str:
        lines = [f"export class {class_name} {{"]
        for attr in attributes:
            name = attr.get("name", "item")
            lines.append(f"    {name}: any;")
        for method in methods:
            lines.append(f"    {method}(): void {{}}")
        lines.append("}")
        return "\n".join(lines)

    def generate_function(self, name: str, params: List[str],
                          body: str, language: TemplateLanguage = TemplateLanguage.PYTHON) -> str:
        if language == TemplateLanguage.PYTHON:
            param_str = ", ".join(params)
            return f"def {name}({param_str}):\n    {body}"
        return f"function {name}({', '.join(params)}) {{ {body} }}"

    def generate_module(self, module_name: str, imports: List[str],
                        classes: List[str], functions: List[str]) -> str:
        lines = [f'"""Module: {module_name}"""', ""]
        for imp in imports:
            lines.append(imp)
        if imports:
            lines.append("")
        for cls in classes:
            lines.append(cls)
            lines.append("")
        for func in functions:
            lines.append(func)
            lines.append("")
        return "\n".join(lines)

    def register_generator(self, name: str, generator_fn: Any) -> None:
        self._generators[name] = generator_fn

    def get_custom_generator(self, name: str) -> Optional[Any]:
        return self._generators.get(name)
