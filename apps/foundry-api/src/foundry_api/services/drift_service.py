"""Main-drift panel assembly."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from foundry_analysis.drift import compute_release_readiness_score
from foundry_core.models import Branch
from foundry_core.schemas import BranchOut, DriftEntry, DriftPanel
from foundry_core.enums import ConflictRisk


async def build_drift_panel(session: AsyncSession, repo_id: str) -> DriftPanel:
    rs = await session.execute(
        select(Branch).where(Branch.repository_id == repo_id, ~Branch.is_default)
    )
    branches = list(rs.scalars().all())

    main_missing: list[DriftEntry] = []
    behind_main: list[DriftEntry] = []
    total_ahead = 0
    total_behind = 0
    risk_summary: dict[str, int] = {}

    for b in branches:
        risk = b.conflict_risk if b.conflict_risk in {"none", "low", "medium", "high"} else "low"
        score = compute_release_readiness_score(
            conflict_risk=ConflictRisk(risk),
            ahead=b.ahead_count,
            behind=b.behind_count,
            checks_passing=None,
        )
        entry = DriftEntry(
            branch=BranchOut.model_validate(b),
            ahead=b.ahead_count,
            behind=b.behind_count,
            conflict_risk=risk,
            readiness=b.readiness,
            release_score=score,
        )
        if b.ahead_count > 0:
            main_missing.append(entry)
            total_ahead += b.ahead_count
        if b.behind_count > 0:
            behind_main.append(entry)
            total_behind += b.behind_count
        risk_summary[risk] = risk_summary.get(risk, 0) + 1

    main_missing.sort(key=lambda e: -e.ahead)
    behind_main.sort(key=lambda e: -e.behind)

    return DriftPanel(
        repository_id=repo_id,
        main_missing=main_missing,
        behind_main=behind_main,
        total_ahead=total_ahead,
        total_behind=total_behind,
        risk_summary=risk_summary,
    )
