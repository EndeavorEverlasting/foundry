from __future__ import annotations

import subprocess

from foundry_api.services.release_service import _detect_added_env_keys, _env_example_keys


def _git(repo: str, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)


def test_env_example_keys_missing_file_returns_empty(tmp_path) -> None:
    keys = _env_example_keys(str(tmp_path), ".env.example")
    assert keys == set()


def test_detect_added_env_keys_from_unstaged_diff(tmp_path) -> None:
    repo = str(tmp_path)
    _git(repo, "init")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")

    src = tmp_path / "app.ts"
    src.write_text("const x = 1;\n", encoding="utf-8")
    _git(repo, "add", "app.ts")
    _git(repo, "commit", "-m", "init")

    src.write_text("const x = process.env.RELEASE_TOKEN;\n", encoding="utf-8")
    keys = _detect_added_env_keys(repo, "HEAD...HEAD")
    assert "RELEASE_TOKEN" in keys
