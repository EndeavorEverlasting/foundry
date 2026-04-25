"""/branches + /repos/{id}/branches."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from foundry_api.deps import SessionDep
from foundry_api.services.branch_service import (
    branch_detail,
    get_branch,
    list_branches,
)
from foundry_core.enums import BranchState
from foundry_core.schemas import BranchDetail, BranchOut

router = APIRouter(tags=["branches"])


@router.get("/repos/{repo_id}/branches", response_model=list[BranchOut])
async def get_branches(
    repo_id: str,
    session: SessionDep,
    state: BranchState | None = None,
    stale_only: bool = False,
    author: str | None = Query(default=None, max_length=320),
    limit: int = Query(default=200, ge=1, le=1000),
) -> list[BranchOut]:
    return await list_branches(
        session,
        repo_id,
        state=state,
        stale_only=stale_only,
        author=author,
        limit=limit,
    )


@router.get("/branches/{branch_id}", response_model=BranchDetail)
async def get_branch_detail(branch_id: str, session: SessionDep) -> BranchDetail:
    branch = await get_branch(session, branch_id)
    if branch is None:
        raise HTTPException(status_code=404, detail="branch not found")
    return await branch_detail(session, branch)
