"""Import boundary guard.

Enforces that BranchFoundry-scoped packages/apps never import from
GuardFoundry-scoped packages/apps, and vice versa. Cross-product glue
should always live behind shared packages under `packages/foundry-*`.

Runs in CI; prints violations and exits non-zero.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Packages that belong to each product. Shared infra (foundry-core,
# foundry-git, foundry-analysis, foundry-hooks-sdk, foundry-policy,
# foundry-security, foundry-ui) must stay product-agnostic.
BRANCHFOUNDRY_ROOTS = [
    "apps/branchfoundry-web",
    # BranchFoundry-specific server packages would go here.
]
GUARDFOUNDRY_ROOTS = [
    "apps/guardfoundry-web",
]

BRANCHFOUNDRY_TOKENS = [
    "branchfoundry-web",
    "@foundry/branchfoundry",
    "foundry_branchfoundry",
]
GUARDFOUNDRY_TOKENS = [
    "guardfoundry-web",
    "@foundry/guardfoundry",
    "foundry_guardfoundry",
]

EXT_OK = {".py", ".ts", ".tsx", ".js", ".jsx", ".mts", ".cts"}
IGNORE_DIRS = {"node_modules", ".venv", "dist", "build", ".turbo", ".git"}


def iter_files(roots: list[str]):
    for root in roots:
        base = ROOT / root
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            if any(part in IGNORE_DIRS for part in path.parts):
                continue
            if path.suffix in EXT_OK:
                yield path


IMPORT_PATTERNS = [
    re.compile(r"""\bimport\s+[^'"\n]+from\s+['"]([^'"]+)['"]"""),
    re.compile(r"""\brequire\(['"]([^'"]+)['"]\)"""),
    re.compile(r"""^\s*import\s+([\w\.]+)""", re.MULTILINE),
    re.compile(r"""^\s*from\s+([\w\.]+)\s+import""", re.MULTILINE),
]


def find_violations(files, forbidden_tokens: list[str]) -> list[tuple[Path, str, str]]:
    violations: list[tuple[Path, str, str]] = []
    for path in files:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for pattern in IMPORT_PATTERNS:
            for match in pattern.finditer(text):
                target = match.group(1)
                for token in forbidden_tokens:
                    if token in target:
                        violations.append((path, target, token))
    return violations


def main() -> int:
    branch_files = list(iter_files(BRANCHFOUNDRY_ROOTS))
    guard_files = list(iter_files(GUARDFOUNDRY_ROOTS))

    violations: list[tuple[str, Path, str, str]] = []
    for p, target, token in find_violations(branch_files, GUARDFOUNDRY_TOKENS):
        violations.append(("branchfoundry -> guardfoundry", p, target, token))
    for p, target, token in find_violations(guard_files, BRANCHFOUNDRY_TOKENS):
        violations.append(("guardfoundry -> branchfoundry", p, target, token))

    if not violations:
        print("import-boundaries: OK")
        return 0

    print("import-boundaries: VIOLATIONS", file=sys.stderr)
    for direction, path, target, token in violations:
        rel = path.relative_to(ROOT)
        print(f"  [{direction}] {rel}: imports {target!r} (matched {token!r})", file=sys.stderr)
    print(
        "\nCross-product imports are forbidden. Move shared logic into "
        "packages/foundry-* (core/analysis/ui/hooks-sdk/policy/security).",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
