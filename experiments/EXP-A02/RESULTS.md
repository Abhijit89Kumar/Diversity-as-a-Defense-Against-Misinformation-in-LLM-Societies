---
id: EXP-A02
title: Simulation-based power analysis for H1
status: COMPLETE
type: DESIGN
preregistered: n/a — this determines the preregistered design
opened: 2026-08-07
closed: 2026-08-07
---

# EXP-A02 — Power analysis

Satisfies **G1 checklist row E2** (SOP-030 §4: replication count is justified by a power
analysis, not chosen by convention). **Zero GPU, zero cost.**

No analytic power formula exists for this design — a discrete-time cloglog hazard with
run-level frailty, a run-level covariate, and right-censoring at T. Power is therefore
computed by simulation using the **same estimator that will analyse the real data**
(validated in `EXP-A01`), so it inherits the actual pipeline's conservatism rather than
assuming an idealised one.

Produced by `scripts/power_analysis.py --reps 120`; raw output in `power_analysis.json`.
α = 0.05, two-sided. `beta_h` is the coefficient across the full diversity range H ∈ [0,1], so
`exp(beta_h)` is the hazard ratio comparing the most diverse cohort (D4) to the least (D0).

---

## 1. Power vs effect size and run count (N = 20, T = 5)

| HR (D4 vs D0) | β_H | 40 runs | 80 runs | 120 runs | 200 runs |
|---|---|---|---|---|---|
| 0.80 | −0.223 | 0.16 | 0.21 | 0.29 | **0.40** |
| 0.67 | −0.400 | 0.36 | 0.49 | 0.70 | **0.88** |
| 0.55 | −0.600 | 0.61 | 0.81 | 0.93 | 1.00 |
| 0.41 | −0.900 | 0.86 | 0.98 | 1.00 | 1.00 |

Approximate runs for 80% power: **HR 0.41 → ~35 · HR 0.55 → ~78 · HR 0.67 → ~140 ·
HR 0.80 → far beyond 200** (extrapolating, of order 600).

## 2. Agents per run (β_H = −0.6, 120 runs)

| N | Power | Mean events |
|---|---|---|
| 10 | 0.79 | 203 |
| 20 | 0.92 | 458 |
| 40 | 1.00 | 964 |

## 3. Rounds (β_H = −0.6, 120 runs, N = 20)

| T | Power | Mean events |
|---|---|---|
| 3 | 0.92 | 302 |
| 5 | 0.94 | 457 |
| 10 | 0.97 | 732 |

---

## 4. What this establishes

### 4.1 The provisional SESOI was unreachable

AMD-0002 §8.4 provisionally proposed HR outside [0.80, 1.25]. **At HR = 0.80, 200 runs give
40% power**, and reaching 80% would need roughly 600 runs — several times any plausible
compute budget, funded or not. Proposing it and never checking would have produced a study
guaranteed to be inconclusive about its own smallest effect of interest. Revised in §5.

### 4.2 T buys almost nothing for power — so set it by the science

**This is the most useful result here.** Going from T = 3 to T = 10 multiplies events by 2.4×
but moves power only 0.92 → 0.97.

The reason is structural: extra rounds add **correlated** agent-rounds within the same run,
and the cluster-robust variance correctly refuses to count them as independent. More rounds
is more information about the same runs, not more runs.

**Consequence: T is set entirely by the scientific question — how long cascades take to
develop (`DR-0008`) — and not at all by power.** That is a clean decoupling, and it means the
cascade horizon can be chosen on its merits.

### 4.3 Runs dominate; N is second; T is nearly free of power value

All three multiply inference cost roughly linearly (cost ≈ runs × N × T), so power-per-unit-
cost ranks them: **runs > N > T**.

Because runs are the *clustering unit*, precision scales with the number of clusters. This
gives a direct answer for scarce compute: **when the budget shrinks, cut N and T before
cutting runs.**

### 4.4 It answers OQ-0032 — N = 20 is adequate

`OQ-0032` worried that N = 20 looks small against the N = 200 precedent in `2605.17353`.
For **power on H1**, N = 20 at 120 runs gives 0.92, and going to N = 40 buys 0.08 for double
the cost. N = 200 would be justified by a different need — percolation thresholds or
bimodality — and both of those claims are already demoted to exploratory (AMD-0001 §2).

**N = 20 stands, and now for a stated reason rather than inheritance from SPEC-3.**

---

## 5. Revised SESOI — closes G1 row B8

> **SESOI: hazard ratio ≤ 0.67 (or ≥ 1.50), on the marginal scale, across the full
> diversity range D0 → D4.**
>
> Equivalently: a **one-third reduction in capitulation hazard**. Requires ≈ 140 runs for 80%
> power; we target **200** (see §6).

Justification, as SOP-030 §4 requires it be argued rather than asserted:

1. **It is below published effect sizes in comparable work.** Sela reports first-choice
   concentration falling 70.9% → 46.1% (r = 0.58) under architectural heterogeneity; Wan et
   al. report critical-fact retention 0.357 → 0.598. If the true effect resembles either, a
   SESOI of 0.67 detects it comfortably.
2. **It is practically meaningful.** A one-third reduction in the rate at which agents adopt
   an injected falsehood is a magnitude that would change a system designer's choice of
   population composition. A 20% reduction arguably would not, and we cannot detect it anyway.
3. **It is achievable.** ~140 runs at 80% power is within reach of the free monthly compute
   credit (`OQ-0048`), which matters given `DR-0009`.

**Stated plainly in the paper, and in the limitations:** *this design is powered to detect a
hazard ratio of about 0.67 or stronger. Smaller protective effects are outside its
resolution, and a null result is evidence against effects of that size — not against any
effect at all.*

Per `OQ-0049`, the SESOI is on the **marginal** hazard-ratio scale, matching what the
estimator reports. The TOST equivalence test required by `DR-0004` for any null claim uses
these same bounds.

---

## 6. Design recommendation

| Parameter | Value | Basis |
|---|---|---|
| Runs for the H1 contrast | **200** | 140 for 80% power at SESOI, inflated for §7 |
| N (agents per run) | **20** | §4.4 — power adequate; larger buys little |
| T (rounds) | **set by cascade onset in `EXP-000`** | §4.2 — power is indifferent |
| Diversity levels | 5 (D0–D4) | AMD-0001 §3 |

---

## 7. Limitation — real power will be lower than this

Stated rather than buried, because it changes the recommended run count.

The generator models **run-level frailty only**. The real design also carries variance from:

- **fact identity** — 15 items with different baseline difficulty and different susceptibility;
- **topology** — a factor in the design;
- **agent→node assignment** — resampled per replication;
- **model-family heterogeneity in baseline hazard** — real and not simulated here.

Each adds variance the simulation does not, so the true power at a given run count is
**lower** than the table in §1. That is why §6 recommends 200 rather than 140 — roughly a 40%
inflation as a first approximation.

**This analysis should be re-run after `EXP-000`** with the measured between-run variance
substituted for the assumed `sigma_run = 0.4`, and with fact and topology variance components
added. Until then, treat §1 as an **upper bound on power** at a given run count.

## 8. Reproduce

```bash
python scripts/power_analysis.py --reps 120 --out experiments/EXP-A02
```

Deterministic given the seeds in the script. Environment recorded in `power_analysis.json`.
