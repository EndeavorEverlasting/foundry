"""Evidence model (§14 of the blueprint).

Every Summary in Foundry is backed by a tiered EvidenceBundle. The UI
derives confidence from *tier coverage*, never from a guessed number.
"""

from __future__ import annotations

from enum import IntEnum

from pydantic import BaseModel, Field


class EvidenceTier(IntEnum):
    """Blueprint §14.1 tiers."""

    GIT_DIRECT = 1
    STRUCTURAL_INFERENCE = 2
    RUNTIME_APP = 3
    MODEL_INFERENCE = 4


class Tier1Evidence(BaseModel):
    """Direct Git evidence."""

    commit_shas: list[str] = Field(default_factory=list)
    files_touched: list[str] = Field(default_factory=list)
    authors: list[str] = Field(default_factory=list)
    branches: list[str] = Field(default_factory=list)
    pr_numbers: list[int] = Field(default_factory=list)

    @property
    def has_signal(self) -> bool:
        return bool(self.commit_shas or self.files_touched)


class Tier2Evidence(BaseModel):
    """Structural inference: manifest matches, tests, ownership."""

    module_matches: list[str] = Field(default_factory=list)
    manifest_features: list[str] = Field(default_factory=list)
    tests_touched: list[str] = Field(default_factory=list)
    ownership_hints: list[str] = Field(default_factory=list)

    @property
    def has_signal(self) -> bool:
        return bool(
            self.module_matches or self.manifest_features or self.tests_touched
        )


class Tier3Evidence(BaseModel):
    """Runtime / app-emitted evidence from FoundryHooks."""

    hook_events: list[str] = Field(default_factory=list)
    domain_events: list[str] = Field(default_factory=list)
    scan_finding_ids: list[str] = Field(default_factory=list)
    runtime_metadata: dict[str, str] = Field(default_factory=dict)

    @property
    def has_signal(self) -> bool:
        return bool(self.hook_events or self.domain_events or self.scan_finding_ids)


class Tier4Evidence(BaseModel):
    """Model-inferred signals (LLM). Empty in v1."""

    model: str | None = None
    natural_language: str | None = None
    inferred_capabilities: list[str] = Field(default_factory=list)

    @property
    def has_signal(self) -> bool:
        return bool(self.natural_language or self.inferred_capabilities)


class EvidenceBundle(BaseModel):
    """Full evidence bundle for a Summary. UI renders every tier."""

    tier1: Tier1Evidence = Field(default_factory=Tier1Evidence)
    tier2: Tier2Evidence = Field(default_factory=Tier2Evidence)
    tier3: Tier3Evidence = Field(default_factory=Tier3Evidence)
    tier4: Tier4Evidence = Field(default_factory=Tier4Evidence)

    def tiers_present(self) -> list[EvidenceTier]:
        result: list[EvidenceTier] = []
        if self.tier1.has_signal:
            result.append(EvidenceTier.GIT_DIRECT)
        if self.tier2.has_signal:
            result.append(EvidenceTier.STRUCTURAL_INFERENCE)
        if self.tier3.has_signal:
            result.append(EvidenceTier.RUNTIME_APP)
        if self.tier4.has_signal:
            result.append(EvidenceTier.MODEL_INFERENCE)
        return result


def confidence_from_bundle(bundle: EvidenceBundle) -> float:
    """Derive a 0.0-1.0 confidence from tier coverage and density.

    Weights rationale: Git evidence is load-bearing; structural and runtime
    evidence meaningfully increase trust; model evidence cannot lift a
    summary above "moderate" on its own.
    """

    score = 0.0
    weights = {
        EvidenceTier.GIT_DIRECT: 0.5,
        EvidenceTier.STRUCTURAL_INFERENCE: 0.25,
        EvidenceTier.RUNTIME_APP: 0.2,
        EvidenceTier.MODEL_INFERENCE: 0.05,
    }
    for tier in bundle.tiers_present():
        score += weights[tier]

    # Density bump: many commits or many manifest features increase confidence.
    if len(bundle.tier1.commit_shas) >= 3:
        score += 0.05
    if len(bundle.tier2.manifest_features) >= 2:
        score += 0.05

    return min(1.0, round(score, 3))
