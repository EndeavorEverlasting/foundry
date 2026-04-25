"""Release readiness routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from foundry_api.deps import SessionDep
from foundry_api.services.release_service import (
    get_release_profile,
    get_release_run,
    run_deploy_action,
    run_release_check,
    update_release_profile,
)
from foundry_api.services.repo_service import get_repository
from foundry_core.schemas import (
    ReleaseCheckRequest,
    ReleaseDeployRequest,
    ReleaseDeployResult,
    ReleaseProfileOut,
    ReleaseProfileUpdate,
    ReleaseRunOut,
)

router = APIRouter(prefix="/release", tags=["release"])


@router.post("/check/{repo_id}", response_model=ReleaseRunOut)
async def release_check(
    repo_id: str, payload: ReleaseCheckRequest, session: SessionDep
) -> ReleaseRunOut:
    repo = await get_repository(session, repo_id)
    if repo is None:
        raise HTTPException(status_code=404, detail="repository not found")
    try:
        return await run_release_check(session, repo, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/runs/{run_id}", response_model=ReleaseRunOut)
async def release_run(run_id: str, session: SessionDep) -> ReleaseRunOut:
    try:
        return await get_release_run(session, run_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/profiles/{repo_id}", response_model=ReleaseProfileOut)
async def release_profile(repo_id: str, session: SessionDep) -> ReleaseProfileOut:
    repo = await get_repository(session, repo_id)
    if repo is None:
        raise HTTPException(status_code=404, detail="repository not found")
    return await get_release_profile(session, repo_id)


@router.put("/profiles/{repo_id}", response_model=ReleaseProfileOut)
async def release_profile_update(
    repo_id: str, payload: ReleaseProfileUpdate, session: SessionDep
) -> ReleaseProfileOut:
    repo = await get_repository(session, repo_id)
    if repo is None:
        raise HTTPException(status_code=404, detail="repository not found")
    updated = await update_release_profile(
        session, repo_id, enabled=payload.enabled, spec=payload.spec
    )
    return ReleaseProfileOut.model_validate(updated)


@router.post("/deploy/{action}/{repo_id}", response_model=ReleaseDeployResult)
async def release_deploy_action(
    action: str, repo_id: str, payload: ReleaseDeployRequest, session: SessionDep
) -> ReleaseDeployResult:
    if action not in {"preview", "promote", "rollback"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid action")
    repo = await get_repository(session, repo_id)
    if repo is None:
        raise HTTPException(status_code=404, detail="repository not found")
    try:
        return await run_deploy_action(session, repo, action, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
