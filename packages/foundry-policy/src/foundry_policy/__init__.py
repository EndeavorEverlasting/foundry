"""foundry-policy: policy engine (v1 stub).

Policies describe rules evaluated against branches or repositories
(e.g. "no merge when findings of severity >= high exist on the branch").
The v1 engine only exposes seams; real evaluation arrives later.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass
class PolicyContext:
    repository_id: str
    branch_id: str | None = None


@dataclass
class PolicyOutcome:
    passed: bool
    detail: dict[str, str]


class PolicyEvaluator(Protocol):
    slug: str

    def evaluate(self, ctx: PolicyContext) -> PolicyOutcome: ...


class NoOpPolicyEngine:
    """Default engine: every policy passes. Replace with real engine later."""

    def __init__(self) -> None:
        self._evaluators: list[PolicyEvaluator] = []

    def register(self, evaluator: PolicyEvaluator) -> None:
        self._evaluators.append(evaluator)

    def evaluate_all(self, ctx: PolicyContext) -> list[tuple[str, PolicyOutcome]]:
        return [(e.slug, e.evaluate(ctx)) for e in self._evaluators]


__all__ = [
    "NoOpPolicyEngine",
    "PolicyContext",
    "PolicyEvaluator",
    "PolicyOutcome",
]
