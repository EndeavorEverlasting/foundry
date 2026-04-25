"""/repos/{id}/drift — main drift panel."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from foundry_api.deps import SessionDep
from foundry_api.services.drift_service import build_drift_panel
from foundry_api.services.repo_service import get_repository
from foundry_core.schemas import DriftPanel

router = APIRouter(tags=["drift"])


@router.get("/repos/{repo_id}/drift", response_model=DriftPanel)
async def drift_panel(repo_id: str, session: SessionDep) -> DriftPanel:
    repo = await get_repository(session, repo_id)
    if repo is None:
        raise HTTPException(status_code=404, detail="repository not found")
    return await build_drift_panel(session, repo_id)
