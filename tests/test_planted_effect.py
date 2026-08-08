"""The planted-effect guard.

SOP-040 SS3 and SOP-060 SS8 require that the analysis pipeline is validated against synthetic
data with a known planted effect **before it touches real data**. G1 checklist row E3.

Two properties, and the second matters more than the first:

  1. **Sensitivity** -- a planted effect is recovered, close to truth, CI excluding zero.
  2. **Calibration** -- with *no* effect planted, the pipeline rejects at approximately the
     nominal rate. A pipeline that finds effects in null data manufactures publishable-
     looking results out of noise, and nothing downstream would catch it.

A third test documents *why* the cluster-robust variance estimator is not optional: with
naive standard errors, the false-positive rate on null data roughly triples. That is
OQ-0006 (pseudoreplication) measured on this design rather than asserted.

Monte Carlo sizes here are kept small enough to run in CI. The fuller study lives in
``scripts/estimator_validation.py``; its results are recorded in
``experiments/EXP-A01/RESULTS.md``.
"""

from __future__ import annotations

import numpy as np
import pytest

from llm_society_sim.analysis.survival import (
    capitulation_data,
    fit_discrete_hazard,
    truth_acquisition_data,
)
from llm_society_sim.analysis.synthetic import HazardSpec, simulate_dataset

TRUE_BETA = -1.2


def _fit(beta_h: float, sigma_run: float, seed: int, n_runs: int = 150):
    spec = HazardSpec(
        beta_h=beta_h, beta_a=0.0, sigma_run=sigma_run, h_destabilise=0.0
    )
    runs = simulate_dataset(spec, n_runs=n_runs, rng=np.random.default_rng(seed))
    data = capitulation_data(runs)
    fit = fit_discrete_hazard(data, ["h_cohort"])
    i = fit.names.index("h_cohort")
    return fit.params[i], fit.se[i], fit


# ------------------------------------------------------------------------- sensitivity


def test_planted_effect_is_recovered():
    est, se, fit = _fit(TRUE_BETA, sigma_run=0.4, seed=11, n_runs=300)
    assert fit.converged
    assert fit.n_events > 100, "risk set too thin for a meaningful test"
    # Point estimate within 3 standard errors of truth.
    assert abs(est - TRUE_BETA) < 3 * se
    # And the interval excludes the null.
    hr, lo, hi = fit.hazard_ratio("h_cohort")
    assert hi < 1.0, f"protective effect not detected: HR {hr:.3f} [{lo:.3f}, {hi:.3f}]"


def test_planted_effect_direction_is_protective():
    est, _, _ = _fit(TRUE_BETA, sigma_run=0.4, seed=12, n_runs=300)
    assert est < 0, "a protective planted effect must yield a negative coefficient"


def test_no_effect_planted_gives_no_detection_on_a_fixed_seed():
    est, se, fit = _fit(0.0, sigma_run=0.4, seed=13, n_runs=300)
    hr, lo, hi = fit.hazard_ratio("h_cohort")
    assert lo < 1.0 < hi, f"false positive on null data: HR {hr:.3f} [{lo:.3f}, {hi:.3f}]"


# ------------------------------------------------------------------------- calibration


@pytest.mark.slow
def test_null_rejection_rate_is_near_nominal():
    """The critical test: on null data the pipeline must reject at about alpha.

    60 replications gives a binomial SE of ~0.028 around 0.05, so the tolerance is wide by
    necessity. The full 150-replication study is in scripts/estimator_validation.py.
    """
    reps, rejects = 60, 0
    for r in range(reps):
        est, se, _ = _fit(0.0, sigma_run=0.4, seed=3000 + r, n_runs=100)
        if abs(est / se) > 1.96:
            rejects += 1
    rate = rejects / reps
    assert rate < 0.20, (
        f"false-positive rate {rate:.3f} is far above nominal 0.05 -- the pipeline "
        "detects effects that are not there"
    )


