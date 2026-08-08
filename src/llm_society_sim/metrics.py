"""Outcome metrics.

Implements AMD-0002 SS2-SS4 and SS6:
  - population trajectories (TRR / MP / DS)          -- SS4
  - run-level cascade outcomes                        -- SS3
  - state assortativity (H2, restated)                -- SS6
  - effective reproduction number, descriptive only   -- SS4

Every metric excludes seeded agents from its denominator. Seeds are the intervention,
not the outcome; including them shifts every metric by sigma in every condition while
adding no information (AMD-0002 SS4).
"""

from __future__ import annotations

import numpy as np

from .types import BeliefState, RunTrajectory

__all__ = [
    "state_fractions",
    "trr",
    "mp",
    "destabilised_fraction",
    "incoherence_rate",
    "cascade_size",
    "peak_cascade_size",
    "cascade_onset",
    "peak_velocity",
    "system_capitulation",
    "irreversibility",
    "state_assortativity",
    "r_effective",
    "run_level_summary",
]


# --------------------------------------------------------------------------- SS4


def state_fractions(traj: RunTrajectory) -> dict[str, np.ndarray]:
    """Fraction of non-seeded agents in each state, per round.

    Returns a dict of (T+1,) arrays keyed by state name. The four sum to 1.0 at every
    round by construction -- reporting only TRR hides where the loss went (AMD-0002 SS4).
    """
    obs = traj.states[traj.observed]  # (N', T+1)
    n_obs = obs.shape[0]
    return {
        "trr": (obs == BeliefState.HOLDS).sum(axis=0) / n_obs,
        "mp": (obs == BeliefState.CAPITULATED).sum(axis=0) / n_obs,
        "ds": (obs == BeliefState.DESTABILISED).sum(axis=0) / n_obs,
        "incoherent": (obs == BeliefState.INCOHERENT).sum(axis=0) / n_obs,
    }


def trr(traj: RunTrajectory) -> np.ndarray:
    """Truth Retention Rate trajectory: fraction of non-seeded agents in HOLDS."""
    return state_fractions(traj)["trr"]


def mp(traj: RunTrajectory) -> np.ndarray:
    """Misinformation Prevalence trajectory: fraction of non-seeded agents CAPITULATED."""
    return state_fractions(traj)["mp"]


def destabilised_fraction(traj: RunTrajectory) -> np.ndarray:
    """Fraction of non-seeded agents DESTABILISED (lost truth, did not adopt falsehood)."""
    return state_fractions(traj)["ds"]


def incoherence_rate(traj: RunTrajectory) -> float:
    """Mean fraction of agent-rounds in the INCOHERENT state.

    A data-quality signal, not a substantive outcome. A rising incoherence rate means the
    probe is failing and must be reported rather than silently absorbed (AMD-0002 SS1).
    """
    obs = traj.states[traj.observed]
    return float((obs == BeliefState.INCOHERENT).mean())


# --------------------------------------------------------------------------- SS3


def _capitulated_counts(traj: RunTrajectory) -> np.ndarray:
    """(T+1,) count of non-seeded agents in CAPITULATED at each round."""
    obs = traj.states[traj.observed]
    return (obs == BeliefState.CAPITULATED).sum(axis=0).astype(float)


def cascade_size(traj: RunTrajectory) -> float:
    """Final cascade extent: fraction of non-seeded agents CAPITULATED at T."""
    counts = _capitulated_counts(traj)
    return float(counts[-1] / traj.observed.sum())


def peak_cascade_size(traj: RunTrajectory) -> float:
    """Maximum fraction CAPITULATED at any round -- extent before any recovery."""
    counts = _capitulated_counts(traj)
    return float(counts.max() / traj.observed.sum())


def cascade_onset(traj: RunTrajectory) -> float:
    """First round at which any non-seeded agent is CAPITULATED.

    Returns ``inf`` if the cascade never starts, which is the correct right-censoring
    value -- callers must handle censoring rather than substituting T.
    """
    counts = _capitulated_counts(traj)
    hit = np.flatnonzero(counts >= 1)
    return float(hit[0]) if hit.size else float("inf")


def peak_velocity(traj: RunTrajectory) -> float:
    """Largest single-round increase in the capitulated fraction.

    The cascade signature: a cascade is characterised by how fast it moves, not only by
    how far it gets.
    """
    counts = _capitulated_counts(traj)
    if counts.size < 2:
        return 0.0
    return float(np.diff(counts).max() / traj.observed.sum())


def system_capitulation(traj: RunTrajectory) -> bool:
    """Did a strict majority of non-seeded agents end CAPITULATED?

    The majority threshold is borrowed from a published mechanism rather than tuned by us:
    Becker et al. found error correction in multi-agent debate is majority-dependent, not
    gradual (self-correction 8.0% -> 20.5% between 2 and 3 uninformed agents).
    """
    return bool(cascade_size(traj) > 0.5)


