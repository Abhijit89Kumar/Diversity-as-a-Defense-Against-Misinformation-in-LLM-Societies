"""Monte Carlo validation of the discrete-time hazard estimator.

Produces the numbers recorded in ``experiments/EXP-A01/RESULTS.md``. Per SOP-010 SS2, any
number that reaches a document carries a pointer to the script that produced it; this is
that script.

Run:
    python scripts/estimator_validation.py --reps 150 --runs 120 --out experiments/EXP-A01

What it establishes (G1 checklist row E3):
  * the estimator is approximately unbiased for the planted coefficient;
  * cluster-robust standard errors are correctly sized (mean SE ~= empirical SD);
  * interval coverage is near nominal;
  * the false-positive rate on null data is near nominal, whereas naive standard errors
    over-reject badly -- OQ-0006 (pseudoreplication) quantified on this design.
"""

from __future__ import annotations

import argparse
import json
import platform
import sys
from dataclasses import asdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from llm_society_sim.analysis.survival import (  # noqa: E402
    _numeric_hessian,
    capitulation_data,
    fit_discrete_hazard,
)
from llm_society_sim.analysis.synthetic import HazardSpec, simulate_dataset  # noqa: E402

TRUE_BETA = -1.2


def _naive_se(data, fit) -> float:
    """Model-based SE ignoring clustering -- the pseudoreplication error, quantified."""
    y = data["event"].to_numpy(float)
    times = np.sort(data["t"].unique())
    cols = [(data["t"].to_numpy() == t).astype(float) for t in times]
    cols.append(data["h_cohort"].to_numpy(float))
    x = np.column_stack(cols)
    hess = _numeric_hessian(fit.params, x, y)
    return float(np.sqrt(np.diag(np.linalg.inv(hess)))[-1])


def study(beta_h: float, sigma_run: float, reps: int, n_runs: int, seed0: int) -> dict:
    est, rob, naive = [], [], []
    rej_rob = rej_naive = cover = 0
    for r in range(reps):
        spec = HazardSpec(
            beta_h=beta_h, beta_a=0.0, sigma_run=sigma_run, h_destabilise=0.0
        )
        runs = simulate_dataset(spec, n_runs=n_runs, rng=np.random.default_rng(seed0 + r))
        data = capitulation_data(runs)
        fit = fit_discrete_hazard(data, ["h_cohort"])
        i = fit.names.index("h_cohort")
        b, s = float(fit.params[i]), float(fit.se[i])
        n = _naive_se(data, fit)

        est.append(b)
        rob.append(s)
        naive.append(n)
        if abs(b / s) > 1.96:
            rej_rob += 1
        if abs(b / n) > 1.96:
            rej_naive += 1
        if b - 1.96 * s <= beta_h <= b + 1.96 * s:
            cover += 1

    est_a = np.asarray(est)
    return {
        "beta_h_true": beta_h,
        "sigma_run": sigma_run,
        "reps": reps,
        "n_runs": n_runs,
        "mean_estimate": float(est_a.mean()),
        "bias": float(est_a.mean() - beta_h),
        "empirical_sd": float(est_a.std(ddof=1)),
        "mean_robust_se": float(np.mean(rob)),
        "mean_naive_se": float(np.mean(naive)),
        "se_ratio_robust_to_empirical": float(np.mean(rob) / est_a.std(ddof=1)),
        "rejection_rate_robust": rej_rob / reps,
        "rejection_rate_naive": rej_naive / reps,
        "coverage_95": cover / reps,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=150)
    ap.add_argument("--runs", type=int, default=120)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    scenarios = [
        ("null_no_frailty", 0.0, 0.0),
        ("null_frailty", 0.0, 0.4),
        ("effect_no_frailty", TRUE_BETA, 0.0),
        ("effect_frailty", TRUE_BETA, 0.4),
    ]

    results = {}
    print(
        f"{'scenario':<22}{'mean est':>10}{'bias':>9}{'emp SD':>9}"
        f"{'rob SE':>9}{'SE/SD':>8}{'reject':>9}{'cover':>8}"
    )
    for k, (name, beta, sigma) in enumerate(scenarios):
        r = study(beta, sigma, args.reps, args.runs, seed0=1000 + 10_000 * k)
        results[name] = r
        print(
            f"{name:<22}{r['mean_estimate']:>10.4f}{r['bias']:>9.4f}"
            f"{r['empirical_sd']:>9.4f}{r['mean_robust_se']:>9.4f}"
            f"{r['se_ratio_robust_to_empirical']:>8.3f}"
            f"{r['rejection_rate_robust']:>9.3f}{r['coverage_95']:>8.3f}"
        )

    print("\nPseudoreplication (null data): robust vs naive false-positive rate")
    for name in ("null_no_frailty", "null_frailty"):
        r = results[name]
        print(
            f"  {name:<20} robust {r['rejection_rate_robust']:.3f}   "
            f"naive {r['rejection_rate_naive']:.3f}"
        )

    if args.out:
        args.out.mkdir(parents=True, exist_ok=True)
        payload = {
            "results": results,
            "spec_defaults": asdict(HazardSpec()),
            "environment": {
                "python": sys.version.split()[0],
                "numpy": np.__version__,
                "platform": platform.platform(),
            },
        }
        path = args.out / "estimator_validation.json"
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"\nwrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
