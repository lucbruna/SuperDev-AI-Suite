from __future__ import annotations

from pydantic import BaseModel


class BaseDTO(BaseModel):
    """Base Data Transfer Object."""
    model_config = {"from_attributes": True}
