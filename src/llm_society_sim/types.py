"""Core data types for the simulation and its analysis.

Implements the state space defined in AMD-0002 §1 ("Notation and the state space").

The dependent variable is a **discrete state**, not a graded credence. See AMD-0001 §8
and OQ-0038: 7-9B models respond to counter-arguments binarily, so a credence in [0,1]
would measure probe noise rather than belief.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum

import numpy as np

__all__ = [
    "BeliefState",
    "RunTrajectory",
    "states_from_endorsements",
]


class BeliefState(IntEnum):
    """Agent belief state w.r.t. a proposition (AMD-0002 §1).

    Derived from two independent binary probes:
        b = endorses s_true
        m = endorses s_false

    s_false is *not* the logical negation of s_true -- it is a specific competing claim --
    so both are probed separately. The distinction between abandoning the truth and
    adopting the falsehood is the scientifically interesting one.
    """

    HOLDS = 0  # b=1, m=0 -- retains the truth
    DESTABILISED = 1  # b=0, m=0 -- lost the truth, has not adopted the falsehood
    CAPITULATED = 2  # b=0, m=1 -- adopted the falsehood
    INCOHERENT = 3  # b=1, m=1 -- endorses both; a data-quality signal, not a substantive state


def states_from_endorsements(b: np.ndarray, m: np.ndarray) -> np.ndarray:
    """Map (b, m) endorsement arrays to a BeliefState array.

    Args:
        b: bool/int array, agent endorses s_true.
        m: bool/int array, same shape, agent endorses s_false.

    Returns:
        int array of BeliefState values, same shape.
    """
    b = np.asarray(b).astype(bool)
    m = np.asarray(m).astype(bool)
    if b.shape != m.shape:
        raise ValueError(f"b and m must have the same shape, got {b.shape} and {m.shape}")

    out = np.empty(b.shape, dtype=np.int8)
    out[b & ~m] = BeliefState.HOLDS
    out[~b & ~m] = BeliefState.DESTABILISED
    out[~b & m] = BeliefState.CAPITULATED
    out[b & m] = BeliefState.INCOHERENT
    return out


@dataclass(frozen=True)
class RunTrajectory:
    """The complete belief trajectory of one simulation run.

    This is the analysis-facing representation. Per SOP-040 §2 the durable artefact is the
    logged raw data; this type is derived from it and analysis is a pure function of it.

    Attributes:
        run_id: Stable identifier.
        states: (N, T+1) int array of BeliefState values. Column t is round t; column 0 is
            the pre-interaction state.
        seed_agents: Indices of seeded (injected) agents. Excluded from all outcome
            denominators -- they are the intervention, not the outcome (AMD-0002 §4).
        h_cohort: Measured functional diversity H(c) of this run's cohort (AMD-0001 §5).
        a_bar: Measured mean isolated accuracy of this run's cohort (AMD-0001 §4).
        condition: Free-form label for the experimental cell.
        adjacency: Optional (N, N) adjacency for assortativity (AMD-0002 §6). adjacency[i, j]
            nonzero means i receives from j.
        failure_count: Inference failures recorded during the run (SOP-040 SS6). Runs above a
            preregistered threshold are excluded by rule.
    """

    run_id: str
    states: np.ndarray
    seed_agents: frozenset[int] = field(default_factory=frozenset)
    h_cohort: float = float("nan")
    a_bar: float = float("nan")
    condition: str = ""
    adjacency: np.ndarray | None = None
    failure_count: int = 0

    def __post_init__(self) -> None:
        if self.states.ndim != 2:
            raise ValueError(f"states must be 2-D (N, T+1), got shape {self.states.shape}")
        n, t_plus_1 = self.states.shape
        if t_plus_1 < 2:
            raise ValueError("states must contain at least an initial state and one round")
        bad = set(self.seed_agents) - set(range(n))
        if bad:
            raise ValueError(f"seed_agents out of range for N={n}: {sorted(bad)}")
        if len(self.seed_agents) >= n:
            raise ValueError("at least one non-seeded agent is required for any outcome")
        if self.adjacency is not None and self.adjacency.shape != (n, n):
            raise ValueError(
                f"adjacency must be ({n}, {n}), got {self.adjacency.shape}"
            )

    @property
    def n_agents(self) -> int:
        return self.states.shape[0]

    @property
    def n_rounds(self) -> int:
        """T -- the number of interaction rounds (states has T+1 columns)."""
        return self.states.shape[1] - 1

    @property
    def observed(self) -> np.ndarray:
        """Boolean mask over agents: True for non-seeded agents.

        Every population metric and every survival outcome is computed over these only.
        """
        mask = np.ones(self.n_agents, dtype=bool)
        if self.seed_agents:
            mask[list(self.seed_agents)] = False
        return mask
