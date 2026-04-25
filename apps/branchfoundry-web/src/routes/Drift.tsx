import { Link, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import {
  AheadBehind,
  BranchStatePill,
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  Empty,
  PageHeader,
  ReadinessPill,
  SkeletonText,
  cn,
  type DriftEntry,
} from "@foundry/ui";
import { api } from "@/lib/api";

export default function Drift() {
  const { repoId } = useParams<{ repoId: string }>();
  const q = useQuery({
    queryKey: ["drift", repoId],
    queryFn: () => api.drift(repoId!),
    enabled: !!repoId,
  });

  return (
    <div>
      <PageHeader
        eyebrow="Main drift"
        title="Where main is drifting"
        description="What main is missing, and which branches need to catch up."
      />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Main is missing</CardTitle>
          </CardHeader>
          <CardContent>
            {q.isLoading ? (
              <SkeletonText lines={6} />
            ) : (q.data?.main_missing.length ?? 0) === 0 ? (
              <Empty title="Main is up to date" description="No branches are ahead of main." />
            ) : (
              <ul className="divide-y divide-white/5">
                {q.data!.main_missing.map((e) => (
                  <DriftRow key={e.branch.id} entry={e} direction="ahead" />
                ))}
              </ul>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Behind main</CardTitle>
          </CardHeader>
          <CardContent>
            {q.isLoading ? (
              <SkeletonText lines={6} />
            ) : (q.data?.behind_main.length ?? 0) === 0 ? (
              <Empty title="All branches are caught up." />
            ) : (
              <ul className="divide-y divide-white/5">
                {q.data!.behind_main.map((e) => (
                  <DriftRow key={e.branch.id} entry={e} direction="behind" />
                ))}
              </ul>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function DriftRow({ entry, direction }: { entry: DriftEntry; direction: "ahead" | "behind" }) {
  const riskClass: Record<DriftEntry["conflict_risk"], string> = {
    none: "text-fg-tertiary",
    low: "text-state-success",
    medium: "text-state-warn",
    high: "text-state-danger",
  };
  return (
    <li className="py-2.5 flex items-center gap-3">
      <div className="min-w-0 flex-1">
        <Link
          to={`/branches/${entry.branch.id}`}
          className="text-sm font-medium text-fg-primary hover:text-accent-blue truncate"
        >
          {entry.branch.name}
        </Link>
        <div className="flex items-center gap-2 text-xs text-fg-tertiary mt-0.5">
          <AheadBehind ahead={entry.ahead} behind={entry.behind} />
          <span className="mx-1">·</span>
          <span className={cn("uppercase tracking-wider text-[10px]", riskClass[entry.conflict_risk])}>
            {entry.conflict_risk} conflict risk
          </span>
          <span className="mx-1">·</span>
          <span>{direction === "ahead" ? `${entry.ahead} ahead of main` : `${entry.behind} behind main`}</span>
        </div>
      </div>
      <div className="flex items-center gap-2 shrink-0">
        <BranchStatePill state={entry.branch.state} />
        <ReadinessPill readiness={entry.readiness} />
      </div>
    </li>
  );
}
