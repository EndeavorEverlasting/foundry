"""Evidence-backed branch summaries.

v1 is deterministic: templated sentences fed from the EvidenceBundle.
No LLM required. The `SummaryProvider` protocol leaves a seam for a
future Tier-4 provider.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol

from foundry_core.evidence import (
    EvidenceBundle,
    Tier1Evidence,
    Tier2Evidence,
    Tier3Evidence,
    confidence_from_bundle,
)

from foundry_analysis.capabilities import CapabilityMatch


@dataclass
class BranchFacts:
    """All inputs needed to summarize a branch."""

    repo_name: str
    branch_name: str
    default_branch: str
    ahead: int
    behind: int
    last_commit_at: datetime | None
    last_author: str | None
    commit_shas: list[str]
    files_touched: list[str]
    authors: list[str]
    tests_touched: list[str] = field(default_factory=list)
    capability_matches: list[CapabilityMatch] = field(default_factory=list)
    hook_events: list[str] = field(default_factory=list)
    domain_events: list[str] = field(default_factory=list)


@dataclass
class SummaryResult:
    headline: str
    body: str
    confidence: float
    capabilities: list[str]
    evidence: EvidenceBundle
    generator: str = "deterministic-v1"


class SummaryProvider(Protocol):
    def summarize(self, facts: BranchFacts) -> SummaryResult: ...


class DeterministicSummaryProvider:
    """Plain-English summary composed from facts + evidence tiers 1-3."""

    def summarize(self, facts: BranchFacts) -> SummaryResult:
        evidence = _build_evidence(facts)
        confidence = confidence_from_bundle(evidence)
        caps = [m.feature for m in facts.capability_matches]
        headline = _compose_headline(facts, caps)
        body = _compose_body(facts, caps)
        return SummaryResult(
            headline=headline,
            body=body,
            confidence=confidence,
            capabilities=caps,
            evidence=evidence,
        )


def _build_evidence(facts: BranchFacts) -> EvidenceBundle:
    tier1 = Tier1Evidence(
        commit_shas=facts.commit_shas[:50],
        files_touched=facts.files_touched[:200],
        authors=sorted(set(facts.authors)),
        branches=[facts.branch_name],
    )
    tier2 = Tier2Evidence(
        module_matches=sorted(
            {path for m in facts.capability_matches for path in m.matched_files}
        )[:200],
        manifest_features=[m.feature for m in facts.capability_matches],
        tests_touched=facts.tests_touched[:50],
    )
    tier3 = Tier3Evidence(
        hook_events=facts.hook_events[:50],
        domain_events=facts.domain_events[:50],
    )
    return EvidenceBundle(tier1=tier1, tier2=tier2, tier3=tier3)


def _compose_headline(facts: BranchFacts, capabilities: list[str]) -> str:
    if capabilities:
        if len(capabilities) == 1:
            return f"{facts.branch_name} changes the {capabilities[0]} capability"
        if len(capabilities) == 2:
            a, b = capabilities
            return f"{facts.branch_name} changes {a} and {b}"
        head = ", ".join(capabilities[:2])
        return f"{facts.branch_name} changes {head} and {len(capabilities) - 2} more"

    if facts.ahead == 0 and facts.behind == 0:
        return f"{facts.branch_name} is aligned with {facts.default_branch}"
    if facts.ahead > 0 and facts.behind == 0:
        return f"{facts.branch_name} is {facts.ahead} commits ahead of {facts.default_branch}"
    if facts.ahead == 0 and facts.behind > 0:
        return f"{facts.branch_name} is {facts.behind} commits behind {facts.default_branch}"
    return (
        f"{facts.branch_name} has diverged from {facts.default_branch} "
        f"({facts.ahead} ahead, {facts.behind} behind)"
    )


def _compose_body(facts: BranchFacts, capabilities: list[str]) -> str:
    lines: list[str] = []

    if facts.ahead or facts.behind:
        lines.append(
            f"Commit drift: {facts.ahead} ahead, {facts.behind} behind "
            f"{facts.default_branch}."
        )
    else:
        lines.append(f"No drift against {facts.default_branch}.")

    if facts.last_commit_at and facts.last_author:
        lines.append(
            f"Last touched by {facts.last_author} on "
            f"{facts.last_commit_at.strftime('%Y-%m-%d')}."
        )

    if capabilities:
        human = ", ".join(capabilities)
        lines.append(f"Likely affects: {human}.")
    else:
        lines.append(
            "No manifest capabilities matched. Capability inference is unavailable; "
            "a foundry.manifest.json would improve coverage."
        )

    if facts.files_touched:
        n_files = len(facts.files_touched)
        preview = ", ".join(facts.files_touched[:3])
        suffix = f" and {n_files - 3} more" if n_files > 3 else ""
        lines.append(f"{n_files} files changed (e.g. {preview}{suffix}).")

    if facts.tests_touched:
        lines.append(f"{len(facts.tests_touched)} test file(s) touched.")

    if facts.hook_events:
        lines.append(f"{len(facts.hook_events)} runtime event(s) observed.")

    return " ".join(lines)
