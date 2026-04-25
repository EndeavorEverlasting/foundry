"""/repos/{id}/manifest — upload/update foundry.manifest.json."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Body, HTTPException
from sqlalchemy import select

from foundry_api.deps import SessionDep
from foundry_api.services.repo_service import get_repository
from foundry_core.models import Feature, HookManifest
from foundry_core.schemas import ManifestFeature, ManifestIn, ManifestOut
from foundry_hooks_sdk import ManifestError, validate_manifest_dict

router = APIRouter(tags=["manifests"])


@router.post("/repos/{repo_id}/manifest", response_model=ManifestOut)
async def upsert_manifest(
    repo_id: str,
    session: SessionDep,
    payload: dict = Body(...),
) -> ManifestOut:
    repo = await get_repository(session, repo_id)
    if repo is None:
        raise HTTPException(status_code=404, detail="repository not found")

    try:
        manifest = validate_manifest_dict(payload)
    except ManifestError as exc:
        raise HTTPException(status_code=422, detail={"errors": exc.messages}) from exc

    # Remove existing manifests for this repo (one-per-repo in v1).
    existing = await session.execute(
        select(HookManifest).where(HookManifest.repository_id == repo_id)
    )
    for old in existing.scalars().all():
        await session.delete(old)

    row = HookManifest(
        repository_id=repo_id,
        app=manifest.app,
        version=manifest.version,
        raw=payload,
        source_path=None,
        created_at=datetime.now(timezone.utc),
    )
    session.add(row)
    await session.flush()

    for f in manifest.features:
        session.add(
            Feature(
                manifest_id=row.id,
                name=f.name,
                paths=list(f.paths),
                signals=list(f.signals),
                description=f.description,
            )
        )

    # Validate ManifestIn shape for response
    manifest_in = ManifestIn.model_validate(payload)
    features_out = [
        ManifestFeature(
            name=f.name,
            paths=list(f.paths),
            signals=list(f.signals),
            description=f.description,
        )
        for f in manifest_in.features
    ]
    return ManifestOut(
        id=row.id,
        repository_id=row.repository_id,
        app=row.app,
        version=row.version,
        features=features_out,
        release=manifest_in.release,
    )


@router.get("/repos/{repo_id}/manifest", response_model=ManifestOut)
async def get_manifest(repo_id: str, session: SessionDep) -> ManifestOut:
    result = await session.execute(
        select(HookManifest).where(HookManifest.repository_id == repo_id)
    )
    manifest = result.scalar_one_or_none()
    if manifest is None:
        raise HTTPException(status_code=404, detail="manifest not found")

    features_rs = await session.execute(
        select(Feature).where(Feature.manifest_id == manifest.id).order_by(Feature.name)
    )
    features = [
        ManifestFeature(
            name=f.name,
            paths=list(f.paths or []),
            signals=list(f.signals or []),
            description=f.description,
        )
        for f in features_rs.scalars().all()
    ]
    return ManifestOut(
        id=manifest.id,
        repository_id=manifest.repository_id,
        app=manifest.app,
        version=manifest.version,
        features=features,
        release=ManifestIn.model_validate(manifest.raw).release
        if manifest.raw
        else None,
    )
