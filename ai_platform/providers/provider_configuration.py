
from pydantic import BaseModel, Field


class ProviderConfig(BaseModel):
    name: str
    type: str
    api_key: str | None = None
    base_url: str | None = None
    default_model: str = ""
    max_retries: int = 3
    timeout: int = 60
    options: dict[str, object] = Field(default_factory=dict)
