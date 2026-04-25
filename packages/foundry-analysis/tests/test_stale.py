from datetime import datetime, timedelta, timezone

from foundry_analysis.stale import classify_staleness
from foundry_core.enums import BranchState, StaleReason


NOW = datetime(2026, 4, 18, tzinfo=timezone.utc)


def test_active_branch() -> None:
    a = classify_staleness(
        last_commit_at=NOW - timedelta(days=2),
        ahead=3,
        behind=0,
        has_open_pr=True,
        has_recent_owner_activity=True,
        now=NOW,
    )
    assert a.state is BranchState.ACTIVE
    assert a.reasons == []


def test_stale_after_warn_days() -> None:
    a = classify_staleness(
        last_commit_at=NOW - timedelta(days=20),
        ahead=2,
        behind=1,
        has_open_pr=False,
        has_recent_owner_activity=False,
        warn_days=14,
        critical_days=45,
        now=NOW,
    )
    assert a.state is BranchState.STALE
    assert StaleReason.NO_PR_ACTIVITY in a.reasons
    assert StaleReason.NO_OWNER_ACTIVITY in a.reasons


def test_orphaned_after_critical_days() -> None:
    a = classify_staleness(
        last_commit_at=NOW - timedelta(days=60),
        ahead=0,
        behind=0,
        has_open_pr=False,
        has_recent_owner_activity=False,
        warn_days=14,
        critical_days=45,
        now=NOW,
    )
    assert a.state is BranchState.ORPHANED
    assert StaleReason.ORPHANED_FROM_MAIN in a.reasons
    assert StaleReason.NO_RECENT_COMMITS in a.reasons
