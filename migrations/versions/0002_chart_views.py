"""chart_views table

Revision ID: 0002_chart_views
Revises: 0001_initial
Create Date: 2026-09-23
"""

from __future__ import annotations

from alembic import op

from analytics.db import ChartView

revision = "0002_chart_views"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    ChartView.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    ChartView.__table__.drop(bind=op.get_bind(), checkfirst=True)
