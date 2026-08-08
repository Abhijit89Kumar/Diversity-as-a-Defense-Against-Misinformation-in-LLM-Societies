"""Simulation-based power analysis for the primary hypothesis (H1).

G1 checklist row E2. Required by SOP-030 §4: replication count is fixed by a power analysis
and justified, not chosen by convention or convenience.

Analytic power formulae do not exist for this design -- a discrete-time cloglog hazard with
run-level frailty, a covariate assigned at the run level, and right-censoring at T. So power
is computed by simulation, using the *same* estimator that will analyse the real data
(validated in EXP-A01). That is the right way round: the power analysis inherits any
conservatism of the actual pipeline instead of assuming an idealised one.

Run:
    python scripts/power_analysis.py --reps 200 --out experiments/EXP-A02

Because compute is unfunded (OQ-0048, DR-0009), the operative question is not "how large can
we go" but **"how small can this be and still answer the question"**. The output is a
minimum-viable design.
"""

from __future__ import annotations

import argparse
import json
import platform
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from llm_society_sim.analysis.survival import capitulation_data, fit_discrete_hazard  # noqa: E402
from llm_society_sim.analysis.synthetic import HazardSpec, simulate_dataset  # noqa: E402

ALPHA = 0.05
Z = 1.959963985


def power_at(
    *,
    beta_h: float,
    n_runs: int,
    n_agents: int,
    n_rounds: int,
    sigma_run: float,
    reps: int,
    seed0: int,
) -> dict:
    """Fraction of replications in which the H1 coefficient is detected at alpha."""
    alpha_baseline = tuple([-2.2] * n_rounds)
    rejects = 0
    events: list[int] = []
    ests: list[float] = []
    for r in range(reps):
        spec = HazardSpec(
            alpha=alpha_baseline,
            beta_h=beta_h,
            beta_a=0.0,
            sigma_run=sigma_run,
            h_destabilise=0.0,
        )
        runs = simulate_dataset(
            spec,
            n_runs=n_runs,
            n_agents=n_agents,
            rng=np.random.default_rng(seed0 + r),
        )
        data = capitulation_data(runs)
        if data.empty or data["event"].sum() == 0:
            events.append(0)
            continue
        try:
            fit = fit_discrete_hazard(data, ["h_cohort"])
        except (ValueError, np.linalg.LinAlgError):
            continue
        i = fit.names.index("h_cohort")
        b, s = float(fit.params[i]), float(fit.se[i])
        ests.append(b)
        events.append(int(data["event"].sum()))
        if np.isfinite(s) and s > 0 and abs(b / s) > Z:
            rejects += 1
    return {
        "beta_h": beta_h,
        "hazard_ratio_full_range": float(np.exp(beta_h)),
        "n_runs": n_runs,
        "n_agents": n_agents,
        "n_rounds": n_rounds,
        "sigma_run": sigma_run,
        "reps": reps,
        "power": rejects / reps,
        "mean_events": float(np.mean(events)) if events else 0.0,
        "mean_estimate": float(np.mean(ests)) if ests else float("nan"),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=200)
    ap.add_argument("--agents", type=int, default=20)
    ap.add_argument("--rounds", type=int, default=5)
    ap.add_argument("--sigma", type=float, default=0.4)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    # beta_h is the coefficient across the FULL diversity range H in [0, 1], so
    # exp(beta_h) is the hazard ratio comparing the most diverse cohort (D4) to the least
    # diverse (D0). The SESOI in AMD-0002 SS8.4 is provisionally HR outside [0.80, 1.25],
    # i.e. |beta_h| >= 0.223 -- included here to see what it costs.
    betas = [-0.223, -0.4, -0.6, -0.9]
    run_counts = [40, 80, 120, 200]

    grid: list[dict] = []
    print(f"{'beta_h':>8}{'HR':>7}  " + "".join(f"{n:>7}" for n in run_counts))
    print(f"{'':>8}{'':>7}  " + "".join(f"{'runs':>7}" for _ in run_counts))
    for k, b in enumerate(betas):
        row = []
        for j, n in enumerate(run_counts):
            r = power_at(
                beta_h=b,
                n_runs=n,
                n_agents=args.agents,
                n_rounds=args.rounds,
                sigma_run=args.sigma,
                reps=args.reps,
                seed0=100_000 * k + 1_000 * j,
            )
            grid.append(r)
            row.append(r["power"])
        print(
            f"{b:>8.3f}{np.exp(b):>7.2f}  " + "".join(f"{p:>7.2f}" for p in row),
            flush=True,
        )

    # Sensitivity to N (agents per run) at a fixed run count.
    print("\nEffect of N (agents per run), beta_h = -0.6, 120 runs:")
    n_grid: list[dict] = []
    for k, na in enumerate([10, 20, 40]):
        r = power_at(
            beta_h=-0.6,
            n_runs=120,
            n_agents=na,
            n_rounds=args.rounds,
            sigma_run=args.sigma,
            reps=args.reps,
            seed0=500_000 + 1_000 * k,
        )
        n_grid.append(r)
        print(f"  N={na:>3}  power {r['power']:.2f}   mean events {r['mean_events']:.0f}", flush=True)

    # Sensitivity to T (rounds). Under DR-0008, T is a first-class IV, and more rounds
    # means more person-periods at risk -- so T buys power as well as cascade dynamics.
    print("\nEffect of T (rounds), beta_h = -0.6, 120 runs, N=20:")
    t_grid: list[dict] = []
    for k, nt in enumerate([3, 5, 10]):
        r = power_at(
            beta_h=-0.6,
            n_runs=120,
            n_agents=args.agents,
            n_rounds=nt,
            sigma_run=args.sigma,
            reps=args.reps,
            seed0=700_000 + 1_000 * k,
        )
        t_grid.append(r)
        print(f"  T={nt:>3}  power {r['power']:.2f}   mean events {r['mean_events']:.0f}", flush=True)

    if args.out:
        args.out.mkdir(parents=True, exist_ok=True)
        payload = {
            "alpha": ALPHA,
            "run_count_grid": grid,
            "agent_count_grid": n_grid,
            "round_count_grid": t_grid,
            "environment": {
                "python": sys.version.split()[0],
                "numpy": np.__version__,
                "platform": platform.platform(),
            },
        }
        path = args.out / "power_analysis.json"
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"\nwrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
