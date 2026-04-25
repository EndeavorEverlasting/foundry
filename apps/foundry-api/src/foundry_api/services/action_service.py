"""Assemble the Action Center payload."""

from __future__ import annotations

from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from foundry_core.enums import ActionKind
from foundry_core.models import Branch, BranchAction
from foundry_core.schemas import ActionCard, ActionCenter, BranchOut


async def build_action_center(session: AsyncSession, repo_id: str) -> ActionCenter:
    rs = await session.execute(
        select(BranchAction, Branch)
        .join(Branch, Branch.id == BranchAction.branch_id)
        .where(Branch.repository_id == repo_id)
        .order_by(BranchAction.priority.desc(), Branch.updated_at.desc())
    )

    by_kind: dict[ActionKind, list[ActionCard]] = defaultdict(list)
    for action, branch in rs.all():
        card = ActionCard(
            branch=BranchOut.model_validate(branch),
            kind=action.kind,
            reason=action.reason,
            priority=action.priority,
        )
        by_kind[action.kind].append(card)

    return ActionCenter(repository_id=repo_id, by_kind=dict(by_kind))
