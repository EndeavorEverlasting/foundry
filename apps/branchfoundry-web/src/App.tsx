import { Navigate, Route, Routes } from "react-router-dom";
import AppShell from "./layouts/AppShell";
import RootRedirect from "./routes/RootRedirect";
import RepoLayout from "./routes/RepoLayout";
import Dashboard from "./routes/Dashboard";
import Graph from "./routes/Graph";
import BranchDetail from "./routes/BranchDetail";
import Drift from "./routes/Drift";
import Stale from "./routes/Stale";
import Actions from "./routes/Actions";
import ReleaseReadiness from "./routes/ReleaseReadiness";
import RegisterRepo from "./routes/RegisterRepo";
import NotFound from "./routes/NotFound";

export default function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route index element={<RootRedirect />} />
        <Route path="register" element={<RegisterRepo />} />
        <Route path="repos/:repoId" element={<RepoLayout />}>
          <Route index element={<Dashboard />} />
          <Route path="graph" element={<Graph />} />
          <Route path="drift" element={<Drift />} />
          <Route path="stale" element={<Stale />} />
          <Route path="actions" element={<Actions />} />
          <Route path="release" element={<ReleaseReadiness />} />
        </Route>
        <Route path="branches/:branchId" element={<BranchDetail />} />
        <Route path="404" element={<NotFound />} />
        <Route path="*" element={<Navigate to="/404" replace />} />
      </Route>
    </Routes>
  );
}
