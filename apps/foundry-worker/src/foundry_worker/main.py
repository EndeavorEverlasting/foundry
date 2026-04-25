"""Arq worker configuration. Entry point: `arq foundry_worker.main.WorkerSettings`."""

from __future__ import annotations

from typing import Any

from arq.connections import RedisSettings

from foundry_core.config import get_settings
from foundry_core.db import dispose_engine
from foundry_core.logging import configure_logging, get_logger
from foundry_worker.jobs.branch_sync import branch_sync
from foundry_worker.jobs.summary_regen import summary_regen


async def on_startup(ctx: dict[str, Any]) -> None:
    configure_logging()
    log = get_logger("foundry.worker")
    log.info("worker.startup", env=get_settings().env)
    ctx["log"] = log


async def on_shutdown(ctx: dict[str, Any]) -> None:
    log = ctx.get("log")
    if log is not None:
        log.info("worker.shutdown")
    await dispose_engine()


class WorkerSettings:
    """Arq worker settings. Job functions must be module-level callables."""

    functions = [branch_sync, summary_regen]
    on_startup = on_startup
    on_shutdown = on_shutdown
    max_jobs = 4
    job_timeout = 600  # seconds; deep histories can take a while
    keep_result = 3600
    allow_abort_jobs = True

    @classmethod
    @property
    def redis_settings(cls) -> RedisSettings:
        return RedisSettings.from_dsn(get_settings().redis_url)
