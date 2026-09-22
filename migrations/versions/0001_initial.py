"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-09-23
"""

from __future__ import annotations

from alembic import op

from analytics.db import Base

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # The initial schema mirrors the SQLAlchemy models exactly; later revisions
    # should use explicit ops.
    Base.metadata.create_all(bind=op.get_bind())


def downgrade() -> None:
    Base.metadata.drop_all(bind=op.get_bind())
