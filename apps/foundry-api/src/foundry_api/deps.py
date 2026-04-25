"""FastAPI dependency providers."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Annotated

from arq import ArqRedis
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from foundry_api.jobs import get_job_pool
from foundry_core.config import Settings, get_settings
from foundry_core.db import get_sessionmaker


async def get_session() -> AsyncIterator[AsyncSession]:
    sm = get_sessionmaker()
    async with sm() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def settings_dep() -> Settings:
    return get_settings()


async def jobs_dep() -> ArqRedis:
    return await get_job_pool()


SessionDep = Annotated[AsyncSession, Depends(get_session)]
SettingsDep = Annotated[Settings, Depends(settings_dep)]
JobsDep = Annotated[ArqRedis, Depends(jobs_dep)]
