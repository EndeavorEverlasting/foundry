from datetime import datetime, timezone

from foundry_analysis.capabilities import CapabilityMatch
from foundry_analysis.summary import BranchFacts, DeterministicSummaryProvider


def test_summary_headline_when_capabilities_present() -> None:
    facts = BranchFacts(
        repo_name="AxTask",
        branch_name="feat/rewards-revamp",
        default_branch="main",
        ahead=3,
        behind=0,
        last_commit_at=datetime(2026, 4, 18, tzinfo=timezone.utc),
        last_author="Richard",
        commit_shas=["abc123", "def456", "ghi789"],
        files_touched=["src/features/rewards/engine.ts"],
        authors=["Richard"],
        capability_matches=[
            CapabilityMatch(
                feature="reward-engine",
                matched_files=["src/features/rewards/engine.ts"],
                total_feature_paths=1,
            )
        ],
    )
    result = DeterministicSummaryProvider().summarize(facts)
    assert "reward-engine" in result.headline
    assert result.confidence > 0
    assert "reward-engine" in result.capabilities


def test_summary_headline_when_aligned() -> None:
    facts = BranchFacts(
        repo_name="AxTask",
        branch_name="spike/xyz",
        default_branch="main",
        ahead=0,
        behind=0,
        last_commit_at=None,
        last_author=None,
        commit_shas=[],
        files_touched=[],
        authors=[],
    )
    result = DeterministicSummaryProvider().summarize(facts)
    assert "aligned" in result.headline.lower()
