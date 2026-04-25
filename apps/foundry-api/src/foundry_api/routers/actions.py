"""/repos/{id}/actions — Action Center."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from foundry_api.deps import SessionDep
from foundry_api.services.action_service import build_action_center
from foundry_api.services.repo_service import get_repository
from foundry_core.schemas import ActionCenter

router = APIRouter(tags=["actions"])


@router.get("/repos/{repo_id}/actions", response_model=ActionCenter)
async def action_center(repo_id: str, session: SessionDep) -> ActionCenter:
    repo = await get_repository(session, repo_id)
    if repo is None:
        raise HTTPException(status_code=404, detail="repository not found")
    return await build_action_center(session, repo_id)
