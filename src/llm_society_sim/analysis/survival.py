"""Discrete-time survival analysis for agent-level outcomes.

Implements AMD-0002 SS2 and SS8.

The model is a discrete-time hazard with a complementary log-log link -- the discrete-time
analogue of proportional hazards, so coefficients are interpretable as hazard ratios:

    cloglog( h_i(t) ) = alpha_t + beta_H * H(c) + beta_a * a_bar(c) + gamma' x_i

Rounds are discrete, so a discrete-time formulation is correct; there is no continuous
time to interpolate. The baseline hazard alpha_t is left free per round because a cascade
*is* a time-varying hazard -- forcing it flat would erase the phenomenon under study.

**Non-independence.** AMD-0002 SS8.1 specifies a run-level frailty term. Frailty models need
`statsmodels`/`lifelines`, which are not dependencies here, so this module implements the
fallback named in AMD-0002 SS8.5: the same fixed-effects fit with **cluster-robust (sandwich)
standard errors clustered at the run**. Both handle the nesting; the sandwich makes weaker
distributional assumptions. If both are available they should be compared, and reported
together if they disagree.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Sequence

import numpy as np
import pandas as pd
from scipy import optimize, stats

from ..types import BeliefState, RunTrajectory

__all__ = [
    "person_period",
    "capitulation_data",
    "truth_acquisition_data",
    "recovery_data",
    "CloglogFit",
    "fit_discrete_hazard",
]


# --------------------------------------------------------------- person-period assembly


def person_period(
    trajectories: Iterable[RunTrajectory],
    *,
    at_risk_at_start: Callable[[int], bool],
    event_state: BeliefState,
    absorbing: bool = True,
) -> pd.DataFrame:
    """Expand trajectories into person-period (agent-round) rows.

    One row per agent per round *while that agent remains in the risk set*. This is the
    standard data layout for discrete-time survival and it makes right-censoring implicit:
    an agent that never experiences the event simply contributes rows with ``event == 0``
    until the horizon ends.

    Args:
        trajectories: Runs to expand.
        at_risk_at_start: Predicate on the agent's state at t=0 deciding entry to the risk
            set. Only non-seeded agents are ever considered.
        event_state: The state whose first occurrence counts as the event.
        absorbing: If True the agent leaves the risk set after the first event. If False,
            rows continue after the event (recurrent-event layout).

    Returns:
        DataFrame with columns: run_id, agent, t, event, h_cohort, a_bar, condition.
    """
    rows: list[dict[str, object]] = []
    for traj in trajectories:
        observed = np.flatnonzero(traj.observed)
        for agent in observed:
            if not at_risk_at_start(int(traj.states[agent, 0])):
                continue
            for t in range(1, traj.n_rounds + 1):
                event = int(traj.states[agent, t] == event_state)
                rows.append(
                    {
                        "run_id": traj.run_id,
                        "agent": int(agent),
                        "t": t,
                        "event": event,
                        "h_cohort": traj.h_cohort,
                        "a_bar": traj.a_bar,
                        "condition": traj.condition,
                    }
                )
                if event and absorbing:
                    break

    return pd.DataFrame(
        rows,
        columns=["run_id", "agent", "t", "event", "h_cohort", "a_bar", "condition"],
    )


def capitulation_data(trajectories: Iterable[RunTrajectory]) -> pd.DataFrame:
    """Risk set for the **primary** outcome (AMD-0002 SS2.1).

    Non-seeded agents that begin in HOLDS; event is the first transition to CAPITULATED.
    """
    return person_period(
        trajectories,
        at_risk_at_start=lambda s: s == BeliefState.HOLDS,
        event_state=BeliefState.CAPITULATED,
        absorbing=True,
    )


def truth_acquisition_data(trajectories: Iterable[RunTrajectory]) -> pd.DataFrame:
    """Risk set for the truth-diffusion counterpart (AMD-0002 SS2.3).

    Non-seeded agents that begin *not* in HOLDS; event is first arrival at HOLDS.

    This is what makes topology results identifiable. Shen et al. measured that sparse
    topologies suppress correct information as well as erroneous information, so reporting
    only the capitulation hazard cannot distinguish "resists misinformation" from
    "transmits less of everything".

    Note this outcome is only estimable if some agents start in the wrong state -- i.e. if
    isolated accuracy on an item is strictly between 0 and 1. That is why the fact-suite
    inclusion band (OQ-0017) is load-bearing rather than mere hygiene.
    """
    return person_period(
        trajectories,
        at_risk_at_start=lambda s: s != BeliefState.HOLDS,
        event_state=BeliefState.HOLDS,
        absorbing=True,
    )


def recovery_data(trajectories: Iterable[RunTrajectory]) -> pd.DataFrame:
    """Risk set for recovery (AMD-0002 SS2.2): capitulated agents returning to HOLDS.

    Recovery is treated as genuinely possible (SIS, not SI) because these systems
    demonstrably do recover, and no classical contagion model predicts it.

    Entry to the risk set is the round *after* first capitulation, so this cannot be built
    with ``person_period``'s t=0 predicate and is assembled directly.
    """
    rows: list[dict[str, object]] = []
    for traj in trajectories:
        for agent in np.flatnonzero(traj.observed):
            series = traj.states[agent]
            hit = np.flatnonzero(series == BeliefState.CAPITULATED)
            if hit.size == 0:
                continue
            first = int(hit[0])
            for t in range(first + 1, traj.n_rounds + 1):
                event = int(series[t] == BeliefState.HOLDS)
                rows.append(
                    {
                        "run_id": traj.run_id,
                        "agent": int(agent),
                        "t": t,
                        "time_since_capitulation": t - first,
                        "event": event,
                        "h_cohort": traj.h_cohort,
                        "a_bar": traj.a_bar,
                        "condition": traj.condition,
                    }
                )
                if event:
                    break
    return pd.DataFrame(
        rows,
        columns=[
            "run_id",
            "agent",
            "t",
            "time_since_capitulation",
            "event",
            "h_cohort",
            "a_bar",
            "condition",
        ],
    )


# ------------------------------------------------------------------- cloglog hazard fit


def _neg_loglik_and_grad(
    beta: np.ndarray, x: np.ndarray, y: np.ndarray
) -> tuple[float, np.ndarray]:
    """Negative Bernoulli log-likelihood under a cloglog link, with analytic gradient.

    h = 1 - exp(-exp(eta));  log(1-h) = -exp(eta);  log(h) = log1p(-exp(-exp(eta)))
    """
    eta = np.clip(x @ beta, -30.0, 30.0)
    u = np.exp(eta)
    s = np.exp(-u)  # = 1 - h
    one_minus_s = -np.expm1(-u)  # = h, computed stably for small u
    one_minus_s = np.clip(one_minus_s, 1e-300, 1.0)

    ll = np.sum(y * np.log(one_minus_s) - (1.0 - y) * u)
    # d(ll)/d(eta) per observation
    d_eta = y * (s * u) / one_minus_s - (1.0 - y) * u
    grad = x.T @ d_eta
    return -ll, -grad


def _score_matrix(beta: np.ndarray, x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Per-observation score contributions (n, k) of the log-likelihood."""
    eta = np.clip(x @ beta, -30.0, 30.0)
    u = np.exp(eta)
    s = np.exp(-u)
    h = np.clip(-np.expm1(-u), 1e-300, 1.0)
    d_eta = y * (s * u) / h - (1.0 - y) * u
    return x * d_eta[:, None]


