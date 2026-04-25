"""Release control plane tables.

Revision ID: 0002_release_control_plane
Revises: 0001_initial
Create Date: 2026-04-25
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002_release_control_plane"
down_revision: str | Sequence[str] | None = "0001_initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _jsonb() -> sa.types.TypeEngine[object]:
    return postgresql.JSONB().with_variant(sa.JSON(), "sqlite")


def upgrade() -> None:
    op.create_table(
        "release_profiles",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "repository_id",
            sa.String(length=36),
            sa.ForeignKey("repositories.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("spec", _jsonb(), nullable=False, server_default="{}"),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_release_profiles_repository_id", "release_profiles", ["repository_id"])

    op.create_table(
        "release_runs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "repository_id",
            sa.String(length=36),
            sa.ForeignKey("repositories.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("branch_name", sa.String(length=200), nullable=False),
        sa.Column("base_ref", sa.String(length=200), nullable=False, server_default="origin/main"),
        sa.Column("range_expr", sa.String(length=400), nullable=True),
        sa.Column("passed", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("summary", _jsonb(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_release_runs_repo_created", "release_runs", ["repository_id", "created_at"])

    op.create_table(
        "release_findings",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "release_run_id",
            sa.String(length=36),
            sa.ForeignKey("release_runs.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("code", sa.String(length=120), nullable=False),
        sa.Column("severity", sa.String(length=32), nullable=False, server_default="info"),
        sa.Column("passed", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("message", sa.String(length=600), nullable=False),
        sa.Column("evidence", _jsonb(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_release_findings_run", "release_findings", ["release_run_id"])


def downgrade() -> None:
    op.drop_index("ix_release_findings_run", table_name="release_findings")
    op.drop_table("release_findings")
    op.drop_index("ix_release_runs_repo_created", table_name="release_runs")
    op.drop_table("release_runs")
    op.drop_index("ix_release_profiles_repository_id", table_name="release_profiles")
    op.drop_table("release_profiles")
