import { useMutation, useQuery } from "@tanstack/react-query";
import { useParams } from "react-router-dom";
import { Badge, Button, Card, CardContent, CardHeader, CardTitle, PageHeader, Skeleton } from "@foundry/ui";
import { api } from "@/lib/api";

function badgeClassForSeverity(sev: string): string {
  if (sev === "critical" || sev === "high") return "bg-state-danger/20 border-state-danger/30 text-state-danger";
  if (sev === "medium") return "bg-state-warn/20 border-state-warn/30 text-state-warn";
  if (sev === "low") return "bg-white/5 border-white/10 text-fg-secondary";
  return "bg-state-success/20 border-state-success/30 text-state-success";
}

export default function ReleaseReadiness() {
  const { repoId } = useParams<{ repoId: string }>();

  const profileQ = useQuery({
    queryKey: ["release-profile", repoId],
    queryFn: () => api.getReleaseProfile(repoId!),
    enabled: Boolean(repoId),
  });

  const runMut = useMutation({
    mutationFn: () => api.runReleaseCheck(repoId!, {}),
  });

  const previewMut = useMutation({
    mutationFn: () => api.deployAction("preview", repoId!, { execute: false }),
  });
  const promoteMut = useMutation({
    mutationFn: () => api.deployAction("promote", repoId!, { execute: false }),
  });
  const rollbackMut = useMutation({
    mutationFn: () =>
      api.deployAction("rollback", repoId!, { execute: false, rollback_to: "HEAD~1" }),
  });

  const runQ = useQuery({
    queryKey: ["release-run", runMut.data?.id],
    queryFn: () => api.getReleaseRun(runMut.data!.id),
    enabled: Boolean(runMut.data?.id),
  });

  if (!repoId) return null;

  const run = runQ.data ?? runMut.data;
  return (
    <div>
      <PageHeader
        eyebrow="Release"
        title="Release Readiness"
        description="Centralized release contract checks (schema, env, routes, release-doc evidence)."
        actions={
          <div className="flex gap-2">
            <Button onClick={() => runMut.mutate()} disabled={runMut.isPending}>
              {runMut.isPending ? "Running..." : "Run checks"}
            </Button>
            <Button variant="secondary" onClick={() => previewMut.mutate()} disabled={previewMut.isPending}>
              Preview plan
            </Button>
            <Button variant="secondary" onClick={() => promoteMut.mutate()} disabled={promoteMut.isPending}>
              Promote plan
            </Button>
            <Button variant="secondary" onClick={() => rollbackMut.mutate()} disabled={rollbackMut.isPending}>
              Rollback plan
            </Button>
          </div>
        }
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Profile</CardTitle>
          </CardHeader>
          <CardContent>
            {profileQ.isLoading ? (
              <Skeleton className="h-20 w-full" />
            ) : profileQ.data ? (
              <div className="space-y-2 text-sm text-fg-secondary">
                <div>Enabled: {profileQ.data.enabled ? "yes" : "no"}</div>
                <div>Updated: {new Date(profileQ.data.updated_at).toLocaleString()}</div>
                <div className="font-mono text-xs break-all">
                  {JSON.stringify(profileQ.data.spec, null, 2)}
                </div>
              </div>
            ) : (
              <div className="text-sm text-fg-tertiary">No profile loaded.</div>
            )}
          </CardContent>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Latest run</CardTitle>
          </CardHeader>
          <CardContent>
            {!run ? (
              <div className="text-sm text-fg-tertiary">Run checks to generate release findings.</div>
            ) : (
              <div className="space-y-3">
                <div className="flex items-center gap-3 text-sm">
                  <Badge className={run.passed ? "bg-state-success/20 border-state-success/30 text-state-success" : "bg-state-danger/20 border-state-danger/30 text-state-danger"}>
                    {run.passed ? "PASS" : "FAIL"}
                  </Badge>
                  <span className="text-fg-tertiary">Branch: {run.branch_name}</span>
                  <span className="text-fg-tertiary">Base: {run.base_ref}</span>
                </div>
                <ul className="space-y-2">
                  {run.findings.map((f) => (
                    <li key={f.id} className="rounded-md border border-white/10 px-3 py-2">
                      <div className="flex items-center justify-between gap-3">
                        <div className="font-medium text-sm">{f.code}</div>
                        <div className="flex items-center gap-2">
                          <Badge className={badgeClassForSeverity(f.severity)}>{f.severity}</Badge>
                          <Badge className={f.passed ? "bg-state-success/20 border-state-success/30 text-state-success" : "bg-state-danger/20 border-state-danger/30 text-state-danger"}>
                            {f.passed ? "pass" : "fail"}
                          </Badge>
                        </div>
                      </div>
                      <div className="text-sm text-fg-secondary mt-1">{f.message}</div>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {(previewMut.data || promoteMut.data || rollbackMut.data) ? (
              <div className="mt-4 rounded-md border border-white/10 p-3">
                <div className="text-sm font-medium mb-2">Deploy action plan</div>
                {[previewMut.data, promoteMut.data, rollbackMut.data]
                  .filter(Boolean)
                  .map((d) => (
                    <div key={`${d!.action}-${d!.message}`} className="mb-2 text-sm text-fg-secondary">
                      <div>
                        <strong>{d!.action}</strong>: {d!.message}
                      </div>
                      <ul className="ml-5 list-disc font-mono text-xs mt-1">
                        {d!.commands.map((cmd) => (
                          <li key={cmd}>{cmd}</li>
                        ))}
                      </ul>
                    </div>
                  ))}
              </div>
            ) : null}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
