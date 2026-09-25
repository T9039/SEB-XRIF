"""evaluations.source column

Revision ID: 0003_evaluation_source
Revises: 0002_chart_views
Create Date: 2026-09-25
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0003_evaluation_source"
down_revision = "0002_chart_views"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 0001 builds the schema from the current models, so on a fresh database
    # this column already exists; only add it to databases created before it.
    columns = {
        column["name"]
        for column in sa.inspect(op.get_bind()).get_columns("evaluations")
    }
    if "source" not in columns:
        op.add_column(
            "evaluations",
            sa.Column("source", sa.String(64), nullable=False, server_default="pilot"),
        )
    indexes = {
        index["name"] for index in sa.inspect(op.get_bind()).get_indexes("evaluations")
    }
    if "ix_evaluations_source" not in indexes:
        op.create_index("ix_evaluations_source", "evaluations", ["source"])


def downgrade() -> None:
    op.drop_index("ix_evaluations_source", table_name="evaluations")
    op.drop_column("evaluations", "source")
