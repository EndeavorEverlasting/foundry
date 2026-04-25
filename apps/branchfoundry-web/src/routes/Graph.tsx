import { useMemo, useState, useCallback, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import ReactFlow, {
  Background,
  BackgroundVariant,
  Controls,
  Handle,
  MiniMap,
  Position,
  type Edge,
  type Node,
  type NodeProps,
} from "reactflow";
import "reactflow/dist/style.css";
import {
  BranchStatePill,
  Card,
  CardContent,
  Empty,
  EvidenceDrawer,
  PageHeader,
  ReadinessPill,
  Skeleton,
  cn,
  type EvidenceBundle,
} from "@foundry/ui";
import { api } from "@/lib/api";
import { shortSha } from "@/lib/format";
import { usePersistentState } from "@/lib/savedFilters";

type CommitNodeData = {
  shortSha: string;
  label: string | null;
  isHead: boolean;
  isMergeBase: boolean;
  isDefault: boolean;
  branchId: string | null;
};

const nodeTypes = {
  commit: CommitNode,
};

export default function Graph() {
  const { repoId } = useParams<{ repoId: string }>();
  const navigate = useNavigate();

  const [activeBranchId, setActiveBranchId] = useState<string | null>(null);
  const [evidenceOpen, setEvidenceOpen] = useState(false);
  const [filters, setFilters] = usePersistentState<GraphFilters>(`graph-filters:${repoId}`, {
    hideStale: false,
    onlyDefault: false,
    q: "",
  });

  const graphQ = useQuery({
    queryKey: ["graph", repoId],
    queryFn: () => api.graph(repoId!),
    enabled: !!repoId,
  });
  const branchesQ = useQuery({
    queryKey: ["branches", repoId, "all"],
    queryFn: () => api.listBranches(repoId!, { limit: 500 }),
    enabled: !!repoId,
  });

  const branchById = useMemo(() => {
    const map = new Map<string, (typeof branchesQ.data)[number]>();
    for (const b of branchesQ.data ?? []) map.set(b.id, b);
    return map;
  }, [branchesQ.data]);

  const filteredBranchIds = useMemo(() => {
    const all = Array.from(branchById.values());
    const q = filters.q.trim().toLowerCase();
    return new Set(
      all
        .filter((b) => !filters.onlyDefault || b.is_default)
        .filter((b) => !filters.hideStale || (b.state !== "stale" && b.state !== "orphaned"))
        .filter((b) => (q ? b.name.toLowerCase().includes(q) : true))
        .map((b) => b.id),
    );
  }, [branchById, filters]);

  const { nodes, edges } = useMemo(() => {
    const g = graphQ.data;
    if (!g) return { nodes: [], edges: [] };
    const keep = new Set<string>();
    const nodes: Node<CommitNodeData>[] = g.nodes
      .filter((n) => !n.branch_id || filteredBranchIds.has(n.branch_id))
      .map((n) => {
        keep.add(n.id);
        return {
          id: n.id,
          position: { x: n.x, y: n.y },
          type: "commit",
          data: {
            shortSha: n.short_sha,
            label: n.label,
            isHead: n.is_head,
            isMergeBase: n.is_merge_base,
            isDefault: n.is_default,
            branchId: n.branch_id,
          },
        } satisfies Node<CommitNodeData>;
      });
    const edges: Edge[] = g.edges
      .filter((e) => keep.has(e.source) && keep.has(e.target))
      .map((e) => ({
        id: e.id,
        source: e.source,
        target: e.target,
        type: "smoothstep",
        animated: e.kind === "merge",
        style: {
          stroke: e.kind === "merge" ? "hsl(210 95% 62%)" : "hsl(222 18% 28%)",
          strokeWidth: e.kind === "merge" ? 2 : 1.2,
        },
      }));
    return { nodes, edges };
  }, [graphQ.data, filteredBranchIds]);

  const activeBranch = activeBranchId ? branchById.get(activeBranchId) : undefined;
  const activeDetailQ = useQuery({
    queryKey: ["branch", activeBranchId],
    queryFn: () => api.getBranch(activeBranchId!),
    enabled: !!activeBranchId && evidenceOpen,
  });

  const onNodeClick = useCallback(
    (_: unknown, node: Node<CommitNodeData>) => {
      if (!node.data.branchId) return;
      setActiveBranchId(node.data.branchId);
      setEvidenceOpen(true);
    },
    [],
  );

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") setEvidenceOpen(false);
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  return (
    <div>
      <PageHeader
        eyebrow="Branch graph"
        title="Interactive DAG"
        description="Each lane is a branch. Click a commit to open the branch's evidence drawer."
      />

      <Card className="mb-4">
        <CardContent className="py-3">
          <div className="flex flex-wrap gap-3 items-center">
            <input
              value={filters.q}
              onChange={(e) => setFilters({ ...filters, q: e.target.value })}
              placeholder="Filter branches..."
              className="h-8 px-3 rounded-md bg-surface border border-white/10 text-sm placeholder:text-fg-tertiary focus:outline-none focus:border-accent-blue/50"
            />
            <label className="flex items-center gap-2 text-sm text-fg-secondary">
              <input
                type="checkbox"
                checked={filters.hideStale}
                onChange={(e) => setFilters({ ...filters, hideStale: e.target.checked })}
              />
              Hide stale/orphaned
            </label>
            <label className="flex items-center gap-2 text-sm text-fg-secondary">
              <input
                type="checkbox"
                checked={filters.onlyDefault}
                onChange={(e) => setFilters({ ...filters, onlyDefault: e.target.checked })}
              />
              Only default branch
            </label>
            <div className="ml-auto text-xs text-fg-tertiary">
              {nodes.length} nodes · {edges.length} edges
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="relative h-[620px] rounded-lg overflow-hidden border border-white/5 bg-surface/30">
        {graphQ.isLoading ? (
          <Skeleton className="absolute inset-0" />
        ) : nodes.length === 0 ? (
          <div className="absolute inset-0 flex items-center justify-center p-6">
            <Empty
              title="No graph data"
              description="Run a sync to ingest commits and build the DAG."
            />
          </div>
        ) : (
          <ReactFlow
            nodes={nodes}
            edges={edges}
            nodeTypes={nodeTypes}
            onNodeClick={onNodeClick}
            fitView
            minZoom={0.2}
            maxZoom={2}
            proOptions={{ hideAttribution: true }}
          >
            <Background variant={BackgroundVariant.Dots} gap={24} size={1} color="hsl(222 18% 18%)" />
            <MiniMap
              maskColor="rgba(0,0,0,0.6)"
              nodeColor={(n) => {
                const d = n.data as CommitNodeData;
                if (d.isDefault) return "hsl(210 95% 62%)";
                if (d.isMergeBase) return "hsl(262 72% 66%)";
                return "hsl(215 18% 72%)";
              }}
              nodeStrokeColor="transparent"
              style={{ background: "hsl(222 25% 10%)", borderColor: "hsl(222 18% 18%)" }}
            />
            <Controls />
          </ReactFlow>
        )}
      </div>

      <EvidenceDrawer
        open={evidenceOpen}
        onClose={() => setEvidenceOpen(false)}
        subtitle={activeBranch?.name}
        title={
          activeBranch ? (
            <span className="inline-flex items-center gap-2">
              {activeBranch.name}
              <BranchStatePill state={activeBranch.state} />
              <ReadinessPill readiness={activeBranch.readiness} />
            </span>
          ) : (
            "Branch"
          )
        }
        confidence={activeDetailQ.data?.latest_summary?.confidence}
        summaryBody={activeDetailQ.data?.latest_summary?.body}
        evidence={(activeDetailQ.data?.latest_summary?.evidence as EvidenceBundle | null) ?? null}
      />

      {activeBranchId ? (
        <div className="mt-4 text-sm">
          <button
            className="text-accent-blue hover:underline"
            onClick={() => navigate(`/branches/${activeBranchId}`)}
          >
            Open full branch detail →
          </button>
        </div>
      ) : null}
    </div>
  );
}

type GraphFilters = {
  hideStale: boolean;
  onlyDefault: boolean;
  q: string;
};

function CommitNode({ data }: NodeProps<CommitNodeData>) {
  const tone = data.isDefault
    ? "bg-accent-blue/15 border-accent-blue/50 text-fg-primary"
    : data.isHead
      ? "bg-state-success/15 border-state-success/40 text-fg-primary"
      : data.isMergeBase
        ? "bg-accent-violet/15 border-accent-violet/40 text-fg-primary"
        : "bg-surface border-white/10 text-fg-secondary";
  return (
    <div
      className={cn(
        "px-2 py-1 rounded-md border text-[11px] font-mono shadow-sm cursor-pointer",
        tone,
      )}
      title={data.label ?? undefined}
    >
      <Handle type="target" position={Position.Left} className="!bg-white/10 !border-0" />
      <span>{shortSha(data.shortSha, 7)}</span>
      <Handle type="source" position={Position.Right} className="!bg-white/10 !border-0" />
    </div>
  );
}
