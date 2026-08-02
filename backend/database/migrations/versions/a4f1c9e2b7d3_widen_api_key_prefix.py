"""widen_api_key_prefix

Widen ``api_keys.key_prefix`` from String(20) to String(32).

The generated key prefix is ``raw[:24]`` (sk_ + 21 hex chars) and must match
the ``token[:24]`` lookup slice in ``APIKeyAuth`` (backend/auth/manager.py).
The previous String(20) column would either truncate or reject the 24-char
value, making every created key unfindable.

Revision ID: a4f1c9e2b7d3
Revises: f36cadc3adde
Create Date: 2026-08-01 12:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a4f1c9e2b7d3"
down_revision: str | None = "f36cadc3adde"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column("api_keys", "key_prefix", type_=sa.String(length=32), nullable=False)


def downgrade() -> None:
    # NOTE: data-shrink — once 24-char prefixes exist, this will fail on
    # PostgreSQL (value too long for character varying(20)). Inherent to
    # shrinking a column; run only against an empty/dev database.
    op.alter_column("api_keys", "key_prefix", type_=sa.String(length=20), nullable=False)
