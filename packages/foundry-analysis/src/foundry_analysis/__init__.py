"""foundry-analysis: drift, stale, capabilities, summary, readiness."""

from foundry_analysis.capabilities import (
    CapabilityMatch,
    match_capabilities,
)
from foundry_analysis.drift import (
    ConflictRisk,
    DriftResult,
    compute_conflict_risk,
)
from foundry_analysis.readiness import compute_readiness
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
    "match_capabilities",
]
