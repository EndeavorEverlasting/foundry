"""foundry-analysis: drift, stale, capabilities, summary, readiness."""

from foundry_analysis.capabilities import (
    CapabilityMatch,
    match_capabilities,
)
from foundry_analysis.drift import (
    ConflictRisk,
    DriftResult,
    compute_conflict_risk,
    compute_release_readiness_score,
)
from foundry_analysis.readiness import (
    check_branch_name_policy,
    compute_readiness,
    is_safe_merge_candidate,
)
from foundry_analysis.stale import (
    StaleAssessment,
    classify_staleness,
)
from foundry_analysis.summary import (
    BranchFacts,
    SummaryResult,
    SummaryProvider,
    DeterministicSummaryProvider,
)

__all__ = [
    "BranchFacts",
    "CapabilityMatch",
    "ConflictRisk",
    "DeterministicSummaryProvider",
    "DriftResult",
    "StaleAssessment",
    "SummaryProvider",
    "SummaryResult",
    "classify_staleness",
    "compute_conflict_risk",
    "compute_readiness",
    "compute_release_readiness_score",
    "match_capabilities",
]
