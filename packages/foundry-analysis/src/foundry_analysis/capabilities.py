"""Map touched files to manifest-declared capabilities (features)."""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass
from pathlib import PurePosixPath


@dataclass(frozen=True)
class CapabilityMatch:
    feature: str
    matched_files: list[str]
    total_feature_paths: int

    @property
    def confidence(self) -> float:
        """Coverage-based confidence: matched files vs total files changed
        contribute weight; path breadth is a tiebreaker.
        """

        # Without knowing total files, use a smoothed log-style score based on count.
        n = len(self.matched_files)
        if n == 0:
            return 0.0
        if n == 1:
            return 0.4
        if n == 2:
            return 0.6
        if n <= 4:
            return 0.75
        return 0.9


def _normalize(path: str) -> str:
    return str(PurePosixPath(path.replace("\\", "/")))


def _glob_match(path: str, pattern: str) -> bool:
    p = _normalize(path)
    pat = _normalize(pattern)
    if fnmatch.fnmatchcase(p, pat):
        return True
    if "**" not in pat:
        return False

    prefix, suffix = pat.split("**", 1)
    prefix = prefix.rstrip("/")
    suffix = suffix.lstrip("/")

    if prefix and not (p == prefix or p.startswith(prefix + "/")):
        return False

    sub = p[len(prefix) + 1 :] if prefix else p

    if not suffix:
        return True

    parts = sub.split("/")
    for i in range(len(parts)):
        candidate = "/".join(parts[i:])
        if fnmatch.fnmatchcase(candidate, suffix):
            return True
    return False


def match_capabilities(
    *,
    files_changed: list[str],
    features: dict[str, list[str]],
) -> list[CapabilityMatch]:
    """Return capability matches ranked by number of matched files."""

    out: list[CapabilityMatch] = []
    for feature_name, patterns in features.items():
        matched: list[str] = []
        for f in files_changed:
            if any(_glob_match(f, pat) for pat in patterns):
                matched.append(f)
        if matched:
            out.append(
                CapabilityMatch(
                    feature=feature_name,
                    matched_files=sorted(set(matched)),
                    total_feature_paths=len(patterns),
                )
            )
    out.sort(key=lambda m: (-len(m.matched_files), m.feature))
    return out
