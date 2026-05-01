from datetime import date

import pytest

from foundry_policy.branch_naming import build_branch_name, validate_branch_name


def test_build_branch_name_requires_date_and_context() -> None:
    result = build_branch_name(
        branch_type="feature",
        context="Foundry PR Cleanup Policy",
        branch_date=date(2026, 5, 1),
    )

    assert result.branch_name == "feature/2026-05-01-foundry-pr-cleanup-policy"
    assert result.branch_type == "feature"
    assert result.branch_date == "2026-05-01"
    assert result.context == "foundry-pr-cleanup-policy"
    assert validate_branch_name(result.branch_name)


@pytest.mark.parametrize(
    "branch_name",
    [
        "feature/pr-cleanup-policy",
        "work",
        "cleanup",
        "feature/2026-05-01",
        "feature/2026-5-1-context",
        "feature/2026-05-01-",
        "feature/2026-05-01_Context",
    ],
)
def test_invalid_branch_names_fail(branch_name: str) -> None:
    assert not validate_branch_name(branch_name)


def test_empty_context_is_rejected() -> None:
    with pytest.raises(ValueError, match="Branch context is required"):
        build_branch_name(
            branch_type="feature",
            context="",
            branch_date=date(2026, 5, 1),
        )


def test_invalid_branch_type_is_rejected() -> None:
    with pytest.raises(ValueError, match="Invalid branch type"):
        build_branch_name(
            branch_type="experiment",
            context="Foundry PR Cleanup Policy",
            branch_date=date(2026, 5, 1),
        )
