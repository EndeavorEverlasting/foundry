import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import {
  AheadBehind,
  BranchStatePill,
  Button,
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  ConfidenceBadge,
  Empty,
  EvidenceDrawer,
  PageHeader,
  ReadinessPill,
  Skeleton,
  SkeletonText,
  Badge,
  type EvidenceBundle,
} from "@foundry/ui";
import { api } from "@/lib/api";
import { formatDate, formatRelative, shortSha } from "@/lib/format";

export default function BranchDetail() {
  const { branchId } = useParams<{ branchId: string }>();
  const navigate = useNavigate();
  const [drawerOpen, setDrawerOpen] = useState(false);

  const q = useQuery({
    queryKey: ["branch", branchId],
    queryFn: () => api.getBranch(branchId!),
    enabled: !!branchId,
  });

  if (q.isLoading) {
    return (
      <div>
        <PageHeader eyebrow="Branch" title={<Skeleton className="h-6 w-48" />} />
        <SkeletonText lines={6} />
      </div>
    );
  }
  if (q.isError || !q.data) {
    return (
      <Empty title="Branch not found" description={(q.error as Error)?.message ?? "Unknown error"} />
    );
  }

  const { branch, commits, latest_summary, pull_requests, suggested_actions } = q.data;

  return (
    <div>
      <PageHeader
        eyebrow={
          <Link to={`/repos/${branch.repository_id}`} className="hover:text-fg-secondary">
            ← Back to repository
          </Link>
        }
        title={
          <span className="inline-flex items-center gap-3">
            <span>{branch.name}</span>
            <BranchStatePill state={branch.state} />
            <ReadinessPill readiness={branch.readiness} />
          </span>
        }
        description={
          <span className="inline-flex items-center gap-3 font-mono text-xs">
            <span>{shortSha(branch.head_sha)}</span>
            <AheadBehind ahead={branch.ahead_count} behind={branch.behind_count} />
          </span>
        }
        actions={
          latest_summary ? (
            <Button variant="secondary" onClick={() => setDrawerOpen(true)}>
              View evidence
            </Button>
          ) : null
        }
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              Summary
              {latest_summary ? (
                <ConfidenceBadge value={latest_summary.confidence} />
              ) : null}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {latest_summary ? (
              <>
                <h2 className="text-base font-semibold text-fg-primary mb-2">
                  {latest_summary.headline}
                </h2>
                <p className="text-sm text-fg-secondary leading-relaxed whitespace-pre-line">
                  {latest_summary.body}
                </p>
                {latest_summary.capabilities.length > 0 ? (
                  <div className="mt-4 flex flex-wrap gap-1">
                    {latest_summary.capabilities.map((c) => (
                      <Badge
                        key={c}
                        className="bg-accent-blue/10 text-accent-blue border-accent-blue/30"
                      >
                        {c}
                      </Badge>
                    ))}
                  </div>
                ) : null}
                <div className="mt-4 text-[11px] text-fg-tertiary">
                  Generated {formatRelative(latest_summary.generated_at)} by {latest_summary.generator}.
                </div>
              </>
            ) : (
              <Empty
                title="No summary yet"
                description="Run a sync to generate the evidence-backed branch summary."
              />
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Suggested actions</CardTitle>
          </CardHeader>
          <CardContent>
            {suggested_actions.length === 0 ? (
              <Empty title="Nothing pressing." />
            ) : (
              <ul className="space-y-2 text-sm">
                {suggested_actions.map((s, i) => (
                  <li key={i} className="flex gap-2">
                    <span className="text-accent-blue">›</span>
                    <span className="text-fg-secondary">{s}</span>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Recent commits</CardTitle>
          </CardHeader>
          <CardContent>
            {commits.length === 0 ? (
              <Empty title="No commits ingested yet" />
            ) : (
              <ul className="divide-y divide-white/5">
                {commits.slice(0, 20).map((c) => (
                  <li key={c.id} className="py-2.5 flex gap-3 items-start">
                    <span className="font-mono text-xs text-fg-tertiary tabular-nums mt-0.5">
                      {shortSha(c.sha)}
                    </span>
                    <div className="min-w-0 flex-1">
                      <div className="text-sm text-fg-primary truncate">
                        {c.message.split("\n")[0]}
                      </div>
                      <div className="text-xs text-fg-tertiary mt-0.5 flex gap-2">
                        <span>{c.author_name}</span>
                        <span>·</span>
                        <span>{formatDate(c.committed_at)}</span>
                        <span>·</span>
                        <span>+{c.additions} / -{c.deletions}</span>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Pull requests</CardTitle>
          </CardHeader>
          <CardContent>
            {pull_requests.length === 0 ? (
              <Empty title="No PRs linked" />
            ) : (
              <ul className="space-y-2">
                {pull_requests.map((p) => (
                  <li key={p.id} className="text-sm">
                    <div className="flex items-center gap-2">
                      <Badge className="font-mono">#{p.number}</Badge>
                      <span className="text-fg-primary truncate">{p.title}</span>
                    </div>
                    <div className="text-xs text-fg-tertiary mt-1">{p.state}</div>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>
      </div>

      <EvidenceDrawer
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        title={branch.name}
        subtitle="Branch evidence"
        confidence={latest_summary?.confidence}
        summaryBody={latest_summary?.body}
        evidence={(latest_summary?.evidence as EvidenceBundle | null) ?? null}
      />

      <div className="mt-8">
        <Button variant="ghost" onClick={() => navigate(-1)}>
          ← Back
        </Button>
      </div>
    </div>
  );
}
