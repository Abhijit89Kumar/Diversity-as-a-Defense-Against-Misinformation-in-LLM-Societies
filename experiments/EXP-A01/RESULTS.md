---
id: EXP-A01
title: Estimator validation on synthetic data with a planted effect
status: COMPLETE
type: NEGATIVE-CONTROL / PIPELINE-VALIDATION
preregistered: n/a — this is a pipeline test, not a hypothesis test
opened: 2026-08-07
closed: 2026-08-07
---

# EXP-A01 — Estimator validation (planted effect)

Satisfies **G1 checklist rows E3 and E4**, required by SOP-040 §3 and SOP-060 §8:

> The analysis pipeline is tested against synthetic data with a planted effect before it
> touches real data. This is the main guard against a pipeline bug that manufactures
> significance.

**Zero GPU. Zero cost.** This is the highest-value item on the G1 checklist and it needed
no compute at all.

## Purpose

Establish, before any real data exists, that the analysis pipeline (a) recovers an effect
that is there, (b) does **not** find an effect that is not there, and (c) that the
cluster-robust variance estimator is doing necessary work rather than decorative work.

(b) matters more than (a). A pipeline that finds effects in null data would produce a
publishable-looking result out of noise, and nothing downstream would catch it.

## Method

Synthetic belief-state trajectories generated under a known discrete-time hazard
(`src/llm_society_sim/analysis/synthetic.py`):

```
cloglog( h_capitulation ) = alpha_t + beta_h · H(c) + beta_a · ā(c) + u_run
u_run ~ N(0, sigma_run²)
```

N = 20 agents, 2 seeded, T = 5 rounds, 120 runs per replication, five diversity levels
{0, 0.25, 0.5, 0.75, 1.0} mirroring the D0–D4 ladder (AMD-0001 §3), ā ≈ 0.6 with small
jitter as capability matching leaves behind. 150 replications per scenario.

Estimated by `fit_discrete_hazard` with cluster-robust standard errors clustered at the
run (AMD-0002 §8.5).

The generator is deliberately **independent of the simulation engine** — coupling them
would let a shared bug pass both tests.

## Results

Produced by `scripts/estimator_validation.py --reps 150 --runs 120`;
raw output in `estimator_validation.json`.

| Scenario | mean est | bias | emp. SD | robust SE | SE/SD | reject | coverage |
|---|---|---|---|---|---|---|---|
| null, no frailty | −0.0017 | −0.0017 | 0.1207 | 0.1162 | 0.963 | **0.067** | 0.933 |
| null, frailty 0.4 | +0.0111 | +0.0111 | 0.1509 | 0.1505 | 0.997 | **0.060** | 0.940 |
| effect (β=−1.2), no frailty | −1.2076 | −0.0076 | 0.1423 | 0.1516 | 1.065 | 1.000 | 0.973 |
| effect (β=−1.2), frailty 0.4 | −1.1673 | +0.0327 | 0.1889 | 0.1782 | 0.943 | 1.000 | 0.907 |

**Pseudoreplication — the same null data, scored two ways:**

| Scenario | cluster-robust SE | naive SE |
|---|---|---|
| null, **no** frailty | 0.067 | 0.073 |
| null, **with** frailty | **0.060** | **0.120** |

## What this establishes

1. **Unbiased.** Bias is ≤ 0.033 on a true value of −1.2 in every scenario — under 3%, and
   within Monte Carlo error in three of four cells.

2. **Correctly-sized standard errors.** The ratio of mean robust SE to empirical SD is
   0.94–1.07 across all four scenarios. This is the diagnostic that would have caught a
   broken variance estimator, and it passes.

3. **Calibrated under the null.** False-positive rates of 0.067 and 0.060 against a nominal
   0.05. With 150 replications the binomial SE is ≈ 0.018, so both are within ~1 SE.
   **The pipeline does not manufacture effects.**

4. **Near-nominal coverage** — 0.907 to 0.973 against nominal 0.95.

5. **Clustering is necessary, and only where it should be.** With no run-level frailty,
   robust and naive standard errors agree (0.067 vs 0.073) — there is nothing to cluster
   on. With frailty, the naive false-positive rate **doubles** to 0.120 while the robust
   rate stays at 0.060.

   That contrast is `OQ-0006` measured on this design rather than asserted. Our runs have
   run-level heterogeneity by construction — agents in a run share a topology, a fact and a
   seed, and they talk to each other — so the naive column is the regime we would have been
   in. **A fifth of our "significant" findings at α = 0.05 would have been noise.**

## Limitation, stated rather than buried

The frailty scenario shows a small attenuation (bias +0.033, coverage 0.907). This is
**expected and not a bug**: a fixed-effects fit with cluster-robust errors estimates the
*marginal* (population-averaged) hazard ratio, whereas `beta_h` in the generator is the
*conditional* (run-specific) coefficient. Hazard ratios are non-collapsible, so the two
differ under frailty.

**Consequence for the paper, and it is a real one:** the estimand must be named. We report
a marginal hazard ratio. The SESOI in AMD-0002 §8.4 must be stated on the same scale, or it
will be compared against the wrong quantity. Raised as `OQ-0049`.

When `statsmodels`/`lifelines` are available, fit the frailty model too and report both;
if they disagree by more than the attenuation seen here, that is a finding about the data,
not a technicality.

## Reproduce

```bash
python scripts/estimator_validation.py --reps 150 --runs 120 --out experiments/EXP-A01
```

Deterministic given the seeds in the script. Environment recorded in
`estimator_validation.json`.

## Execution record

| Field | Value |
|---|---|
| git commit | recorded at commit time |
| launched | 2026-08-07 |
| replications | 150 per scenario × 4 scenarios |
| runs per replication | 120 |
| GPU cost | **none** |
| wall clock | ~5 min |
| data | `estimator_validation.json` |
