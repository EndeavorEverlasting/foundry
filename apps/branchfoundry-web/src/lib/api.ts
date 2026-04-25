import type {
  ActionCenter,
  Branch,
  BranchDetail,
  DriftPanel,
  GraphResponse,
  Manifest,
  ReleaseProfile,
  ReleaseDeployResult,
  ReleaseRun,
  Repository,
  RepoSummary,
  StaleView,
} from "@foundry/ui";

const API_BASE = (import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000").replace(/\/$/, "");

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
      ...(init?.headers ?? {}),
    },
    ...init,
  });
  if (!res.ok) {
    let detail: unknown = res.statusText;
    try {
      detail = await res.json();
    } catch {
      // fall through
    }
    throw new ApiError(res.status, typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export class ApiError extends Error {
  readonly status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
    this.name = "ApiError";
  }
}

export const api = {
  health: () => request<{ status: string; env: string; version: string }>("/health"),

  listRepos: () => request<Repository[]>("/api/v1/repos"),
  getRepo: (id: string) => request<Repository>(`/api/v1/repos/${id}`),
  repoSummary: (id: string) => request<RepoSummary>(`/api/v1/repos/${id}/summary`),
  registerRepo: (body: {
    slug: string;
    name: string;
    url: string;
    default_branch?: string;
    provider?: string;
    local_path?: string | null;
  }) =>
    request<Repository>("/api/v1/repos", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  enqueueSync: (id: string) =>
    request<{ job_id: string; enqueued_at: string }>(`/api/v1/repos/${id}/sync`, {
      method: "POST",
    }),

  listBranches: (
    repoId: string,
    params?: { state?: string; stale_only?: boolean; author?: string; limit?: number },
  ) => {
    const search = new URLSearchParams();
    if (params?.state) search.set("state", params.state);
    if (params?.stale_only) search.set("stale_only", "true");
    if (params?.author) search.set("author", params.author);
    if (params?.limit) search.set("limit", String(params.limit));
    const qs = search.toString();
    return request<Branch[]>(`/api/v1/repos/${repoId}/branches${qs ? `?${qs}` : ""}`);
  },
  getBranch: (id: string) => request<BranchDetail>(`/api/v1/branches/${id}`),

  graph: (repoId: string) => request<GraphResponse>(`/api/v1/repos/${repoId}/graph`),
  stale: (repoId: string) => request<StaleView>(`/api/v1/repos/${repoId}/stale`),
  actions: (repoId: string) => request<ActionCenter>(`/api/v1/repos/${repoId}/actions`),
  drift: (repoId: string) => request<DriftPanel>(`/api/v1/repos/${repoId}/drift`),

  getManifest: (repoId: string) => request<Manifest>(`/api/v1/repos/${repoId}/manifest`),
  upsertManifest: (repoId: string, body: unknown) =>
    request<Manifest>(`/api/v1/repos/${repoId}/manifest`, {
      method: "POST",
      body: JSON.stringify(body),
    }),

  getReleaseProfile: (repoId: string) =>
    request<ReleaseProfile>(`/api/v1/release/profiles/${repoId}`),
  runReleaseCheck: (repoId: string, body?: { branch_name?: string; base_ref?: string }) =>
    request<ReleaseRun>(`/api/v1/release/check/${repoId}`, {
      method: "POST",
      body: JSON.stringify(body ?? {}),
    }),
  getReleaseRun: (runId: string) => request<ReleaseRun>(`/api/v1/release/runs/${runId}`),
  deployAction: (
    action: "preview" | "promote" | "rollback",
    repoId: string,
    body?: { execute?: boolean; base_ref?: string; target_ref?: string; rollback_to?: string },
  ) =>
    request<ReleaseDeployResult>(`/api/v1/release/deploy/${action}/${repoId}`, {
      method: "POST",
      body: JSON.stringify(body ?? {}),
    }),
};
