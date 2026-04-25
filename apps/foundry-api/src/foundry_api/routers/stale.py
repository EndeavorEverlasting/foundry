"""/repos/{id}/stale."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from foundry_api.deps import SessionDep
from foundry_api.services.repo_service import get_repository
from foundry_api.services.stale_service import build_stale_view
from foundry_core.schemas import StaleView

router = APIRouter(tags=["stale"])


@router.get("/repos/{repo_id}/stale", response_model=StaleView)
async def stale_view(repo_id: str, session: SessionDep) -> StaleView:
    repo = await get_repository(session, repo_id)
    if repo is None:
        raise HTTPException(status_code=404, detail="repository not found")
    return await build_stale_view(session, repo_id)
