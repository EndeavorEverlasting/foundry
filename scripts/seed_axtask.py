"""Seed the local AxTask repo into Foundry.

Idempotent: re-running updates the existing repo + manifest without
creating duplicates.

Usage:
  docker compose -f infra/compose/docker-compose.yml exec api \
      python -m scripts.seed_axtask
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import delete, select

from foundry_core.config import get_settings
from foundry_core.db import session_scope
from foundry_core.logging import configure_logging, get_logger
from foundry_core.models import Feature, HookManifest, Repository


REPO_NAME = "AxTask"
REPO_SLUG = "axtask"
DEFAULT_BRANCH = os.getenv("FOUNDRY_AXTASK_DEFAULT_BRANCH", "main")

# Path must exist *inside the container* (or host, if running bare metal).
# We default to /workspace/AxTask because people usually mount their dev
# folder one level above Foundry.
DEFAULT_LOCAL_PATH = os.getenv("FOUNDRY_AXTASK_PATH", "/workspace/AxTask")
MANIFEST_PATH = Path(__file__).parent.parent / "examples" / "axtask-integration" / "foundry.manifest.json"


async def main() -> int:
    configure_logging()
    log = get_logger("foundry.scripts.seed_axtask")
    _ = get_settings()

    if not MANIFEST_PATH.exists():
        log.error("seed.manifest_missing", path=str(MANIFEST_PATH))
        return 2

    manifest_data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    local_path = Path(DEFAULT_LOCAL_PATH)
    url = local_path.as_posix() if local_path.exists() else "file:///local/axtask"

    async with session_scope() as session:
        existing = await session.execute(select(Repository).where(Repository.slug == REPO_SLUG))
        repo = existing.scalar_one_or_none()
        now = datetime.now(timezone.utc)
        if repo is None:
            repo = Repository(
                slug=REPO_SLUG,
                name=REPO_NAME,
                provider="local",
                url=url,
                default_branch=DEFAULT_BRANCH,
                local_path=str(local_path) if local_path.exists() else None,
                created_at=now,
                updated_at=now,
            )
            session.add(repo)
            await session.flush()
            log.info("seed.repo_created", id=repo.id, slug=repo.slug)
        else:
            repo.url = url
            repo.local_path = str(local_path) if local_path.exists() else repo.local_path
            repo.default_branch = DEFAULT_BRANCH
            repo.updated_at = now
            log.info("seed.repo_updated", id=repo.id, slug=repo.slug)

        # Remove existing manifests + features for this repo
        old_rs = await session.execute(
            select(HookManifest).where(HookManifest.repository_id == repo.id)
        )
        for old in old_rs.scalars().all():
            await session.execute(delete(Feature).where(Feature.manifest_id == old.id))
            await session.delete(old)

        manifest = HookManifest(
            repository_id=repo.id,
            app=manifest_data["app"],
            version=manifest_data.get("version", "0.1"),
            raw=manifest_data,
            source_path=str(MANIFEST_PATH),
            created_at=now,
        )
        session.add(manifest)
        await session.flush()

        for f in manifest_data.get("features", []):
            session.add(
                Feature(
                    manifest_id=manifest.id,
                    name=f["name"],
                    paths=list(f.get("paths", [])),
                    signals=list(f.get("signals", [])),
                    description=f.get("description"),
                )
            )

        log.info(
            "seed.manifest_written",
            manifest_id=manifest.id,
            feature_count=len(manifest_data.get("features", [])),
        )

    log.info("seed.done")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
