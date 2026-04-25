"""/repos/{id}/graph."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from foundry_api.deps import SessionDep
from foundry_api.services.graph_service import build_graph
from foundry_api.services.repo_service import get_repository
from foundry_core.schemas import GraphResponse

router = APIRouter(tags=["graph"])


@router.get("/repos/{repo_id}/graph", response_model=GraphResponse)
async def get_graph(repo_id: str, session: SessionDep) -> GraphResponse:
    repo = await get_repository(session, repo_id)
    if repo is None:
        raise HTTPException(status_code=404, detail="repository not found")
    return await build_graph(session, repo_id)
