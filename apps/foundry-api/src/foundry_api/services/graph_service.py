"""Build a React-Flow-friendly branch DAG payload.

Server-side lane assignment: each branch gets a horizontal lane; commits
are placed along their branch's lane in chronological order. Edges track
`parents[0]` to keep things visually clean (merge commits still get
multiple edges).
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from foundry_core.models import Branch, Commit
from foundry_core.schemas import GraphEdge, GraphNode, GraphResponse


COMMIT_X_STEP = 80
LANE_Y_STEP = 72
LANE_Y_OFFSET = 40


async def build_graph(
    session: AsyncSession, repo_id: str, *, per_branch_limit: int = 40
) -> GraphResponse:
    branches_rs = await session.execute(
        select(Branch)
        .where(Branch.repository_id == repo_id)
        .order_by(Branch.is_default.desc(), Branch.updated_at.desc())
    )
    branches = list(branches_rs.scalars().all())

    if not branches:
        return GraphResponse(repository_id=repo_id, nodes=[], edges=[], lanes={})

    # Assign lanes (default branch gets lane 0).
    lanes: dict[str, int] = {}
    for idx, b in enumerate(branches):
        lanes[b.id] = idx

    nodes: list[GraphNode] = []
    edges: list[GraphEdge] = []
    sha_to_node: dict[str, str] = {}
    # Track the earliest (leftmost) global x by timestamp so the graph reads left-to-right.
    min_ts: datetime | None = None

    # First pass: find oldest commit timestamp so we can normalize X positions.
    commit_ts_by_sha: dict[str, datetime] = {}
    commits_by_branch: dict[str, list[Commit]] = defaultdict(list)
    for b in branches:
        cs_rs = await session.execute(
            select(Commit)
            .where(Commit.branch_id == b.id)
            .order_by(Commit.committed_at.asc())
            .limit(per_branch_limit)
        )
        cs = list(cs_rs.scalars().all())
        commits_by_branch[b.id] = cs
        for c in cs:
            commit_ts_by_sha.setdefault(c.sha, c.committed_at)
            if min_ts is None or c.committed_at < min_ts:
                min_ts = c.committed_at

    def x_for(ts: datetime) -> int:
        if min_ts is None:
            return 0
        # 1 step per 6 hours so long histories don't blow out horizontally.
        seconds = (ts - min_ts).total_seconds()
        return int((seconds / 21600) * COMMIT_X_STEP)

    # Second pass: emit nodes + intra-branch edges.
    for b in branches:
        lane = lanes[b.id]
        y = LANE_Y_OFFSET + lane * LANE_Y_STEP
        prev_node_id: str | None = None
        for c in commits_by_branch[b.id]:
            node_id = f"c:{c.sha}:{b.id}"
            is_head = c.sha == b.head_sha
            is_mb = bool(b.merge_base_sha) and c.sha == b.merge_base_sha
            nodes.append(
                GraphNode(
                    id=node_id,
                    branch_id=b.id,
                    commit_sha=c.sha,
                    short_sha=c.short_sha,
                    lane=lane,
                    x=x_for(c.committed_at),
                    y=y,
                    label=(c.message.splitlines()[0][:80] if c.message else None),
                    is_head=is_head,
                    is_merge_base=is_mb,
                    is_default=b.is_default,
                )
            )
            sha_to_node[c.sha] = node_id
            if prev_node_id is not None:
                edges.append(
                    GraphEdge(
                        id=f"e:{prev_node_id}->{node_id}",
                        source=prev_node_id,
                        target=node_id,
                        kind="lane",
                    )
                )
            prev_node_id = node_id

    # Third pass: merge edges across branches.
    for b in branches:
        for c in commits_by_branch[b.id]:
            if len(c.parents) <= 1:
                continue
            target_id = sha_to_node.get(c.sha)
            if target_id is None:
                continue
            for parent_sha in c.parents[1:]:
                src = sha_to_node.get(parent_sha)
                if src is None:
                    continue
                edges.append(
                    GraphEdge(
                        id=f"m:{src}->{target_id}",
                        source=src,
                        target=target_id,
                        kind="merge",
                    )
                )

    branch_lanes = {b.name: lanes[b.id] for b in branches}
    return GraphResponse(repository_id=repo_id, nodes=nodes, edges=edges, lanes=branch_lanes)
