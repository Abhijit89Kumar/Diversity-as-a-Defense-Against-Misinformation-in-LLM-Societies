"""Inference backends.

The engine talks to models only through :class:`Backend`. That boundary is why the entire
simulation can be built and tested with **no GPU and no API key** (`DR-0009`): the stub
backend below satisfies the same interface as a served model.

That separation was forced on us by losing compute funding, and it is better engineering than
we would have chosen with money available — it makes the released package usable with any
inference provider rather than welded to one.

Failure policy (SOP-040 §6): a failed call returns a result with `error` set and
`text=None`. **It never returns a placeholder string.** SPEC-2 v1.0 returned
`"[Agent Error: Latency drop]"`, which would have been broadcast into neighbours' contexts as
though it were a message — and since failure rates differ by provider, that corruption would
have been correlated with the experimental condition.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Protocol, Sequence

from .memory import Message, TokenCounter, heuristic_token_count

__all__ = ["Generation", "ProbeAnswer", "Backend", "StubBackend"]


@dataclass(frozen=True, slots=True)
class Generation:
    text: str | None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    finish_reason: str = "stop"
    error: str | None = None
    meta: dict[str, str] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return self.error is None and self.text is not None


@dataclass(frozen=True, slots=True)
class ProbeAnswer:
    """One probe response. `answer=None` means unparseable — recorded, never guessed."""

    answer: bool | None
    raw: str | None = None
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.error is None and self.answer is not None


class Backend(Protocol):
    """What the engine needs from a model. Implementations must be stateless across agents."""

    name: str

    def token_counter(self) -> TokenCounter:
        """The model's own tokenizer.

        Not optional: counting Qwen context with an OpenAI tokenizer would make the context
        budget a different amount of text per family, and family composition *is* the
        manipulation (see `memory.py`).
        """
        ...

    def generate(
        self, *, system: str, turn: str, history: Sequence[Message],
        max_tokens: int, temperature: float, seed: int,
    ) -> Generation: ...

    def probe(
        self, *, system: str, history: Sequence[Message], question: str, seed: int
    ) -> ProbeAnswer: ...


# --------------------------------------------------------------------------------- stub


_TRUE_RE = re.compile(r"\bTRUE\b", re.IGNORECASE)
_FALSE_RE = re.compile(r"\bFALSE\b", re.IGNORECASE)

STANCE_TRUE = "TRUE"
STANCE_FALSE = "FALSE"
STANCE_UNSURE = "UNSURE"


class StubBackend:
    """Deterministic backend for building and testing the engine without inference.

    Its purpose is to exercise the plumbing — scheduling, routing, memory bounds, probing,
    logging — end to end, and to make the engine's outputs consumable by the metrics.

    The behavioural rule is a **social-influence threshold**: an agent adopts the falsehood
    when the share of peers asserting it in its (budget-limited) incoming messages exceeds
    `threshold`, and returns to the truth when that share falls back below it. Deliberately
    simple — realistic dynamics belong in `analysis/synthetic.py`, which is what validates the
    *analysis*. Keeping the two independent means a shared bug cannot pass both.

    Stub messages carry an explicit ``[STANCE:...]`` marker so peers can read them without
    natural-language understanding. Real backends leave `Message.stance` as None and stance is
    inferred by probing, exactly as it will be in the real experiment.
    """

    name = "stub"

    def __init__(
        self,
        *,
        s_false: str,
        threshold: float = 0.5,
        base_accuracy: float = 0.7,
        stubbornness: float = 0.0,
        counter: TokenCounter | None = None,
    ) -> None:
        """
        Args:
            s_false: The injected claim for this run. The stub needs it to tell which of the
                two claims a probe is asking about. A real model reads the claim out of the
                question text, so this is stub-only state and is deliberately kept here
                rather than added as a parameter to :class:`Backend` that real backends
                would have to ignore.
        """
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("threshold must be in [0, 1]")
        if not 0.0 <= base_accuracy <= 1.0:
            raise ValueError("base_accuracy must be in [0, 1]")
        self.s_false = s_false
        self.threshold = threshold
        self.base_accuracy = base_accuracy
        self.stubbornness = stubbornness
        self._counter = counter or heuristic_token_count

    # -- deterministic pseudo-randomness -------------------------------------------------

    @staticmethod
    def _unit(*parts: object) -> float:
        """A stable float in [0, 1) from the given parts. No RNG state, so fully replayable."""
        key = "\x1f".join(str(p) for p in parts).encode("utf-8")
        return int.from_bytes(hashlib.sha256(key).digest()[:8], "big") / 2**64

    # -- belief model --------------------------------------------------------------------

    def _belief(
        self, system: str, history: Sequence[Message], seed: int
    ) -> tuple[bool, bool]:
        """Return `(endorses_true, endorses_false)` — the 2x2 state of AMD-0002 §1.

        The two are tracked **separately and are not complements**, which is the whole point
        of probing both claims. An agent that simply does not know the fact endorses neither:
        it is DESTABILISED, not CAPITULATED. Only peer pressure produces endorsement of the
        specific injected falsehood.

        Getting this wrong collapses DESTABILISED to zero and empties the truth-acquisition
        risk set, making a primary metric unestimable (AMD-0002 §2.3). The first end-to-end
        smoke test caught exactly that.
        """
        if "try to persuade the other participants" in system:
            return False, True  # seeded: pinned to the injected claim

        peers = [m.stance for m in history if m.stance in (STANCE_TRUE, STANCE_FALSE)]
        knows_it = self._unit("prior", seed, system) < self.base_accuracy

        if not peers:
            # No exposure yet. Either the agent knows the fact, or it holds no position on
            # either claim -- it has never encountered the falsehood.
            return knows_it, False

        share_false = sum(s == STANCE_FALSE for s in peers) / len(peers)
        share_true = sum(s == STANCE_TRUE for s in peers) / len(peers)
        cut = self.threshold + self.stubbornness

        if share_false > cut:
            return False, True  # capitulated
        if share_true > cut:
            return True, False  # holds, or acquired the truth from peers
        # Contested neighbourhood: the agent falls back on what it knows, and endorses the
        # falsehood only if peers pushed it there, which they have not.
        return knows_it, False

    # -- interface -----------------------------------------------------------------------

    def token_counter(self) -> TokenCounter:
        return self._counter

    def generate(
        self, *, system: str, turn: str, history: Sequence[Message],
        max_tokens: int, temperature: float, seed: int,
    ) -> Generation:
        endorses_true, endorses_false = self._belief(system, history, seed)
        if endorses_false:
            stance = STANCE_FALSE
        elif endorses_true:
            stance = STANCE_TRUE
        else:
            stance = STANCE_UNSURE

        text = f"[STANCE:{stance}] Considering the discussion so far, my position is {stance}."
        return Generation(
            text=text,
            prompt_tokens=self._counter(system) + self._counter(turn)
            + sum(self._counter(m.content) for m in history),
            completion_tokens=self._counter(text),
            meta={"stance": stance},
        )

    def probe(
        self, *, system: str, history: Sequence[Message], question: str, seed: int
    ) -> ProbeAnswer:
        """Answer a TRUE/FALSE probe about whichever claim the question names.

        The engine probes the true and the false claim in separate calls, so this must answer
        about the claim in the question rather than echoing a single stance.
        """
        endorses_true, endorses_false = self._belief(system, history, seed)
        answer = endorses_false if self.s_false in question else endorses_true
        return ProbeAnswer(answer=answer, raw="TRUE" if answer else "FALSE")


def parse_true_false(text: str) -> bool | None:
    """Parse a TRUE/FALSE probe response.

    Returns None when the response contains both or neither. **Unparseable is recorded as
    unparseable** — never coerced to a default, which would silently manufacture belief states
    and bias the very outcome under study.
    """
    if text is None:
        return None
    has_true = bool(_TRUE_RE.search(text))
    has_false = bool(_FALSE_RE.search(text))
    if has_true == has_false:
        return None
    return has_true
