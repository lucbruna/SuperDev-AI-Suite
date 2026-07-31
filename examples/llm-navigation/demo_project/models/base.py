"""Base entity shared by the demo models."""


class BaseEntity:
    """Minimal base class."""

    def to_dict(self) -> dict:
        return vars(self)