def _numeric_hessian(
    beta: np.ndarray, x: np.ndarray, y: np.ndarray, eps: float = 1e-5
) -> np.ndarray:
    """Hessian of the *negative* log-likelihood by central differences on the gradient.

    Finite differences on an analytic gradient are accurate enough for a handful of
    parameters and far less error-prone than a hand-derived second derivative.
    """
    k = beta.size
    hess = np.zeros((k, k))
    for j in range(k):
        step = np.zeros(k)
        step[j] = eps
        _, g_plus = _neg_loglik_and_grad(beta + step, x, y)
        _, g_minus = _neg_loglik_and_grad(beta - step, x, y)
        hess[:, j] = (g_plus - g_minus) / (2.0 * eps)
    return 0.5 * (hess + hess.T)


@dataclass
class CloglogFit:
    """Result of a discrete-time cloglog hazard fit.

    Attributes:
        names: Parameter names, aligned with ``params``.
        params: Estimated coefficients on the cloglog scale.
        se: Cluster-robust standard errors.
        n_obs: Number of agent-round rows.
        n_clusters: Number of runs (the clustering unit).
        n_events: Number of events observed.
        converged: Whether the optimiser reported success.
    """

    names: list[str]
    params: np.ndarray
    se: np.ndarray
    n_obs: int
    n_clusters: int
    n_events: int
    converged: bool

    def hazard_ratio(self, name: str) -> tuple[float, float, float]:
        """Hazard ratio and its 95% CI for one coefficient.

        Effect sizes, not p-values, are the headline (SOP-060 SS4). "Diverse cohorts
        capitulated at 0.62x the hazard (95% CI [0.48, 0.80])" is a finding.
        """
        i = self.names.index(name)
        b, s = self.params[i], self.se[i]
        z = stats.norm.ppf(0.975)
        return float(np.exp(b)), float(np.exp(b - z * s)), float(np.exp(b + z * s))

    def p_value(self, name: str) -> float:
        """Two-sided Wald p-value. Reported alongside, never instead of, the effect size."""
        i = self.names.index(name)
        if not np.isfinite(self.se[i]) or self.se[i] == 0:
            return float("nan")
        z = self.params[i] / self.se[i]
        return float(2.0 * stats.norm.sf(abs(z)))

    def summary(self) -> pd.DataFrame:
        z = stats.norm.ppf(0.975)
        return pd.DataFrame(
            {
                "coef": self.params,
                "se": self.se,
                "hazard_ratio": np.exp(self.params),
                "hr_lo": np.exp(self.params - z * self.se),
                "hr_hi": np.exp(self.params + z * self.se),
                "p": [self.p_value(n) for n in self.names],
            },
            index=self.names,
        )


