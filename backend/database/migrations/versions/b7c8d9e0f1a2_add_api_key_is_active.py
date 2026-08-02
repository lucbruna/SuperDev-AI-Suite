"""add_api_key_is_active

Add ``api_keys.is_active`` boolean column for the soft-delete/revoke contract.

The ``APIKeyAuth`` dependency filters ``.where(APIKey.is_active)`` and the
``revoke_api_key`` route sets ``api_key.is_active = False``, but the column
never existed on the model/table — every API-key lookup crashed with
``AttributeError: type object 'APIKey' has no attribute 'is_active'``. This
completes the soft-delete contract (regression coverage for finding
2f29e692's e2e flow: created keys must authenticate, revoked keys must not).

Revision ID: b7c8d9e0f1a2
Revises: a4f1c9e2b7d3
Create Date: 2026-08-01 16:20:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b7c8d9e0f1a2"
down_revision: str | None = "a4f1c9e2b7d3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "api_keys",
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
    )
    op.create_index("ix_api_keys_is_active", "api_keys", ["is_active"])


def downgrade() -> None:
    op.drop_index("ix_api_keys_is_active", table_name="api_keys")
    op.drop_column("api_keys", "is_active")
