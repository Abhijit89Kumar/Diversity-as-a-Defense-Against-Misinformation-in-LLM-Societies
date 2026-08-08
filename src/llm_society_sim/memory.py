"""Bounded context operator M_φ.

Implements SPEC-1 §2.3, with the token counter made pluggable.

The counter matters more than it looks. `tiktoken` (SPEC-2 v1.0's choice) implements OpenAI's
BPE, which is the wrong tokenizer for every model in our pool (AMD-0001, `MODEL-POOL.md`).
Counting Qwen or OLMo context with an OpenAI tokenizer would mean the "2000-token budget" is a
different amount of text for each family — and since the pool composition *is* the experimental
manipulation, that would make context length differ systematically by condition.

So: the backend supplies its own exact counter, and the heuristic below is used only when no
model is being served (stub runs, tests).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Protocol, Sequence

__all__ = ["Message", "TokenCounter", "heuristic_token_count", "BoundedMemory"]


@dataclass(frozen=True, slots=True)
class Message:
    """One broadcast message from one agent in one round."""

    sender: int
    round: int
    content: str
    stance: str | None = None  # stub-only annotation; real backends leave this None


class TokenCounter(Protocol):
    def __call__(self, text: str) -> int: ...


def heuristic_token_count(text: str) -> int:
    """Rough token count for stub runs and tests.

    ~4 characters per token is a reasonable English approximation. **Never used when a real
    model is served** — the backend's own tokenizer is, because a family-dependent counter
    would confound context length with the experimental condition.
    """
    return max(1, (len(text) + 3) // 4)


class BoundedMemory:
    """Keeps an agent's context within a token budget K.

    The system prompt is pinned; the most recent messages are retained until the budget is
    exhausted. Truncation is recorded rather than silent — how much context an agent lost is
    a covariate we may need, and under the per-edge budget convention it differs
    systematically by topology (AMD-0002 §7).
    """

    def __init__(self, token_budget: int, counter: TokenCounter | None = None) -> None:
        if token_budget <= 0:
            raise ValueError("token_budget must be positive")
        self.budget = token_budget
        self.count: TokenCounter = counter or heuristic_token_count

    def prune(
        self, system_prompt: str, history: Sequence[Message]
    ) -> tuple[list[Message], dict[str, int]]:
        """Return the retained suffix of `history`, plus truncation statistics.

        Args:
            system_prompt: Pinned; always counted against the budget.
            history: Chronological messages, oldest first.

        Returns:
            `(kept, stats)` where `kept` is a chronological sublist and `stats` records
            `dropped`, `kept`, `tokens_used` and `tokens_available`.
        """
        available = self.budget - self.count(system_prompt)
        kept: list[Message] = []
        used = 0

        if available > 0:
            for msg in reversed(history):
                cost = self.count(msg.content)
                if used + cost > available:
                    break
                kept.append(msg)
                used += cost
            kept.reverse()

        return kept, {
            "kept": len(kept),
            "dropped": len(history) - len(kept),
            "tokens_used": used,
            "tokens_available": max(0, available),
        }
