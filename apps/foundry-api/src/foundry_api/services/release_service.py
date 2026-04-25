"""Release readiness policy engine (repo-local git checks)."""

from __future__ import annotations

import os
import re
import subprocess
from fnmatch import fnmatch
from datetime import datetime, timezone

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from foundry_core.enums import FindingSeverity
from foundry_core.models import (
    HookManifest,
    ReleaseFinding,
    ReleaseProfile,
    ReleaseRun,
    Repository,
)
from foundry_core.schemas import (
    ManifestIn,
    ReleaseCheckRequest,
    ReleaseDeployRequest,
    ReleaseDeployResult,
    ReleaseRunOut,
)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _run_git(repo_path: str, args: list[str], allow_fail: bool = False) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=repo_path,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if proc.returncode != 0 and not allow_fail:
        stderr = (proc.stderr or proc.stdout or "").strip()
        raise RuntimeError(stderr or f"git {' '.join(args)} failed")
    return (proc.stdout or "").strip()


def _to_files(text: str) -> set[str]:
    return {line.strip() for line in text.splitlines() if line.strip()}


def _matches(path: str, regex_value: object, glob_values: object) -> bool:
    if isinstance(glob_values, list) and glob_values:
        return any(isinstance(g, str) and fnmatch(path, g) for g in glob_values)
    if isinstance(regex_value, str) and regex_value:
        return bool(re.compile(regex_value).match(path))
    return False


def _detect_added_env_keys(repo_path: str, range_expr: str) -> set[str]:
    committed = _run_git(repo_path, ["diff", "--unified=0", range_expr], allow_fail=True)
    staged = _run_git(repo_path, ["diff", "--unified=0", "--cached"], allow_fail=True)
    unstaged = _run_git(repo_path, ["diff", "--unified=0"], allow_fail=True)
    keys: set[str] = set()
    for line in f"{committed}\n{staged}\n{unstaged}".splitlines():
        if not line.startswith("+") or line.startswith("+++"):
            continue
        for hit in re.findall(r"process\.env\.([A-Z][A-Z0-9_]+)", line):
            keys.add(hit)
    return keys


def _env_example_keys(repo_path: str, env_file: str) -> set[str]:
    env_path = os.path.join(repo_path, env_file)
    if not os.path.exists(env_path):
        return set()
    try:
        with open(env_path, encoding="utf-8") as f:
            src = f.read()
    except OSError:
        return set()
    keys: set[str] = set()
    for line in src.splitlines():
        m = re.match(r"^\s*#?\s*([A-Z][A-Z0-9_]*)\s*=", line)
        if m:
            keys.add(m.group(1))
    return keys


async def _get_or_create_profile(session: AsyncSession, repo_id: str) -> ReleaseProfile:
    existing = await session.execute(
        select(ReleaseProfile).where(ReleaseProfile.repository_id == repo_id)
    )
    profile = existing.scalar_one_or_none()
    if profile is not None:
        return profile
    default_spec: dict[str, object] = {
        "schema_glob": r"^shared/schema/.+\.ts$",
        "migration_glob": r"^migrations/\d+_.+\.sql$",
        "routes_glob": r"^server/(routes|shopping-lists-routes)\.ts$",
        "route_inventory_file": "server/routes-inventory.contract.test.ts",
        "env_example_file": ".env.example",
        "release_doc_glob": r"^docs/releases/.+\.md$",
    }
    manifest_q = await session.execute(
        select(HookManifest)
        .where(HookManifest.repository_id == repo_id)
        .order_by(HookManifest.created_at.desc())
    )
    manifest_row = manifest_q.scalar_one_or_none()
    if manifest_row and manifest_row.raw:
        try:
            manifest = ManifestIn.model_validate(manifest_row.raw)
            if manifest.release is not None:
                if manifest.release.route_inventory_file:
                    default_spec["route_inventory_file"] = manifest.release.route_inventory_file
                if manifest.release.env_template_file:
                    default_spec["env_example_file"] = manifest.release.env_template_file
                if manifest.release.schema_globs:
                    default_spec["schema_globs"] = manifest.release.schema_globs
                if manifest.release.migration_globs:
                    default_spec["migration_globs"] = manifest.release.migration_globs
                if manifest.release.release_doc_globs:
                    default_spec["release_doc_globs"] = manifest.release.release_doc_globs
        except Exception:
            # Keep baseline defaults if the manifest payload is partial/invalid.
            pass

    profile = ReleaseProfile(
        repository_id=repo_id,
        enabled=True,
        spec=default_spec,
    )
    session.add(profile)
    await session.flush()
    return profile


