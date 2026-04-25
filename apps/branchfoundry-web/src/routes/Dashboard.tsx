import { Link, useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  BranchStatePill,
  Button,
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  Empty,
  PageHeader,
  ReadinessPill,
  Skeleton,
  SkeletonText,
  Stat,
} from "@foundry/ui";
import { api } from "@/lib/api";
import { formatRelative, shortSha } from "@/lib/format";

export default function Dashboard() {
  const { repoId } = useParams<{ repoId: string }>();
  const qc = useQueryClient();

  const summaryQ = useQuery({
    queryKey: ["repo-summary", repoId],
    queryFn: () => api.repoSummary(repoId!),
    enabled: !!repoId,
  });
  const branchesQ = useQuery({
    queryKey: ["branches", repoId, "recent"],
    queryFn: () => api.listBranches(repoId!, { limit: 8 }),
    enabled: !!repoId,
  });
  const actionsQ = useQuery({
    queryKey: ["actions", repoId],
    queryFn: () => api.actions(repoId!),
    enabled: !!repoId,
  });

  const syncMut = useMutation({
    mutationFn: () => api.enqueueSync(repoId!),
    onSuccess: async () => {
      await qc.invalidateQueries({ queryKey: ["repo-summary", repoId] });
      await qc.invalidateQueries({ queryKey: ["branches"] });
      await qc.invalidateQueries({ queryKey: ["actions"] });
    },
  });

  if (!repoId) return null;

  const s = summaryQ.data;
  const branches = branchesQ.data ?? [];
  const actionKinds = Object.entries(actionsQ.data?.by_kind ?? {});

  return (
    <div>
      <PageHeader
        eyebrow="Repository"
        title={s?.repository.name ?? "Loading..."}
        description={
          s?.repository ? (
            <span className="font-mono text-xs">{s.repository.url}</span>
          ) : undefined
        }
        actions={
          <>
            <Button
              variant="secondary"
              onClick={() => syncMut.mutate()}
              disabled={syncMut.isPending}
            >
              {syncMut.isPending ? "Syncing..." : "Sync now"}
            </Button>
            <Link to={`/repos/${repoId}/graph`}>
              <Button>Open graph</Button>
            </Link>
          </>
        }
      />

      <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-8">
        <Stat
          label="Active branches"
          value={summaryQ.isLoading ? <Skeleton className="h-6 w-10" /> : s?.active_branches ?? 0}
          tone="neutral"
        />
        <Stat
          label="Stale branches"
          value={summaryQ.isLoading ? <Skeleton className="h-6 w-10" /> : s?.stale_branches ?? 0}
          tone={(s?.stale_branches ?? 0) > 0 ? "warn" : "neutral"}
        />
        <Stat
          label="Open PRs"
          value={summaryQ.isLoading ? <Skeleton className="h-6 w-10" /> : s?.open_prs ?? 0}
        />
        <Stat
          label="Critical findings"
          value={summaryQ.isLoading ? <Skeleton className="h-6 w-10" /> : s?.critical_findings ?? 0}
          tone={(s?.critical_findings ?? 0) > 0 ? "danger" : "neutral"}
          hint="GuardFoundry wiring up"
        />
        <Stat
          label="Last synced"
          value={
            summaryQ.isLoading
              ? <Skeleton className="h-6 w-24" />
              : <span className="text-base font-medium">{formatRelative(s?.last_synced_at)}</span>
          }
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Recent branches</CardTitle>
          </CardHeader>
          <CardContent>
            {branchesQ.isLoading ? (
              <SkeletonText lines={5} />
            ) : branches.length === 0 ? (
              <Empty
                title="No branches synced yet"
                description="Kick off a sync to populate this repo."
                action={
                  <Button
                    variant="secondary"
                    onClick={() => syncMut.mutate()}
                  >
                    Run sync
                  </Button>
                }
              />
            ) : (
              <ul className="divide-y divide-white/5">
                {branches.map((b) => (
                  <li key={b.id} className="py-3 flex items-center gap-3 min-w-0">
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2">
                        <Link
                          to={`/branches/${b.id}`}
                          className="text-sm font-medium text-fg-primary hover:text-accent-blue truncate"
                        >
                          {b.name}
                        </Link>
                        {b.is_default ? (
                          <span className="text-[10px] uppercase text-fg-tertiary tracking-wider">default</span>
                        ) : null}
                      </div>
                      <div className="text-xs text-fg-tertiary mt-0.5 flex items-center gap-2 flex-wrap">
                        <span className="font-mono">{shortSha(b.head_sha)}</span>
                        <span>·</span>
                        <span>↑{b.ahead_count} / ↓{b.behind_count}</span>
                        {b.last_author ? (
                          <>
                            <span>·</span>
                            <span>by {b.last_author}</span>
                          </>
                        ) : null}
                        {b.last_commit_at ? (
                          <>
                            <span>·</span>
                            <span>{formatRelative(b.last_commit_at)}</span>
                          </>
                        ) : null}
                      </div>
                    </div>
                    <div className="flex items-center gap-2 shrink-0">
                      <BranchStatePill state={b.state} />
                      <ReadinessPill readiness={b.readiness} />
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Action center</CardTitle>
          </CardHeader>
          <CardContent>
            {actionsQ.isLoading ? (
              <SkeletonText lines={4} />
            ) : actionKinds.length === 0 ? (
              <Empty title="Nothing to act on" description="You're clear." />
            ) : (
              <ul className="space-y-2">
                {actionKinds.map(([kind, cards]) => (
                  <li
                    key={kind}
                    className="flex items-center justify-between rounded-md border border-white/5 bg-surface/40 px-3 py-2"
                  >
                    <div className="text-sm text-fg-primary">{humanize(kind)}</div>
                    <div className="text-sm font-medium tabular-nums text-fg-secondary">
                      {cards?.length ?? 0}
                    </div>
                  </li>
                ))}
              </ul>
            )}
            <div className="mt-3">
              <div className="flex gap-2">
                <Link to={`/repos/${repoId}/actions`}>
                  <Button variant="ghost" size="sm">Open action center</Button>
                </Link>
                <Link to={`/repos/${repoId}/release`}>
                  <Button variant="ghost" size="sm">Release readiness</Button>
                </Link>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function humanize(kind: string): string {
  return kind
    .split("_")
    .map((w) => w[0]!.toUpperCase() + w.slice(1))
    .join(" ");
}
