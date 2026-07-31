"""Service helpers — sibling module reachable via ``from . import helpers``.

Imports across two packages with ``from ..utils.helpers import ...`` so the
navigation resolves a level-2 relative import.
"""

from ..utils.helpers import generate_id


def build_order_id() -> str:
    """Order id derived from the shared id generator."""
    return f"ORD-{generate_id()}"
