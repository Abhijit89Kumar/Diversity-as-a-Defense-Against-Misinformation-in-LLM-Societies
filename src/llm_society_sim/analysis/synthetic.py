"""Synthetic trajectory generation with a *known planted effect*.

Implements the guard required by SOP-040 SS3 and SOP-060 SS8, and row E3 of the G1 checklist:

    The analysis pipeline is tested against synthetic data with a planted effect before it
    touches real data. This is the main guard against a pipeline bug that manufactures
    significance.

The generator simulates the belief-state process directly under a known discrete-time
hazard model, so the *true* coefficient is known by construction. Two properties must hold
and are asserted in ``tests/test_planted_effect.py``:

  1. **Sensitivity** -- when an effect is planted, the pipeline recovers it, with the
     estimate close to truth and the confidence interval excluding zero.
  2. **Calibration** -- when *no* effect is planted, the pipeline rejects at approximately
     the nominal rate. This is the more important of the two. A pipeline that finds effects
     in null data would produce a publishable-looking result from noise, and no amount of
     downstream care would catch it.

Note this module is deliberately independent of the simulation engine. It tests the
*analysis*, and coupling it to the engine would let a shared bug pass both.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..types import BeliefState, RunTrajectory

__all__ = ["HazardSpec", "simulate_run", "simulate_dataset"]


def _cloglog_inv(eta: np.ndarray | float) -> np.ndarray | float:
    """Inverse complementary log-log: h = 1 - exp(-exp(eta))."""
    return -np.expm1(-np.exp(np.clip(eta, -30.0, 30.0)))


@dataclass(frozen=True)
class HazardSpec:
    """Ground-truth parameters for the synthetic process.

    The capitulation hazard for an agent in run r at round t is

        cloglog(h) = alpha[t-1] + beta_h * H(c) + beta_a * a_bar(c) + u_r

    with ``u_r ~ N(0, sigma_run^2)``. ``beta_h`` is what the analysis must recover.

    Attributes:
        alpha: Baseline hazard per round on the cloglog scale, length T.
        beta_h: **The planted effect.** Negative means diversity is protective.
        beta_a: Coefficient on cohort mean accuracy.
        sigma_run: SD of the run-level frailty. Non-zero is the realistic case and is what
            makes cluster-robust standard errors necessary rather than optional.
        h_truth: Per-round hazard of acquiring the truth when not holding it.
        h_recover: Per-round hazard of returning to HOLDS from CAPITULATED.
        h_destabilise: Per-round hazard of HOLDS -> DESTABILISED (losing the truth without
            adopting the falsehood).
        p_incoherent: Probe-noise rate producing the INCOHERENT state. Should be small; it
            exists so the pipeline is exercised against imperfect measurement.
    """

    alpha: tuple[float, ...] = (-2.5, -2.2, -2.0, -2.0, -2.0)
    beta_h: float = 0.0
    beta_a: float = 0.0
    sigma_run: float = 0.4
    h_truth: float = 0.10
    h_recover: float = 0.08
    h_destabilise: float = 0.05
    p_incoherent: float = 0.0

    @property
    def n_rounds(self) -> int:
        return len(self.alpha)


def simulate_run(
    spec: HazardSpec,
    *,
    run_id: str,
    n_agents: int,
    h_cohort: float,
    a_bar: float,
    n_seeds: int,
    rng: np.random.Generator,
    adjacency: np.ndarray | None = None,
    condition: str = "",
) -> RunTrajectory:
    """Simulate one run's belief-state trajectory under ``spec``.

    Seeded agents are pinned to CAPITULATED for the whole run: they are the intervention
    and hold the injected claim by construction (SPEC-3 SS3.1 persona). They are excluded
    from every outcome denominator downstream.
    """
    t_max = spec.n_rounds
    states = np.empty((n_agents, t_max + 1), dtype=np.int8)

    seeds = np.arange(n_seeds)
    non_seed = np.arange(n_seeds, n_agents)

    # t = 0: agents hold the truth with probability equal to cohort isolated accuracy.
    # Agents that do not are DESTABILISED -- they got the fact wrong alone. This is what
    # makes the truth-acquisition hazard estimable (AMD-0002 SS2.3).
    init = rng.random(n_agents) < a_bar
    states[:, 0] = np.where(init, BeliefState.HOLDS, BeliefState.DESTABILISED)
    states[seeds, 0] = BeliefState.CAPITULATED

    u_run = rng.normal(0.0, spec.sigma_run) if spec.sigma_run > 0 else 0.0

    for t in range(1, t_max + 1):
        eta = spec.alpha[t - 1] + spec.beta_h * h_cohort + spec.beta_a * a_bar + u_run
        h_cap = float(_cloglog_inv(eta))

        prev = states[:, t - 1].copy()
        cur = prev.copy()

        draws = rng.random(n_agents)

        holds = prev == BeliefState.HOLDS
        # HOLDS -> CAPITULATED (the planted-effect channel), else -> DESTABILISED
        cur[holds & (draws < h_cap)] = BeliefState.CAPITULATED
        cur[holds & (draws >= h_cap) & (draws < h_cap + spec.h_destabilise)] = (
            BeliefState.DESTABILISED
        )

        destab = prev == BeliefState.DESTABILISED
        cur[destab & (draws < spec.h_truth)] = BeliefState.HOLDS
        cur[destab & (draws >= spec.h_truth) & (draws < spec.h_truth + h_cap)] = (
            BeliefState.CAPITULATED
        )

        capit = prev == BeliefState.CAPITULATED
        cur[capit & (draws < spec.h_recover)] = BeliefState.HOLDS

        if spec.p_incoherent > 0:
            noise = rng.random(n_agents) < spec.p_incoherent
            cur[noise] = BeliefState.INCOHERENT

        cur[seeds] = BeliefState.CAPITULATED
        states[:, t] = cur

    _ = non_seed  # documented for clarity; masking is handled by RunTrajectory.observed
    return RunTrajectory(
        run_id=run_id,
        states=states,
        seed_agents=frozenset(int(s) for s in seeds),
        h_cohort=h_cohort,
        a_bar=a_bar,
        condition=condition,
        adjacency=adjacency,
    )


def simulate_dataset(
    spec: HazardSpec,
    *,
    n_runs: int,
    n_agents: int = 20,
    n_seeds: int = 2,
    h_levels: tuple[float, ...] = (0.0, 0.25, 0.5, 0.75, 1.0),
    a_bar: float = 0.6,
    a_bar_jitter: float = 0.02,
    rng: np.random.Generator | None = None,
) -> list[RunTrajectory]:
    """Simulate a balanced dataset across the diversity ladder.

    ``h_levels`` mirrors the five-level ladder in AMD-0001 SS3 (D0-D4). ``a_bar`` is held
    approximately fixed across levels, as the capability-matching protocol requires
    (AMD-0001 SS4); ``a_bar_jitter`` supplies the small residual variance that real matching
    leaves behind, without which the capability covariate would be unidentifiable.
    """
    rng = rng or np.random.default_rng(0)
    runs: list[RunTrajectory] = []
    for i in range(n_runs):
        h = h_levels[i % len(h_levels)]
        a = float(np.clip(a_bar + rng.normal(0.0, a_bar_jitter), 0.05, 0.95))
        runs.append(
            simulate_run(
                spec,
                run_id=f"synthetic_{i:05d}",
                n_agents=n_agents,
                h_cohort=h,
                a_bar=a,
                n_seeds=n_seeds,
                rng=rng,
                condition=f"D{i % len(h_levels)}",
            )
        )
    return runs
