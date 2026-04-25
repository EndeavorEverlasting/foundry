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
} from "@foundry/ui";
import { api } from "@/lib/api";
import { formatRelative } from "@/lib/format";

export default function Stale() {
  const { repoId } = useParams<{ repoId: string }>();
  const q = useQuery({
    queryKey: ["stale", repoId],
    queryFn: () => api.stale(repoId!),
    enabled: !!repoId,
  });

  return (
    <div>
      <PageHeader
        eyebrow="Stale work"
        title="Forgotten, dormant, orphaned"
        description="Segmented by why the branch looks abandoned."
      />

      {q.isLoading ? (
        <SkeletonText lines={10} />
      ) : (q.data?.buckets.length ?? 0) === 0 ? (
        <Empty title="No stale branches" description="Everything looks active." />
      ) : (
        <div className="space-y-6">
          {q.data!.buckets.map((bucket) => (
            <Card key={bucket.label}>
              <CardHeader>
                <CardTitle>{bucket.label}</CardTitle>
                <CardDescription>{bucket.description}</CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="divide-y divide-white/5">
                  {bucket.branches.map((b) => (
                    <li key={b.id} className="py-2.5 flex items-center gap-3">
                      <div className="min-w-0 flex-1">
                        <Link
                          to={`/branches/${b.id}`}
                          className="text-sm font-medium text-fg-primary hover:text-accent-blue truncate"
                        >
                          {b.name}
                        </Link>
                        <div className="text-xs text-fg-tertiary mt-0.5">
                          Last commit {formatRelative(b.last_commit_at)} by {b.last_author ?? "unknown"}
                        </div>
                      </div>
                      <div className="flex items-center gap-2 shrink-0">
                        <BranchStatePill state={b.state} />
                        <ReadinessPill readiness={b.readiness} />
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
