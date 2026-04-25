from foundry_analysis.drift import ConflictRisk, compute_conflict_risk


def test_no_overlap_is_none() -> None:
    r = compute_conflict_risk(
        branch_files={"a.py", "b.py"},
        main_files_since_fork={"c.py", "d.py"},
    )
    assert r is ConflictRisk.NONE


def test_full_overlap_is_high() -> None:
    branch = {f"f{i}.py" for i in range(10)}
    r = compute_conflict_risk(branch_files=branch, main_files_since_fork=branch)
    assert r is ConflictRisk.HIGH


def test_partial_overlap_medium_threshold() -> None:
    r = compute_conflict_risk(
        branch_files={"a.py", "b.py", "c.py", "d.py"},
        main_files_since_fork={"a.py", "b.py", "x.py"},
    )
    assert r in (ConflictRisk.MEDIUM, ConflictRisk.HIGH)