async def run_release_check(
    session: AsyncSession, repo: Repository, payload: ReleaseCheckRequest
) -> ReleaseRunOut:
    if not repo.local_path:
        raise ValueError("repository.local_path is required to run release checks")
    if not os.path.isdir(repo.local_path):
        raise ValueError("repository.local_path does not exist on disk")

    profile = await _get_or_create_profile(session, repo.id)
    spec = profile.spec or {}
    branch_name = payload.branch_name or _run_git(repo.local_path, ["branch", "--show-current"])
    base_ref = payload.base_ref or "origin/main"

    merge_base = _run_git(
        repo.local_path, ["merge-base", base_ref, "HEAD"], allow_fail=True
    )
    range_expr = f"{merge_base}...HEAD" if merge_base else f"{base_ref}...HEAD"

    committed = _run_git(repo.local_path, ["diff", "--name-only", range_expr], allow_fail=True)
    staged = _run_git(repo.local_path, ["diff", "--name-only", "--cached"], allow_fail=True)
    unstaged = _run_git(repo.local_path, ["diff", "--name-only"], allow_fail=True)
    untracked = _run_git(
        repo.local_path, ["ls-files", "--others", "--exclude-standard"], allow_fail=True
    )
    changed = _to_files(f"{committed}\n{staged}\n{unstaged}\n{untracked}")

    findings: list[ReleaseFinding] = []

    def add_finding(
        code: str,
        passed: bool,
        message: str,
        severity: FindingSeverity,
        evidence: dict[str, object] | None = None,
    ) -> None:
        findings.append(
            ReleaseFinding(
                code=code,
                passed=passed,
                severity=severity,
                message=message,
                evidence=evidence or {},
            )
        )

    schema_regex = spec.get("schema_glob", r"^shared/schema/.+\.ts$")
    migration_regex = spec.get("migration_glob", r"^migrations/\d+_.+\.sql$")
    routes_regex = spec.get("routes_glob", r"^server/(routes|shopping-lists-routes)\.ts$")
    release_doc_regex = spec.get("release_doc_glob", r"^docs/releases/.+\.md$")
    schema_globs = spec.get("schema_globs")
    migration_globs = spec.get("migration_globs")
    release_doc_globs = spec.get("release_doc_globs")
    route_inventory_file = str(
        spec.get("route_inventory_file", "server/routes-inventory.contract.test.ts")
    )
    env_example_file = str(spec.get("env_example_file", ".env.example"))

    schema_touched = sorted(
        f for f in changed if _matches(f, schema_regex, schema_globs)
    )
    migrations_touched = sorted(
        f for f in changed if _matches(f, migration_regex, migration_globs)
    )
    add_finding(
        code="schema_migration_evidence",
        passed=not schema_touched or bool(migrations_touched),
        severity=FindingSeverity.HIGH,
        message=(
            "Schema changes include numbered SQL migration evidence."
            if (not schema_touched or migrations_touched)
            else "Schema changed but no numbered SQL migration was detected."
        ),
        evidence={"schema_files": schema_touched, "migration_files": migrations_touched},
    )

    routes_touched = sorted(f for f in changed if _matches(f, routes_regex, None))
    route_inventory_changed = route_inventory_file in changed
    add_finding(
        code="route_inventory_evidence",
        passed=not routes_touched or route_inventory_changed,
        severity=FindingSeverity.MEDIUM,
        message=(
            "Route inventory evidence present."
            if (not routes_touched or route_inventory_changed)
            else "Routes changed but route inventory contract file was not touched."
        ),
        evidence={"route_files": routes_touched, "inventory_file": route_inventory_file},
    )

    added_env_keys = sorted(_detect_added_env_keys(repo.local_path, range_expr))
    env_keys = _env_example_keys(repo.local_path, env_example_file)
    missing_env = sorted(k for k in added_env_keys if k not in env_keys)
    add_finding(
        code="env_template_evidence",
        passed=not missing_env,
        severity=FindingSeverity.MEDIUM,
        message=(
            "Environment template covers new process.env keys."
            if not missing_env
            else "New process.env keys are missing from env template."
        ),
        evidence={
            "env_example_file": env_example_file,
            "added_env_keys": added_env_keys,
            "missing_env_keys": missing_env,
        },
    )

    release_docs = sorted(
        f for f in changed if _matches(f, release_doc_regex, release_doc_globs)
    )
    require_release_doc = branch_name not in {"main", "master"}
    add_finding(
        code="release_doc_evidence",
        passed=(not require_release_doc) or bool(release_docs),
        severity=FindingSeverity.LOW,
        message=(
            "Release documentation evidence present."
            if ((not require_release_doc) or release_docs)
            else "No docs/releases/*.md change detected for this feature branch."
        ),
        evidence={"branch_name": branch_name, "release_docs": release_docs},
    )

    passed = all(f.passed for f in findings)
    run = ReleaseRun(
        repository_id=repo.id,
        branch_name=branch_name,
        base_ref=base_ref,
        range_expr=range_expr,
        passed=passed,
        summary={
            "changed_files_count": len(changed),
            "failing_count": sum(1 for f in findings if not f.passed),
        },
    )
    session.add(run)
    await session.flush()

    for f in findings:
        f.release_run_id = run.id
        session.add(f)

    await session.flush()
    return await get_release_run(session, run.id)


