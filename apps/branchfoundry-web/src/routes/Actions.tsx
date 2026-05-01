import { Link, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import {
  BranchStatePill,
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Empty,
  PageHeader,
  ReadinessPill,
  SkeletonText,
  type ActionKind,
} from "@foundry/ui";
import { api } from "@/lib/api";

const KIND_LABELS: Record<ActionKind, { label: string; description: string }> = {
  ready_to_merge: { label: "Ready to merge", description: "Up to date and looks good to ship." },
  needs_review: { label: "Needs review", description: "Open PRs without reviewers attached." },
  needs_rebase: { label: "Needs rebase", description: "Branches behind the default." },
  at_risk: { label: "At risk", description: "Stale or orphaned branches with real work." },
  failing_checks: { label: "Failing checks", description: "CI is red on the PR." },
  branch_policy_violation: { label: "Policy violation", description: "Branch name does not follow naming conventions." },
  manual_review: { label: "Manual review", description: "High-risk changes require human review before merge." },
};

const ORDER: ActionKind[] = [
  "ready_to_merge",
  "needs_review",
  "needs_rebase",
  "failing_checks",
  "at_risk",
  "branch_policy_violation",
  "manual_review",
];

export default function Actions() {
  const { repoId } = useParams<{ repoId: string }>();
  const q = useQuery({
    queryKey: ["actions", repoId],
    queryFn: () => api.actions(repoId!),
    enabled: !!repoId,
  });

  const byKind = q.data?.by_kind ?? {};
  const hasAny = Object.values(byKind).some((v) => (v?.length ?? 0) > 0);

  return (
    <div>
      <PageHeader
        eyebrow="Action center"
        title="Things to act on"
        description="Every card cites the branch it's about. Click through for full evidence."
      />

      {q.isLoading ? (
        <SkeletonText lines={10} />
      ) : !hasAny ? (
        <Empty title="All clear" description="No active items." />
      ) : (
        <div className="space-y-6">
          {ORDER.filter((k) => (byKind[k]?.length ?? 0) > 0).map((kind) => (
            <Card key={kind}>
              <CardHeader>
                <CardTitle>{KIND_LABELS[kind].label}</CardTitle>
                <CardDescription>{KIND_LABELS[kind].description}</CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="divide-y divide-white/5">
                  {(byKind[kind] ?? []).map((a) => (
                    <li key={a.branch.id} className="py-2.5 flex items-center gap-3">
                      <div className="min-w-0 flex-1">
                        <Link
                          to={`/branches/${a.branch.id}`}
                          className="text-sm font-medium text-fg-primary hover:text-accent-blue truncate"
                        >
                          {a.branch.name}
                        </Link>
                        <div className="text-xs text-fg-tertiary mt-0.5">{a.reason}</div>
                      </div>
                      <div className="flex items-center gap-2 shrink-0">
                        <BranchStatePill state={a.branch.state} />
                        <ReadinessPill readiness={a.branch.readiness} />
                      </div>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
