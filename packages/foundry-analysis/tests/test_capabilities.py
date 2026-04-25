from foundry_analysis.capabilities import match_capabilities


def test_matches_simple_glob() -> None:
    matches = match_capabilities(
        files_changed=["src/features/rewards/engine.ts", "README.md"],
        features={
            "reward-engine": ["src/features/rewards/**"],
            "docs": ["**/*.md"],
        },
    )
    names = {m.feature for m in matches}
    assert names == {"reward-engine", "docs"}


def test_windows_path_normalization() -> None:
    matches = match_capabilities(
        files_changed=["src\\features\\tasks\\create.ts"],
        features={"task-creation": ["src/features/tasks/**"]},
    )
    assert matches and matches[0].feature == "task-creation"


def test_ranks_by_matched_count() -> None:
    matches = match_capabilities(
        files_changed=[
            "src/features/tasks/a.ts",
            "src/features/tasks/b.ts",
            "src/features/tasks/c.ts",
            "src/features/feedback/d.ts",
        ],
        features={
            "task-creation": ["src/features/tasks/**"],
            "feedback-system": ["src/features/feedback/**"],
        },
    )
    assert matches[0].feature == "task-creation"
    assert matches[1].feature == "feedback-system"