def irreversibility(traj: RunTrajectory) -> float:
    """Of the agents that ever capitulated, the fraction still capitulated at T.

    Returns NaN when no agent ever capitulated -- the ratio is undefined, and returning
    0.0 or 1.0 there would silently fabricate a data point.
    """
    counts = _capitulated_counts(traj)
    peak = counts.max()
    if peak == 0:
        return float("nan")
    return float(counts[-1] / peak)


# --------------------------------------------------------------------------- SS6


def state_assortativity(traj: RunTrajectory, t: int = -1) -> float:
    """Newman assortativity of belief state over the edge set (AMD-0002 SS6).

    This is H2, restated. A K-S test detects distributional difference, not bimodality
    (OQ-0010); and with a *discrete* state, bimodality is meaningless -- a two-valued
    variable is trivially bimodal. The claim H2 was reaching for is **echo chambers**:
    that agents who capitulate are near each other in the graph. That is a network
    property, and this is its standard measure.

    r -> 1 means neighbours share states (belief has clustered spatially).
    r ~= 0 means state is arranged independently of structure.

    Note this is a run-level statistic, so it needs no clustering correction, and it is
    defined at N=20 where a dip test would be badly underpowered (OQ-0032).

    **Seeded agents are excluded**, and the statistic is computed on the subgraph induced
    on non-seeded agents. Seeds are pinned to CAPITULATED by construction, so including
    them would make assortativity partly a function of seed placement and seed degree --
    both of which differ systematically across topologies. Since H2 *is* the topology
    comparison, that would confound the metric with the manipulation. This is the same
    reasoning that excludes seeds from every other denominator (AMD-0002 SS4).

    Returns NaN if the induced subgraph has no edges, or if the surviving agents all share
    one state (assortativity is undefined when the attribute has no variance).
    """
    if traj.adjacency is None:
        raise ValueError("state_assortativity requires an adjacency matrix")

    keep = traj.observed
    states = traj.states[keep, t]
    sub = traj.adjacency[np.ix_(keep, keep)]
    src, dst = np.nonzero(sub)
    if src.size == 0:
        return float("nan")

    categories = np.unique(states)
    if categories.size < 2:
        return float("nan")

    # Newman's categorical assortativity: r = (sum e_ii - sum a_i b_i) / (1 - sum a_i b_i)
    index = {c: k for k, c in enumerate(categories)}
    k = categories.size
    e = np.zeros((k, k), dtype=float)
    for i, j in zip(states[src], states[dst]):
        e[index[i], index[j]] += 1.0
    e /= e.sum()

    a = e.sum(axis=1)
    b = e.sum(axis=0)
    trace = float(np.trace(e))
    ab = float(a @ b)
    if np.isclose(ab, 1.0):
        return float("nan")
    return (trace - ab) / (1.0 - ab)


def r_effective(traj: RunTrajectory) -> np.ndarray:
    """Effective reproduction number trajectory, R_eff(t) (AMD-0002 SS4).

    **Descriptive, within-topology only.** R_eff is bounded above by out-degree and is
    therefore NOT comparable across topologies -- which is exactly the comparison a reader
    will want to make, so the caveat travels with the metric. It is not a structural
    epidemiological parameter and must not be presented as one.

    Returns a (T,) array; entries are NaN where no agent was capitulated at t.
    """
    counts = _capitulated_counts(traj)
    prev = counts[:-1]
    new = np.diff(counts)
    with np.errstate(divide="ignore", invalid="ignore"):
        out = np.where(prev > 0, new / prev, np.nan)
    return out


# --------------------------------------------------------------------------- roll-up


def run_level_summary(traj: RunTrajectory) -> dict[str, float]:
    """All run-level outcomes for one run, as a flat dict.

    The unit here is the **run**, which is also the randomisation unit, so these need no
    frailty term and no clustering correction: n = number of runs (AMD-0002 SS8.1).
    """
    fractions = state_fractions(traj)
    summary: dict[str, float] = {
        "cascade_size": cascade_size(traj),
        "peak_cascade_size": peak_cascade_size(traj),
        "cascade_onset": cascade_onset(traj),
        "peak_velocity": peak_velocity(traj),
        "system_capitulation": float(system_capitulation(traj)),
        "irreversibility": irreversibility(traj),
        "trr_final": float(fractions["trr"][-1]),
        "mp_final": float(fractions["mp"][-1]),
        "ds_final": float(fractions["ds"][-1]),
        "incoherence_rate": incoherence_rate(traj),
        "convergence_delta": float(abs(fractions["mp"][-1] - fractions["mp"][-2])),
        "h_cohort": traj.h_cohort,
        "a_bar": traj.a_bar,
        "failure_count": float(traj.failure_count),
    }
    if traj.adjacency is not None:
        summary["state_assortativity"] = state_assortativity(traj)
    return summary
