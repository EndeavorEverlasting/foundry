"""Regenerate summaries for a single branch without touching Git.

Useful when the manifest changes: we want to re-run capability inference
against already-ingested data.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from foundry_analysis import (
    BranchFacts,
    DeterministicSummaryProvider,
    match_capabilities,
)
from foundry_core.db import session_scope
from foundry_core.logging import get_logger
from foundry_core.models import (
    Branch,
    Commit,
    Feature,
    HookManifest,
    Repository,
    Summary,
)

log = get_logger("foundry.worker.summary_regen")


async def summary_regen(ctx: dict[str, Any], branch_id: str) -> dict[str, str]:
    async with session_scope() as session:
        branch = await session.get(Branch, branch_id)
        if branch is None:
            return {"error": "branch_not_found"}
        repo = await session.get(Repository, branch.repository_id)
        if repo is None:
            return {"error": "repo_not_found"}

        feature_map = await _feature_map(session, repo.id)
        commits = await _recent_commits(session, branch.id)
        files_touched: set[str] = set()
        authors: set[str] = set()
        shas: list[str] = []
        last_commit_at = branch.last_commit_at
        last_author = branch.last_author
        tests_touched: set[str] = set()
        for c in commits:
            shas.append(c.sha)
            authors.add(c.author_name)
            for f in c.files_changed or []:
                files_touched.add(f)
                if _looks_like_test(f):
                    tests_touched.add(f)

        caps = (
            match_capabilities(files_changed=sorted(files_touched), features=feature_map)
            if feature_map
            else []
        )
        facts = BranchFacts(
            repo_name=repo.name,
            branch_name=branch.name,
            default_branch=repo.default_branch,
            ahead=branch.ahead_count,
            behind=branch.behind_count,
            last_commit_at=last_commit_at,
            last_author=last_author,
            commit_shas=shas[:50],
            files_touched=sorted(files_touched)[:200],
            authors=sorted(authors),
            tests_touched=sorted(tests_touched),
            capability_matches=caps,
        )
        result = DeterministicSummaryProvider().summarize(facts)

        await session.execute(delete(Summary).where(Summary.branch_id == branch.id))
        session.add(
            Summary(
                branch_id=branch.id,
                headline=result.headline,
                body=result.body,
                confidence=result.confidence,
                evidence=result.evidence.model_dump(),
                capabilities=result.capabilities,
                generator=result.generator,
                generated_at=datetime.now(timezone.utc),
            )
        )

    log.info("summary_regen.ok", branch_id=branch_id)
    return {"status": "ok"}


async def _feature_map(session: AsyncSession, repo_id: str) -> dict[str, list[str]]:
    m_rs = await session.execute(
        select(HookManifest).where(HookManifest.repository_id == repo_id)
    )
    manifests = list(m_rs.scalars().all())
    if not manifests:
        return {}
    f_rs = await session.execute(
        select(Feature).where(Feature.manifest_id.in_([m.id for m in manifests]))
    )
    return {f.name: list(f.paths or []) for f in f_rs.scalars().all()}


async def _recent_commits(session: AsyncSession, branch_id: str) -> list[Commit]:
    rs = await session.execute(
        select(Commit)
        .where(Commit.branch_id == branch_id)
        .order_by(Commit.committed_at.desc())
        .limit(100)
    )
    return list(rs.scalars().all())


def _looks_like_test(path: str) -> bool:
    p = path.lower().replace("\\", "/")
    return (
        "/test" in p
        or "/tests/" in p
        or p.endswith("_test.py")
        or p.endswith(".spec.ts")
        or p.endswith(".spec.tsx")
        or p.endswith(".test.ts")
        or p.endswith(".test.tsx")
        or p.endswith(".test.js")
    )
