"""Stale-branch classification."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from foundry_core.enums import BranchState, StaleReason


@dataclass(frozen=True)
class StaleAssessment:
    state: BranchState
    reasons: list[StaleReason] = field(default_factory=list)
    age_days: int = 0

    @property
    def is_stale(self) -> bool:
        return self.state in (BranchState.STALE, BranchState.ORPHANED)


def _age_days(last_commit_at: datetime | None, now: datetime) -> int:
    if last_commit_at is None:
        return 0
    delta = now - last_commit_at.astimezone(timezone.utc)
    return max(0, delta.days)


def classify_staleness(
    *,
    last_commit_at: datetime | None,
    ahead: int,
    behind: int,
    has_open_pr: bool,
    has_recent_owner_activity: bool,
    warn_days: int = 14,
    critical_days: int = 45,
    now: datetime | None = None,
) -> StaleAssessment:
    now = now or datetime.now(timezone.utc)
    age = _age_days(last_commit_at, now)
    reasons: list[StaleReason] = []

    if age >= critical_days:
        reasons.append(StaleReason.NO_RECENT_COMMITS)
    if not has_open_pr and age >= warn_days and ahead > 0:
        reasons.append(StaleReason.NO_PR_ACTIVITY)
    if ahead == 0 and behind == 0 and last_commit_at is not None:
        reasons.append(StaleReason.ORPHANED_FROM_MAIN)
    if not has_recent_owner_activity and age >= warn_days:
        reasons.append(StaleReason.NO_OWNER_ACTIVITY)

    if StaleReason.ORPHANED_FROM_MAIN in reasons and age >= critical_days:
        state = BranchState.ORPHANED
    elif reasons:
        state = BranchState.STALE if age >= warn_days else BranchState.ACTIVE
    else:
        state = BranchState.ACTIVE

    # De-duplicate reasons while preserving order
    seen: set[StaleReason] = set()
    uniq_reasons: list[StaleReason] = []
    for r in reasons:
        if r not in seen:
            uniq_reasons.append(r)
            seen.add(r)

    return StaleAssessment(state=state, reasons=uniq_reasons, age_days=age)
