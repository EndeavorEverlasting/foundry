"""FastAPI application factory."""

from __future__ import annotations

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from foundry_api import __version__
from foundry_api.jobs import close_job_pool, get_job_pool
from foundry_api.routers import (
    actions,
    branches,
    drift,
    graph,
    health,
    manifests,
    release,
    repos,
    stale,
)
from foundry_core.config import get_settings
from foundry_core.db import dispose_engine, get_engine
from foundry_core.logging import configure_logging, get_logger

configure_logging()
log = get_logger("foundry.api")


@asynccontextmanager
async def _lifespan(_: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    log.info("api.startup", env=settings.env, version=__version__)
    # Eagerly initialize engine + job pool so failures surface on boot.
    get_engine()
    await get_job_pool()
    try:
        yield
    finally:
        log.info("api.shutdown")
        await close_job_pool()
        await dispose_engine()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Foundry API",
        version=__version__,
        summary="BranchFoundry + GuardFoundry REST surface.",
        lifespan=_lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)

    v1_prefix = "/api/v1"
    app.include_router(repos.router, prefix=v1_prefix)
    app.include_router(branches.router, prefix=v1_prefix)
    app.include_router(graph.router, prefix=v1_prefix)
    app.include_router(stale.router, prefix=v1_prefix)
    app.include_router(actions.router, prefix=v1_prefix)
    app.include_router(drift.router, prefix=v1_prefix)
    app.include_router(manifests.router, prefix=v1_prefix)
    app.include_router(release.router, prefix=v1_prefix)

    return app


app = create_app()
