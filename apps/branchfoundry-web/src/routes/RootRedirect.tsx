import { useQuery } from "@tanstack/react-query";
import { Navigate } from "react-router-dom";
import { api } from "@/lib/api";
import { Empty, Button, PageHeader } from "@foundry/ui";
import { Link } from "react-router-dom";

export default function RootRedirect() {
  const { data: repos, isLoading } = useQuery({
    queryKey: ["repos"],
    queryFn: () => api.listRepos(),
  });

  if (isLoading) return null;
  const first = repos?.[0];
  if (first) return <Navigate to={`/repos/${first.id}`} replace />;

  return (
    <div>
      <PageHeader
        eyebrow="Welcome"
        title="No repositories registered yet"
        description="Register your first repository to see branch intelligence, drift analysis, and stale-work detection."
      />
      <Empty
        title="Let's register a repository"
        description="BranchFoundry will clone or read it, build an interactive DAG, and surface evidence-backed summaries."
        action={
          <Link to="/register">
            <Button>Register repository</Button>
          </Link>
        }
      />
    </div>
  );
}
