from typing import Optional
from pydantic import BaseModel, Field


class ProviderConfig(BaseModel):
    name: str
    type: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    default_model: str = ""
    max_retries: int = 3
    timeout: int = 60
    options: dict[str, object] = Field(default_factory=dict)