@pytest.mark.slow
def test_estimator_is_approximately_unbiased():
    """Mean estimate over replications should sit close to the planted value."""
    reps = 40
    est = []
    for r in range(reps):
        e, _, _ = _fit(TRUE_BETA, sigma_run=0.0, seed=4000 + r, n_runs=100)
        est.append(e)
    mean = float(np.mean(est))
    sem = float(np.std(est, ddof=1) / np.sqrt(reps))
    assert abs(mean - TRUE_BETA) < 4 * sem, (
        f"mean estimate {mean:.4f} vs planted {TRUE_BETA} (SEM {sem:.4f})"
    )


@pytest.mark.slow
def test_cluster_robust_se_beats_naive_se_on_null_data():
    """Quantifies OQ-0006 on this design.

    Run-level frailty plus a run-level covariate is exactly the structure that breaks naive
    standard errors. If this test ever passes trivially it means the frailty is not being
    simulated and the guard is inert.
    """
    from llm_society_sim.analysis.survival import _numeric_hessian

    reps = 50
    rej_robust = rej_naive = 0
    for r in range(reps):
        spec = HazardSpec(beta_h=0.0, beta_a=0.0, sigma_run=0.4, h_destabilise=0.0)
        runs = simulate_dataset(spec, n_runs=100, rng=np.random.default_rng(5000 + r))
        data = capitulation_data(runs)
        fit = fit_discrete_hazard(data, ["h_cohort"])
        i = fit.names.index("h_cohort")

        y = data["event"].to_numpy(float)
        times = np.sort(data["t"].unique())
        cols = [(data["t"].to_numpy() == t).astype(float) for t in times]
        cols.append(data["h_cohort"].to_numpy(float))
        x = np.column_stack(cols)
        naive = float(
            np.sqrt(np.diag(np.linalg.inv(_numeric_hessian(fit.params, x, y))))[-1]
        )

        if abs(fit.params[i] / fit.se[i]) > 1.96:
            rej_robust += 1
        if abs(fit.params[i] / naive) > 1.96:
            rej_naive += 1

    assert rej_naive > rej_robust, (
        "naive standard errors should over-reject under run-level clustering; "
        f"robust={rej_robust}/{reps}, naive={rej_naive}/{reps}"
    )


# ---------------------------------------------------------------- risk-set construction


def test_capitulation_risk_set_excludes_seeds_and_non_holders():
    spec = HazardSpec(beta_h=0.0, sigma_run=0.0)
    runs = simulate_dataset(spec, n_runs=5, rng=np.random.default_rng(1))
    data = capitulation_data(runs)
    by_run = {r.run_id: r for r in runs}
    for _, row in data.iterrows():
        traj = by_run[row["run_id"]]
        assert row["agent"] not in traj.seed_agents, "seed leaked into the risk set"


def test_capitulation_is_absorbing_one_event_per_agent():
    spec = HazardSpec(beta_h=0.0, sigma_run=0.0)
    runs = simulate_dataset(spec, n_runs=20, rng=np.random.default_rng(2))
    data = capitulation_data(runs)
    per_agent = data.groupby(["run_id", "agent"])["event"].sum()
    assert per_agent.max() <= 1, "an agent recorded more than one first-capitulation"


def test_truth_acquisition_risk_set_is_the_complement():
    """Agents start either in the capitulation risk set or the truth-acquisition one."""
    spec = HazardSpec(beta_h=0.0, sigma_run=0.0)
    runs = simulate_dataset(spec, n_runs=20, rng=np.random.default_rng(3))
    cap = capitulation_data(runs)
    tru = truth_acquisition_data(runs)
    cap_keys = set(map(tuple, cap[["run_id", "agent"]].drop_duplicates().to_numpy()))
    tru_keys = set(map(tuple, tru[["run_id", "agent"]].drop_duplicates().to_numpy()))
    assert not (cap_keys & tru_keys), "an agent cannot be in both risk sets at t=0"
    assert tru_keys, "truth-acquisition risk set is empty -- h_truth is not estimable"
