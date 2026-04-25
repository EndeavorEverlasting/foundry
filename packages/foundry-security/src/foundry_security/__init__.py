"""foundry-security: GuardFoundry shared building blocks (v1 stub).

This package intentionally does not import anything from BranchFoundry
code. Boundary is enforced by the CI import-boundary check.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ScannerDescriptor:
    """Static description of a scanner. Concrete scanners land in Phase 3."""

    slug: str
    name: str
    description: str
    kinds: tuple[str, ...]


BUILTIN_SCANNERS: tuple[ScannerDescriptor, ...] = (
    ScannerDescriptor(
        slug="secrets",
        name="Secret scanning",
        description="Detect committed secrets across branches and history.",
        kinds=("secrets_scan",),
    ),
    ScannerDescriptor(
        slug="config-exposure",
        name="Config exposure",
        description="Find unsafe env defaults, exposed credentials, permissive CORS.",
        kinds=("config_scan",),
    ),
    ScannerDescriptor(
        slug="frontend-exposure",
        name="Frontend exposure",
        description="Identify leak patterns in browser-facing code.",
        kinds=("frontend_exposure",),
    ),
)


__all__ = ["BUILTIN_SCANNERS", "ScannerDescriptor"]
