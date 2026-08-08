"""Unit tests for outcome metrics on hand-constructed trajectories with known answers.

Required by SOP-040 SS3: anything that produces a number in the paper is tested. These are
deliberately hand-built rather than generated, so the expected value is obvious by
inspection and a reader can verify the test itself.
"""

from __future__ import annotations

import numpy as np
import pytest

from llm_society_sim import metrics
from llm_society_sim.types import BeliefState, RunTrajectory, states_from_endorsements

H, D, C, I = (
    BeliefState.HOLDS,
    BeliefState.DESTABILISED,
    BeliefState.CAPITULATED,
    BeliefState.INCOHERENT,
)


# --------------------------------------------------------------------------- state map


def test_states_from_endorsements_covers_the_2x2():
    b = np.array([1, 0, 0, 1])
    m = np.array([0, 1, 0, 1])
    assert list(states_from_endorsements(b, m)) == [H, C, D, I]


def test_states_from_endorsements_rejects_shape_mismatch():
    with pytest.raises(ValueError, match="same shape"):
        states_from_endorsements(np.zeros(3), np.zeros(4))


# ----------------------------------------------------------------------- construction


def test_seed_agents_must_leave_at_least_one_observed():
    states = np.full((2, 3), H, dtype=np.int8)
    with pytest.raises(ValueError, match="non-seeded agent"):
        RunTrajectory(run_id="r", states=states, seed_agents=frozenset({0, 1}))


def test_out_of_range_seed_rejected():
    states = np.full((3, 3), H, dtype=np.int8)
    with pytest.raises(ValueError, match="out of range"):
        RunTrajectory(run_id="r", states=states, seed_agents=frozenset({7}))


# --------------------------------------------------------------------------- fractions


def _traj(rows, seeds=(0,), adjacency=None):
    return RunTrajectory(
        run_id="t",
        states=np.array(rows, dtype=np.int8),
        seed_agents=frozenset(seeds),
        adjacency=adjacency,
    )


def test_state_fractions_exclude_seeds_and_sum_to_one():
    # agent 0 is the seed and stays capitulated; agents 1-4 are observed.
    traj = _traj(
        [
            [C, C, C],  # seed
            [H, H, C],
            [H, C, C],
            [H, H, H],
            [D, D, H],
        ]
    )
    f = metrics.state_fractions(traj)
    # 4 observed agents. At t=0: 3 HOLDS, 1 DESTABILISED.
    assert f["trr"][0] == pytest.approx(0.75)
    assert f["ds"][0] == pytest.approx(0.25)
    assert f["mp"][0] == pytest.approx(0.0)
    # At t=2: agents 1,2 capitulated; 3,4 hold.
    assert f["mp"][2] == pytest.approx(0.5)
    assert f["trr"][2] == pytest.approx(0.5)
    total = f["trr"] + f["mp"] + f["ds"] + f["incoherent"]
    assert np.allclose(total, 1.0)


def test_incoherence_rate_is_reported_not_absorbed():
    traj = _traj([[C, C], [I, H], [H, H], [H, H]])
    # 1 incoherent agent-round out of 3 observed agents x 2 rounds = 6.
    assert metrics.incoherence_rate(traj) == pytest.approx(1 / 6)


# ---------------------------------------------------------------------------- cascades


def test_cascade_outcomes_on_a_known_trajectory():
    traj = _traj(
        [
            [C, C, C, C],  # seed
            [H, H, C, C],
            [H, C, C, H],  # capitulates then recovers
            [H, H, H, C],
            [H, H, H, H],
        ]
    )
    # observed = agents 1..4, so denominator is 4.
    # counts capitulated per round: t0=0, t1=1, t2=2, t3=2
    assert metrics.cascade_size(traj) == pytest.approx(2 / 4)
    assert metrics.peak_cascade_size(traj) == pytest.approx(2 / 4)
    assert metrics.cascade_onset(traj) == 1.0
    assert metrics.peak_velocity(traj) == pytest.approx(1 / 4)
    assert metrics.system_capitulation(traj) is False  # 0.5 is not a strict majority
    assert metrics.irreversibility(traj) == pytest.approx(1.0)


def test_system_capitulation_requires_strict_majority():
    half = _traj([[C, C], [C, C], [C, C], [H, H], [H, H]])  # 2 of 4 observed
    assert metrics.system_capitulation(half) is False
    most = _traj([[C, C], [C, C], [C, C], [C, C], [H, H]])  # 3 of 4 observed
    assert metrics.system_capitulation(most) is True


def test_cascade_onset_is_inf_when_no_cascade():
    traj = _traj([[C, C], [H, H], [H, H]])
    assert metrics.cascade_onset(traj) == float("inf")


def test_irreversibility_is_nan_when_nothing_capitulated():
    traj = _traj([[C, C], [H, H], [H, H]])
    assert np.isnan(metrics.irreversibility(traj))


def test_irreversibility_detects_full_recovery():
    traj = _traj([[C, C, C], [H, C, H], [H, C, H], [H, H, H]])
    # peak = 2, final = 0 -> fully reversible
    assert metrics.irreversibility(traj) == pytest.approx(0.0)


# ----------------------------------------------------------------------- assortativity


def test_assortativity_is_high_when_states_cluster():
    # Two disconnected pairs; each pair shares a state. Perfect clustering.
    adj = np.zeros((5, 5))
    for i, j in [(1, 2), (2, 1), (3, 4), (4, 3)]:
        adj[i, j] = 1
    traj = _traj([[C, C], [C, C], [C, C], [H, H], [H, H]], adjacency=adj)
    assert metrics.state_assortativity(traj) == pytest.approx(1.0)


def test_assortativity_is_negative_when_states_alternate():
    # Every edge joins agents in different states -- perfectly disassortative.
    adj = np.zeros((5, 5))
    for i, j in [(1, 3), (3, 1), (2, 4), (4, 2)]:
        adj[i, j] = 1
    traj = _traj([[C, C], [C, C], [C, C], [H, H], [H, H]], adjacency=adj)
    assert metrics.state_assortativity(traj) < 0


def test_assortativity_is_nan_without_variance():
    adj = np.ones((3, 3)) - np.eye(3)
    traj = _traj([[C, C], [H, H], [H, H]], adjacency=adj)
    assert np.isnan(metrics.state_assortativity(traj))


def test_assortativity_requires_a_graph():
    with pytest.raises(ValueError, match="adjacency"):
        metrics.state_assortativity(_traj([[C, C], [H, H]]))


# ------------------------------------------------------------------------------ R_eff


def test_r_effective_is_nan_before_any_infection():
    traj = _traj([[C, C, C], [H, H, C], [H, H, H]])
    r = metrics.r_effective(traj)
    # counts over observed agents: t0=0, t1=0, t2=1 -> first ratio undefined (0 infected)
    assert np.isnan(r[0])
