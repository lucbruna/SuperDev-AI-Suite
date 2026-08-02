"""add_app_settings

Create the ``app_settings`` key/value table used by the Settings API.

Previously the table was created lazily via ``CREATE TABLE IF NOT EXISTS`` in
``backend/api/v1/settings.py`` with SQLite-flavored DDL (``datetime('now')``),
which is invalid on PostgreSQL — so settings silently failed to persist on the
primary database. This migration creates the table with proper PostgreSQL
types; ``settings_service`` still guards with ``CREATE TABLE IF NOT EXISTS`` as
a defensive fallback, but the real source of truth is this migration.

Revision ID: c1d2e3f4a5b6
Revises: b7c8d9e0f1a2
Create Date: 2026-08-01 17:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c1d2e3f4a5b6"
down_revision: str | None = "b7c8d9e0f1a2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "app_settings",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("key", sa.Text(), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("category", sa.Text(), server_default="general", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key"),
    )


def downgrade() -> None:
    op.drop_table("app_settings")