def fit_discrete_hazard(
    data: pd.DataFrame,
    covariates: Sequence[str],
    *,
    time_col: str = "t",
    event_col: str = "event",
    cluster_col: str = "run_id",
    baseline: str = "factor",
) -> CloglogFit:
    """Fit a discrete-time cloglog hazard model with cluster-robust standard errors.

    Args:
        data: Person-period rows, e.g. from :func:`capitulation_data`.
        covariates: Column names to enter as covariates (e.g. ``["h_cohort", "a_bar"]``).
        time_col: Round index column.
        event_col: 0/1 event indicator.
        cluster_col: Clustering unit. **Must be the run** -- that is the randomisation
            unit, and clustering anywhere else reintroduces the pseudoreplication that
            OQ-0006 exists to prevent.
        baseline: ``"factor"`` for a free hazard per round (default, and correct for
            cascades); ``"linear"`` for a single linear time trend, which is more
            parsimonious but assumes the hazard cannot accelerate.

    Returns:
        A :class:`CloglogFit`.
    """
    if data.empty:
        raise ValueError("no person-period rows -- risk set is empty")

    y = data[event_col].to_numpy(dtype=float)
    parts: list[np.ndarray] = []
    names: list[str] = []

    if baseline == "factor":
        times = np.sort(data[time_col].unique())
        # Full dummy set, no intercept: each column is that round's baseline hazard.
        for t in times:
            parts.append((data[time_col].to_numpy() == t).astype(float))
            names.append(f"alpha_t{t}")
    elif baseline == "linear":
        parts.append(np.ones(len(data)))
        names.append("intercept")
        parts.append(data[time_col].to_numpy(dtype=float))
        names.append("t")
    else:
        raise ValueError(f"unknown baseline: {baseline!r}")

    for c in covariates:
        col = data[c].to_numpy(dtype=float)
        if np.allclose(col, col[0]):
            raise ValueError(
                f"covariate {c!r} has no variance across the sample -- it cannot be "
                "estimated. If it is constant by design, drop it from the model."
            )
        parts.append(col)
        names.append(c)

    x = np.column_stack(parts)

    beta0 = np.zeros(x.shape[1])
    # Reasonable start for the baseline terms: overall event rate on the cloglog scale.
    rate = float(np.clip(y.mean(), 1e-4, 1 - 1e-4))
    beta0[: len(times) if baseline == "factor" else 1] = np.log(-np.log(1.0 - rate))

    result = optimize.minimize(
        _neg_loglik_and_grad,
        beta0,
        args=(x, y),
        jac=True,
        method="BFGS",
        options={"maxiter": 2000, "gtol": 1e-8},
    )
    beta = result.x

    # Cluster-robust sandwich: V = H^-1 (sum_g s_g s_g') H^-1
    hess = _numeric_hessian(beta, x, y)
    try:
        bread = np.linalg.inv(hess)
    except np.linalg.LinAlgError:
        bread = np.linalg.pinv(hess)

    scores = _score_matrix(beta, x, y)
    clusters = data[cluster_col].to_numpy()
    meat = np.zeros((x.shape[1], x.shape[1]))
    for g in np.unique(clusters):
        s_g = scores[clusters == g].sum(axis=0)
        meat += np.outer(s_g, s_g)

    n_g = len(np.unique(clusters))
    # Standard small-sample correction for cluster-robust variance.
    if n_g > 1:
        meat *= n_g / (n_g - 1.0)

    cov = bread @ meat @ bread
    se = np.sqrt(np.clip(np.diag(cov), 0.0, np.inf))

    return CloglogFit(
        names=names,
        params=beta,
        se=se,
        n_obs=len(data),
        n_clusters=n_g,
        n_events=int(y.sum()),
        converged=bool(result.success),
    )
