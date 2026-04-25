from foundry_git.service import RepoService


def test_slug_is_stable_for_same_url() -> None:
    a = RepoService.slug_for("https://github.com/example/repo.git")
    b = RepoService.slug_for("https://github.com/example/repo.git")
    assert a == b
    assert a.startswith("example-repo-")


def test_slug_differs_for_different_urls() -> None:
    a = RepoService.slug_for("https://github.com/example/repo-a.git")
    b = RepoService.slug_for("https://github.com/example/repo-b.git")
    assert a != b


def test_slug_handles_local_paths() -> None:
    slug = RepoService.slug_for("file:///C:/Users/someone/Desktop/dev/AxTask")
    assert "axtask" in slug.lower()
