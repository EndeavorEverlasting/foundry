"""Health + version endpoints (unversioned on purpose)."""

from __future__ import annotations

from fastapi import APIRouter

from foundry_api import __version__
from foundry_api.deps import SettingsDep
from foundry_core.schemas import HealthResponse

router = APIRouter(tags=["meta"])


@router.get("/health", response_model=HealthResponse)
async def health(settings: SettingsDep) -> HealthResponse:
    return HealthResponse(status="ok", env=settings.env, version=__version__)


@router.get("/version")
async def version() -> dict[str, str]:
    return {"version": __version__}