async def get_release_run(session: AsyncSession, run_id: str) -> ReleaseRunOut:
    run_q = await session.execute(select(ReleaseRun).where(ReleaseRun.id == run_id))
    run = run_q.scalar_one_or_none()
    if run is None:
        raise ValueError("release run not found")
    findings_q = await session.execute(
        select(ReleaseFinding)
        .where(ReleaseFinding.release_run_id == run.id)
        .order_by(ReleaseFinding.created_at.asc())
    )
    findings = findings_q.scalars().all()
    return ReleaseRunOut(
        id=run.id,
        repository_id=run.repository_id,
        branch_name=run.branch_name,
        base_ref=run.base_ref,
        range_expr=run.range_expr,
        passed=run.passed,
        summary=run.summary,
        created_at=run.created_at,
        findings=[f for f in findings],
    )


async def get_release_profile(session: AsyncSession, repo_id: str) -> ReleaseProfile:
    return await _get_or_create_profile(session, repo_id)


async def update_release_profile(
    session: AsyncSession, repo_id: str, enabled: bool, spec: dict[str, object]
) -> ReleaseProfile:
    profile = await _get_or_create_profile(session, repo_id)
    profile.enabled = enabled
    profile.spec = spec
    profile.updated_at = _utcnow()
    session.add(profile)
    await session.flush()
    return profile


async def clear_release_runs_for_repo(session: AsyncSession, repo_id: str) -> None:
    """Utility for tests and cleanup."""
    run_ids_q = await session.execute(select(ReleaseRun.id).where(ReleaseRun.repository_id == repo_id))
    run_ids = [row[0] for row in run_ids_q.all()]
    if run_ids:
        await session.execute(delete(ReleaseFinding).where(ReleaseFinding.release_run_id.in_(run_ids)))
    await session.execute(delete(ReleaseRun).where(ReleaseRun.repository_id == repo_id))


def _run_local(cmd: list[str], cwd: str, execute: bool) -> tuple[bool, str]:
    shell_cmd = " ".join(cmd)
    if not execute:
        return True, f"[dry-run] {shell_cmd}"
    proc = subprocess.run(
        cmd, cwd=cwd, check=False, capture_output=True, text=True, encoding="utf-8"
    )
    if proc.returncode == 0:
        return True, (proc.stdout or "").strip() or f"ok: {shell_cmd}"
    return False, (proc.stderr or proc.stdout or f"failed: {shell_cmd}").strip()


async def run_deploy_action(
    session: AsyncSession,
    repo: Repository,
    action: str,
    payload: ReleaseDeployRequest,
) -> ReleaseDeployResult:
    if not repo.local_path:
        raise ValueError("repository.local_path is required for deploy actions")
    if not os.path.isdir(repo.local_path):
        raise ValueError("repository.local_path does not exist on disk")

    current_branch = _run_git(repo.local_path, ["branch", "--show-current"])
    commands: list[list[str]]
    target_ref = payload.target_ref

    if action == "preview":
        target = target_ref or current_branch
        commands = [
            ["git", "fetch", "origin", target],
            ["git", "checkout", target],
        ]
    elif action == "promote":
        target = target_ref or "main"
        commands = [
            ["git", "fetch", "origin", target],
            ["git", "checkout", target],
            ["git", "merge", "--ff-only", current_branch],
        ]
    elif action == "rollback":
        rollback_to = payload.rollback_to or ""
        if not rollback_to:
            raise ValueError("rollback_to is required for rollback action")
        target = target_ref or "main"
        commands = [
            ["git", "fetch", "origin", target],
            ["git", "checkout", target],
            ["git", "revert", "--no-edit", rollback_to],
        ]
    else:
        raise ValueError("unknown deploy action")

    outputs: list[str] = []
    for cmd in commands:
        ok, out = _run_local(cmd, repo.local_path, payload.execute)
        outputs.append(out)
        if not ok:
            return ReleaseDeployResult(
                action=action,
                executed=payload.execute,
                success=False,
                message=out,
                commands=[" ".join(c) for c in commands],
            )

    return ReleaseDeployResult(
        action=action,
        executed=payload.execute,
        success=True,
        message="Deploy action completed." if payload.execute else "Deploy action planned (dry-run).",
        commands=[" ".join(c) for c in commands],
    )
