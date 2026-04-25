"""Initial Foundry schema.

Revision ID: 0001_initial
Revises:
Create Date: 2026-04-18

Creates the full v1 schema in one shot. Subsequent changes should be
incremental migrations.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _jsonb() -> sa.types.TypeEngine[object]:
    return postgresql.JSONB().with_variant(sa.JSON(), "sqlite")


def upgrade() -> None:
    # --- users / teams ------------------------------------------------------
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("email", sa.String(length=320), nullable=False, unique=True),
        sa.Column("display_name", sa.String(length=120), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "teams",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("slug", sa.String(length=80), nullable=False, unique=True),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # --- repositories -------------------------------------------------------
    op.create_table(
        "repositories",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("slug", sa.String(length=160), nullable=False, unique=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("provider", sa.String(length=32), nullable=False, server_default="local"),
        sa.Column("url", sa.String(length=1024), nullable=False),
        sa.Column("default_branch", sa.String(length=200), nullable=False, server_default="main"),
        sa.Column("local_path", sa.String(length=1024), nullable=True),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    # --- branches -----------------------------------------------------------
    op.create_table(
        "branches",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "repository_id",
            sa.String(length=36),
            sa.ForeignKey("repositories.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("name", sa.String(length=400), nullable=False),
        sa.Column("head_sha", sa.String(length=40), nullable=False, index=True),
        sa.Column("upstream_sha", sa.String(length=40), nullable=True),
        sa.Column("merge_base_sha", sa.String(length=40), nullable=True),
        sa.Column("ahead_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("behind_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("diverged_at_sha", sa.String(length=40), nullable=True),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("state", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("stale_reasons", _jsonb(), nullable=False, server_default="[]"),
        sa.Column(
            "readiness", sa.String(length=32), nullable=False, server_default="needs_review"
        ),
        sa.Column("last_author", sa.String(length=320), nullable=True),
        sa.Column("last_commit_at", sa.DateTime(timezone=True), nullable=True, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_branches_repo_name", "branches", ["repository_id", "name"], unique=True
    )
    op.create_index("ix_branches_state", "branches", ["state"])

    # --- commits ------------------------------------------------------------
    op.create_table(
        "commits",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "branch_id",
            sa.String(length=36),
            sa.ForeignKey("branches.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("sha", sa.String(length=40), nullable=False, index=True),
        sa.Column("short_sha", sa.String(length=12), nullable=False),
        sa.Column("author_name", sa.String(length=320), nullable=False),
        sa.Column("author_email", sa.String(length=320), nullable=False),
        sa.Column("committed_at", sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("files_changed", _jsonb(), nullable=False, server_default="[]"),
        sa.Column("additions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("deletions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("parents", _jsonb(), nullable=False, server_default="[]"),
    )
    op.create_index("ix_commits_branch_sha", "commits", ["branch_id", "sha"], unique=True)

    # --- pull requests ------------------------------------------------------
    op.create_table(
        "pull_requests",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "repository_id",
            sa.String(length=36),
            sa.ForeignKey("repositories.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "branch_id",
            sa.String(length=36),
            sa.ForeignKey("branches.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        ),
        sa.Column("number", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("state", sa.String(length=32), nullable=False, server_default="open"),
        sa.Column("url", sa.String(length=1024), nullable=True),
        sa.Column("author", sa.String(length=320), nullable=True),
        sa.Column("reviewers", _jsonb(), nullable=False, server_default="[]"),
        sa.Column("checks_passing", sa.Boolean(), nullable=True),
        sa.Column("opened_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("merged_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_prs_repo_number", "pull_requests", ["repository_id", "number"], unique=True)

    # --- summaries ----------------------------------------------------------
    op.create_table(
        "summaries",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "branch_id",
            sa.String(length=36),
            sa.ForeignKey("branches.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("headline", sa.String(length=400), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0"),
        sa.Column("evidence", _jsonb(), nullable=False, server_default="{}"),
        sa.Column("capabilities", _jsonb(), nullable=False, server_default="[]"),
        sa.Column(
            "generator", sa.String(length=80), nullable=False, server_default="deterministic-v1"
        ),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
    )

    # --- snapshots ----------------------------------------------------------
    op.create_table(
        "snapshots",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "repository_id",
            sa.String(length=36),
            sa.ForeignKey("repositories.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("taken_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("active_branches", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("stale_branches", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("open_prs", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("critical_findings", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("metrics", _jsonb(), nullable=False, server_default="{}"),
    )
    op.create_index("ix_snapshots_repo_taken", "snapshots", ["repository_id", "taken_at"])

    # --- hook manifests + features -----------------------------------------
    op.create_table(
        "hook_manifests",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "repository_id",
            sa.String(length=36),
            sa.ForeignKey("repositories.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("app", sa.String(length=160), nullable=False),
        sa.Column("version", sa.String(length=40), nullable=False, server_default="0.1"),
        sa.Column("raw", _jsonb(), nullable=False, server_default="{}"),
        sa.Column("source_path", sa.String(length=1024), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "features",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "manifest_id",
            sa.String(length=36),
            sa.ForeignKey("hook_manifests.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("paths", _jsonb(), nullable=False, server_default="[]"),
        sa.Column("signals", _jsonb(), nullable=False, server_default="[]"),
        sa.Column("description", sa.Text(), nullable=True),
    )
    op.create_index(
        "ix_features_manifest_name", "features", ["manifest_id", "name"], unique=True
    )

    # --- hook events --------------------------------------------------------
    op.create_table(
        "hook_events",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "repository_id",
            sa.String(length=36),
            sa.ForeignKey("repositories.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "branch_id",
            sa.String(length=36),
            sa.ForeignKey("branches.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        ),
        sa.Column(
            "feature_id",
            sa.String(length=36),
            sa.ForeignKey("features.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        ),
        sa.Column("signal", sa.String(length=160), nullable=False),
        sa.Column("payload", _jsonb(), nullable=False, server_default="{}"),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_hook_events_repo_received", "hook_events", ["repository_id", "received_at"]
    )

    # --- scan runs ----------------------------------------------------------
    op.create_table(
        "scan_runs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "repository_id",
            sa.String(length=36),
            sa.ForeignKey("repositories.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "branch_id",
            sa.String(length=36),
            sa.ForeignKey("branches.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        ),
        sa.Column("kind", sa.String(length=40), nullable=False, server_default="branch_sync"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("stats", _jsonb(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_scan_runs_repo_kind", "scan_runs", ["repository_id", "kind"])

    # --- findings -----------------------------------------------------------
    op.create_table(
        "findings",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "repository_id",
            sa.String(length=36),
            sa.ForeignKey("repositories.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "branch_id",
            sa.String(length=36),
            sa.ForeignKey("branches.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        ),
        sa.Column(
            "scan_run_id",
            sa.String(length=36),
            sa.ForeignKey("scan_runs.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        ),
        sa.Column("rule", sa.String(length=160), nullable=False),
        sa.Column("severity", sa.String(length=16), nullable=False, server_default="low"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="open"),
        sa.Column("title", sa.String(length=400), nullable=False),
        sa.Column("detail", sa.Text(), nullable=True),
        sa.Column("file_path", sa.String(length=1024), nullable=True),
        sa.Column("line", sa.Integer(), nullable=True),
        sa.Column("commit_sha", sa.String(length=40), nullable=True),
        sa.Column("on_main", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # --- policies -----------------------------------------------------------
    op.create_table(
        "policies",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("slug", sa.String(length=120), nullable=False, unique=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("spec", _jsonb(), nullable=False, server_default="{}"),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "policy_results",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "policy_id",
            sa.String(length=36),
            sa.ForeignKey("policies.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "repository_id",
            sa.String(length=36),
            sa.ForeignKey("repositories.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "branch_id",
            sa.String(length=36),
            sa.ForeignKey("branches.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        ),
        sa.Column("passed", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("detail", _jsonb(), nullable=False, server_default="{}"),
        sa.Column("evaluated_at", sa.DateTime(timezone=True), nullable=False),
    )

    # --- branch actions -----------------------------------------------------
    op.create_table(
        "branch_actions",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "branch_id",
            sa.String(length=36),
            sa.ForeignKey("branches.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("kind", sa.String(length=32), nullable=False, server_default="needs_review"),
        sa.Column("reason", sa.String(length=400), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_branch_actions_branch_kind", "branch_actions", ["branch_id", "kind"], unique=True
    )


def downgrade() -> None:
    for table in (
        "branch_actions",
        "policy_results",
        "policies",
        "findings",
        "scan_runs",
        "hook_events",
        "features",
        "hook_manifests",
        "snapshots",
        "summaries",
        "pull_requests",
        "commits",
        "branches",
        "repositories",
        "teams",
        "users",
    ):
        op.drop_table(table)
