from __future__ import annotations


class CodeGenerator:
    """Code generation utilities."""

    @staticmethod
    def generate_crud(model_name: str, fields: dict[str, str]) -> dict[str, str]:
        snake = model_name.lower()
        templates = {
            "model": f'class {model_name}(Base):\n    __tablename__ = "{snake}s"\n\n',
            "schema": f'class {model_name}Base(BaseModel):\n    model_config = {{"from_attributes": True}}\n\n',
            "router": f'router = APIRouter(prefix="/{snake}s", tags=["{snake}"])\n\n',
        }
        for field_name, field_type in fields.items():
            templates["model"] += f"    {field_name}: Mapped[{field_type}]\n"
            templates["schema"] += f"    {field_name}: {field_type}\n"
        return templates

    @staticmethod
    def generate_api_endpoint(
        method: str,
        path: str,
        function_name: str,
        response_model: str | None = None,
    ) -> str:
        decorator = f'@router.{method}("{path}")'
        if response_model:
            decorator += f', response_model={response_model}'
        return f"{decorator}\nasync def {function_name}() -> dict:\n    pass\n"
