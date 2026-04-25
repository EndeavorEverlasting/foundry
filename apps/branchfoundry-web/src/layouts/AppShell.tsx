import { NavLink, Outlet, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { cn } from "@foundry/ui";
import { GitBranch, LayoutDashboard, GitPullRequestArrow, Hourglass, Target, ShieldCheck } from "lucide-react";

export default function AppShell() {
  const { repoId } = useParams();
  const { data: health } = useQuery({ queryKey: ["health"], queryFn: () => api.health() });
  const { data: repos } = useQuery({ queryKey: ["repos"], queryFn: () => api.listRepos() });
  const currentRepo = repos?.find((r) => r.id === repoId);

  return (
    <div className="min-h-screen bg-grid-fade">
      <div className="flex min-h-screen">
        <Sidebar
          repoId={repoId}
          repos={repos ?? []}
          currentRepoName={currentRepo?.name}
        />
        <main className="flex-1 min-w-0">
          <TopBar env={health?.env} version={health?.version} />
          <div className="px-6 py-6 max-w-[1400px] mx-auto">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}

function TopBar({ env, version }: { env?: string; version?: string }) {
  return (
    <div className="h-11 flex items-center gap-3 px-6 border-b border-white/5 bg-bg-base/60 backdrop-blur sticky top-0 z-20">
      <div className="text-[11px] uppercase tracking-[0.18em] text-fg-tertiary">
        BranchFoundry
      </div>
      <div className="text-[11px] text-fg-tertiary/80">v1 preview</div>
      <div className="ml-auto flex items-center gap-3 text-[11px] text-fg-tertiary">
        {env ? <span>{env}</span> : null}
        {version ? <span className="font-mono">{version}</span> : null}
      </div>
    </div>
  );
}

function Sidebar({
  repoId,
  repos,
  currentRepoName,
}: {
  repoId?: string;
  repos: Array<{ id: string; name: string; slug: string }>;
  currentRepoName?: string;
}) {
  return (
    <aside className="w-[240px] shrink-0 border-r border-white/5 bg-bg-base/70 flex flex-col min-h-screen">
      <div className="px-5 py-5 border-b border-white/5">
        <div className="flex items-center gap-2">
          <div className="h-7 w-7 rounded-md bg-accent-blue/20 border border-accent-blue/30 flex items-center justify-center">
            <GitBranch size={16} className="text-accent-blue" />
          </div>
          <div className="min-w-0">
            <div className="text-sm font-semibold text-fg-primary truncate">Foundry</div>
            <div className="text-[11px] text-fg-tertiary">BranchFoundry</div>
          </div>
        </div>
      </div>

      <nav className="px-3 py-4 space-y-1 text-sm">
        <SidebarSectionLabel>Repositories</SidebarSectionLabel>
        {repos.length === 0 ? (
          <div className="px-3 py-2 text-xs text-fg-tertiary">No repositories yet.</div>
        ) : (
          <div className="space-y-0.5">
            {repos.map((r) => (
              <NavLink
                key={r.id}
                to={`/repos/${r.id}`}
                end
                className={({ isActive }) =>
                  cn(
                    "flex items-center px-3 py-1.5 rounded-md text-fg-secondary hover:bg-white/5 hover:text-fg-primary truncate",
                    (isActive || r.id === repoId) &&
                      "bg-white/5 text-fg-primary border border-white/8",
                  )
                }
              >
                <span className="truncate">{r.name}</span>
              </NavLink>
            ))}
          </div>
        )}
        <div className="pt-2">
          <NavLink
            to="/register"
            className={({ isActive }) =>
              cn(
                "flex items-center gap-2 px-3 py-1.5 rounded-md text-fg-secondary hover:bg-white/5 hover:text-fg-primary text-xs",
                isActive && "bg-white/5 text-fg-primary",
              )
            }
          >
            <span>+ Register repository</span>
          </NavLink>
        </div>
      </nav>

      {repoId ? (
        <nav className="px-3 py-4 space-y-1 border-t border-white/5">
          <SidebarSectionLabel>
            {currentRepoName ? currentRepoName : "Views"}
          </SidebarSectionLabel>
          <SidebarLink to={`/repos/${repoId}`} end label="Dashboard" icon={<LayoutDashboard size={14} />} />
          <SidebarLink to={`/repos/${repoId}/graph`} label="Branch graph" icon={<GitBranch size={14} />} />
          <SidebarLink to={`/repos/${repoId}/drift`} label="Main drift" icon={<GitPullRequestArrow size={14} />} />
          <SidebarLink to={`/repos/${repoId}/stale`} label="Stale work" icon={<Hourglass size={14} />} />
          <SidebarLink to={`/repos/${repoId}/actions`} label="Action center" icon={<Target size={14} />} />
          <SidebarLink to={`/repos/${repoId}/release`} label="Release readiness" icon={<ShieldCheck size={14} />} />
        </nav>
      ) : null}

      <div className="mt-auto px-5 py-4 border-t border-white/5 text-[11px] text-fg-tertiary">
        Restrained premium engineering observability.
      </div>
    </aside>
  );
}

function SidebarSectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <div className="px-3 py-1 text-[10px] font-semibold uppercase tracking-wider text-fg-tertiary">
      {children}
    </div>
  );
}

function SidebarLink({
  to,
  end,
  label,
  icon,
}: {
  to: string;
  end?: boolean;
  label: string;
  icon: React.ReactNode;
}) {
  return (
    <NavLink
      to={to}
      end={end}
      className={({ isActive }) =>
        cn(
          "flex items-center gap-2 px-3 py-1.5 rounded-md text-fg-secondary hover:bg-white/5 hover:text-fg-primary",
          isActive && "bg-white/5 text-fg-primary border border-white/8",
        )
      }
    >
      {icon}
      <span>{label}</span>
    </NavLink>
  );
}
