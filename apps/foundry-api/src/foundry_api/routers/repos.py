"""/repos — registration, listing, summary, sync enqueue."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status

from foundry_api.deps import JobsDep, SessionDep
from foundry_api.services.repo_service import (
    create_repository,
    get_repository,
    list_repositories,
    summarize_repository,
)
from foundry_core.schemas import (
    EnqueueResponse,
    RepoSummary,
    RepositoryIn,
    RepositoryOut,
)

router = APIRouter(prefix="/repos", tags=["repositories"])


@router.get("", response_model=list[RepositoryOut])
async def get_repos(session: SessionDep) -> list[RepositoryOut]:
    return await list_repositories(session)


@router.post("", response_model=RepositoryOut, status_code=status.HTTP_201_CREATED)
async def register_repo(payload: RepositoryIn, session: SessionDep) -> RepositoryOut:
    return await create_repository(session, payload)


@router.get("/{repo_id}", response_model=RepositoryOut)
async def get_repo(repo_id: str, session: SessionDep) -> RepositoryOut:
    repo = await get_repository(session, repo_id)
    if repo is None:
        raise HTTPException(status_code=404, detail="repository not found")
    return RepositoryOut.model_validate(repo)


@router.get("/{repo_id}/summary", response_model=RepoSummary)
async def repo_summary(repo_id: str, session: SessionDep) -> RepoSummary:
    repo = await get_repository(session, repo_id)
    if repo is None:
        raise HTTPException(status_code=404, detail="repository not found")
    return await summarize_repository(session, repo)


@router.post("/{repo_id}/sync", response_model=EnqueueResponse)
async def enqueue_sync(repo_id: str, session: SessionDep, jobs: JobsDep) -> EnqueueResponse:
    repo = await get_repository(session, repo_id)
    if repo is None:
        raise HTTPException(status_code=404, detail="repository not found")
    job = await jobs.enqueue_job("branch_sync", repo_id)
    if job is None:
        raise HTTPException(status_code=503, detail="queue unavailable")
    return EnqueueResponse(job_id=job.job_id, enqueued_at=datetime.now(timezone.utc))
