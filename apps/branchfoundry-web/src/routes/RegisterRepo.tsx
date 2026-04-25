import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { Button, Card, CardContent, CardDescription, CardHeader, CardTitle, PageHeader } from "@foundry/ui";
import { api } from "@/lib/api";

export default function RegisterRepo() {
  const navigate = useNavigate();
  const qc = useQueryClient();
  const [slug, setSlug] = useState("");
  const [name, setName] = useState("");
  const [url, setUrl] = useState("");
  const [defaultBranch, setDefaultBranch] = useState("main");
  const [provider, setProvider] = useState("local");
  const [localPath, setLocalPath] = useState("");

  const mutation = useMutation({
    mutationFn: async () =>
      api.registerRepo({
        slug,
        name,
        url,
        default_branch: defaultBranch,
        provider,
        local_path: provider === "local" && localPath ? localPath : null,
      }),
    onSuccess: async (repo) => {
      await qc.invalidateQueries({ queryKey: ["repos"] });
      await api.enqueueSync(repo.id).catch(() => null);
      navigate(`/repos/${repo.id}`);
    },
  });

  return (
    <div>
      <PageHeader
        eyebrow="Setup"
        title="Register a repository"
        description="Point BranchFoundry at a repo you want to analyze. Local paths skip cloning and read in place."
      />

      <div className="grid grid-cols-1 md:grid-cols-[1fr_320px] gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Repository details</CardTitle>
            <CardDescription>
              Slug must be unique. Use a local path for a folder on disk (no clone), or a Git URL for remote repos.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form
              className="space-y-4"
              onSubmit={(e) => {
                e.preventDefault();
                mutation.mutate();
              }}
            >
              <Field label="Name">
                <input
                  className="form-input"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="AxTask"
                  required
                />
              </Field>
              <Field label="Slug">
                <input
                  className="form-input"
                  value={slug}
                  onChange={(e) => setSlug(e.target.value)}
                  placeholder="axtask"
                  required
                />
              </Field>
              <Field label="Provider">
                <select
                  className="form-input"
                  value={provider}
                  onChange={(e) => setProvider(e.target.value)}
                >
                  <option value="local">Local path</option>
                  <option value="github">GitHub</option>
                  <option value="gitlab">GitLab</option>
                  <option value="bitbucket">Bitbucket</option>
                  <option value="azure">Azure DevOps</option>
                  <option value="generic">Generic Git</option>
                </select>
              </Field>
              {provider === "local" ? (
                <Field label="Local path (inside worker container)">
                  <input
                    className="form-input font-mono text-sm"
                    value={localPath}
                    onChange={(e) => setLocalPath(e.target.value)}
                    placeholder="/workspace-mount/AxTask"
                  />
                </Field>
              ) : null}
              <Field label="Git URL">
                <input
                  className="form-input font-mono text-sm"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="https://github.com/example/repo.git"
                  required
                />
              </Field>
              <Field label="Default branch">
                <input
                  className="form-input"
                  value={defaultBranch}
                  onChange={(e) => setDefaultBranch(e.target.value)}
                  placeholder="main"
                />
              </Field>

              {mutation.isError ? (
                <p className="text-sm text-state-danger">
                  {(mutation.error as Error).message}
                </p>
              ) : null}

              <div className="flex justify-end gap-2 pt-2">
                <Button
                  type="submit"
                  disabled={mutation.isPending || !name || !slug || !url}
                >
                  {mutation.isPending ? "Registering..." : "Register + sync"}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Notes</CardTitle>
            <CardDescription>
              Registration enqueues a branch sync. Data appears as the worker finishes.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="text-sm text-fg-secondary space-y-2 list-disc pl-4">
              <li>Local paths must exist inside the worker container (mount your dev folder in compose).</li>
              <li>Secrets / private repo auth is not wired in v1. Use SSH keys on the container host or public URLs.</li>
              <li>Re-running sync is safe; ingestion is incremental.</li>
            </ul>
          </CardContent>
        </Card>
      </div>

      <style>{`
        .form-input {
          width: 100%;
          background: hsl(222 25% 10%);
          border: 1px solid hsl(222 18% 18%);
          border-radius: 6px;
          padding: 8px 10px;
          color: hsl(210 35% 96%);
          outline: none;
        }
        .form-input:focus {
          border-color: hsl(210 95% 62%);
          box-shadow: 0 0 0 2px hsl(210 95% 62% / 0.25);
        }
      `}</style>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block">
      <div className="text-xs text-fg-tertiary mb-1.5 font-medium">{label}</div>
      {children}
    </label>
  );
}
