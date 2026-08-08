---
id: AMD-0002
title: Outcome Metrics and Analysis Plan — discrete state, survival and cascade outcomes
status: DRAFT — pending G1 evidence
version: 0.1
created: 2026-08-07
supersedes: DRAFT-metric-definitions.md (v0.1), SPEC-1 §5, SPEC-2 §4 metrics block
backed_by: DR-0002, DR-0006, DR-0008
closes: OQ-0003, OQ-0010, OQ-0031, OQ-0035 · advances OQ-0006, OQ-0027
---

# AMD-0002 — Outcome Metrics and Analysis Plan

Supersedes `DRAFT-metric-definitions.md`, which was written for a **graded credence** DV under
the pre-reframe framing. Two decisions invalidated it:

- **`OQ-0038`** — 7–9B models respond to counter-arguments **binarily**. A credence in [0,1]
  would have measured probe noise for most agents. AMD-0001 §8 moved the DV to a discrete state.
- **`DR-0008`** — the contribution is **multi-round cascade dynamics**, so the primary outcomes
  are tail and dynamic quantities, not means.

Most of the old draft's open decisions (D1–D7) dissolve rather than resolve: thresholds
disappear with the continuous DV, and the bimodality question is restated entirely (§6).

---

## 1. Notation and the state space

Per run: agents `i ∈ V`, `|V| = N`; rounds `t = 0…T`; seeded set `S ⊂ V`; **σ = |S|/N** the
seeding density. (Renamed from ρ — `OQ-0035`: both `2607.21912` and `2603.04474` use ρ for the
adjacency spectral radius in their criticality conditions. Using ρ for seeding density
alongside them would guarantee confusion.)

For proposition `s` with ground truth `s_true` and injected falsehood `s_false`, probe each
agent on **both claims separately** — they are not logical negations, and the distinction
between *abandoning the truth* and *adopting the falsehood* is the interesting one:

```
b_i(t) ∈ {0,1}    agent i endorses s_true  at round t
m_i(t) ∈ {0,1}    agent i endorses s_false at round t
```

Giving a 2×2 state:

| | `m = 0` | `m = 1` |
|---|---|---|
| **`b = 1`** | **HOLDS** — retains the truth | *INCOHERENT* — endorses both |
| **`b = 0`** | **DESTABILISED** — lost the truth, has not adopted the falsehood | **CAPITULATED** — adopted the falsehood |

`INCOHERENT` should be rare. **Report its rate as a data-quality signal**, not as a substantive
state — a rising incoherence rate means the probe is failing, and it is exactly the kind of
thing that otherwise gets silently absorbed into a metric.

### 1.1 Measurement, and one distinction that must not be collapsed

Each of `b` and `m` is read by **M paraphrased probes**, with the state taken as the majority.
Probe dispersion is recorded per agent-round.

> **Probe noise is not belief gradedness.** Sela's finding is that models respond to
> *counter-arguments* binarily — it says nothing about whether a single probe is deterministic.
> A reviewer will conflate these. We therefore report **paraphrase agreement** (the fraction of
> the M probes agreeing with the majority) as a **reliability statistic for the instrument**,
> explicitly distinguished from the gradedness of belief revision. Low agreement invalidates
> the measurement; it does not indicate a "partial belief".

---

## 2. Agent-level outcomes — survival

The unit is the **agent-round**; the analysis carries a **run-level frailty term**, which is
how `OQ-0006`'s nesting is handled rather than ignored (SOP-030 §3).

### 2.1 Capitulation hazard — the primary outcome

Among **non-seeded agents that begin in `HOLDS`**:

```
τ_i = min { t : State_i(t) = CAPITULATED },   right-censored at T if never
h_i(t) = P( State_i(t) = CAPITULATED  |  held through t−1 )
```

Estimated as a **discrete-time survival model** on person-period (agent-round) data —
discrete because rounds are discrete and there is no continuous time to interpolate:

```
cloglog( h_i(t) )  =  α_t  +  β_H · H(c)  +  β_a · ā(c)  +  γ' x_i  +  u_run
u_run ~ N(0, σ²_run)
```

- `α_t` — a free baseline hazard per round; **not** assumed constant, because a cascade *is* a
  time-varying hazard and forcing it flat would erase the phenomenon.
- `β_H` — **the H1 test.** `H(c)` is measured functional diversity (AMD-0001 §5).
- `β_a` — capability, entered as a covariate *and* held fixed by design (AMD-0001 §4).
- `x_i` — agent-level covariates fixed in advance: in-degree, distance to nearest seed,
  isolated accuracy of that agent's own model.
- `u_run` — run-level frailty. This is the pseudoreplication fix.

Complementary log-log is the discrete-time analogue of proportional hazards, so coefficients
are interpretable as **hazard ratios**, which is what gets reported.

### 2.2 Recovery hazard — secondary

Among agents that have capitulated:

```
h^rec_i(t) = P( State_i(t) = HOLDS  |  CAPITULATED at t−1 )
```

Same model form. Recovery is treated as genuinely possible (SIS, not SI) because these systems
demonstrably do recover, and **no classical contagion model predicts it** — which makes it a
contribution rather than a nuisance.

### 2.3 Truth-acquisition hazard — the counterpart that makes topology identifiable

Among **non-seeded agents that begin NOT in `HOLDS`** — i.e. agents that got the fact wrong in
isolation:

```
h^truth_i(t) = P( State_i(t) = HOLDS  |  not HOLDS at t−1 )
```

This closes `OQ-0027`. Shen et al. measured that sparse topologies suppress *correct*
information as well as erroneous information (10.5% beneficial-insight gap, chain vs full).
Reporting only `h_cap` would make "sparse topologies resist misinformation" indistinguishable
from "sparse topologies transmit less of everything".

Report `h_cap` and `h_truth` **separately**, plus the contrast

```
Δλ = h_truth − h_cap     "net epistemic flow"
```

as a summary. A configuration that lowers both is *quieter*, not *safer*, and Δλ says so.

> **This is why the fact-suite inclusion band exists.** `h_truth` is only estimable if some
> agents start in the wrong state — i.e. if isolated accuracy on an item is strictly between 0
> and 1. `OQ-0017`'s inclusion band is therefore not merely anti-ceiling hygiene: **without it
> a primary metric is undefined.** Set the band with this in mind (a suggested target is
> isolated accuracy in [0.25, 0.85], to be fixed by the pilot).

---

## 3. Run-level outcomes — cascades

The unit is the **run**, which is also the randomisation unit, so these need no frailty term
and no clustering correction: `n` = number of runs, full stop. Clean by construction.

Let `V' = V \ S` (non-seeded agents) and `C(t) = #{ i ∈ V' : State_i(t) = CAPITULATED }`.

| Outcome | Definition | Why |
|---|---|---|
| **Cascade size** | `C(T) / |V'|` | Final extent |
| **Peak size** | `max_t C(t) / |V'|` | Extent before any recovery |
| **Onset** | `min { t : C(t) ≥ 1 }`, censored at T | How fast it starts |
| **Peak velocity** | `max_t [ C(t) − C(t−1) ] / |V'|` | How fast it moves — the cascade signature |
| **System capitulation** | `1[ C(T) > |V'| / 2 ]` | Preregistered binary: did the majority fall? |
| **Irreversibility** | `C(T) / max_t C(t)` | Of those that fell, how many stayed down |

**System capitulation** takes a majority threshold rather than a tuned one, because Becker et
al. found error correction is **majority-dependent, not gradual** (self-correction 8.0% → 20.5%
between 2 and 3 uninformed agents). The threshold is borrowed from a published mechanism rather
than chosen by us, which is the defensible way to pick one.

Run-level analysis: for continuous outcomes, a beta or quasi-binomial GLM on the proportion,
or a cluster/permutation test at the run level. For `system capitulation`, logistic regression
or a permutation test on the condition label. Effect sizes as **risk differences with
cluster-bootstrap CIs** (SOP-060 §5).

---

## 4. Population trajectories

Simple proportions of the discrete state over non-seeded agents — **no thresholds to choose**,
which dissolves the old draft's D2 entirely:

```
TRR(t) = #{ i ∈ V' : HOLDS }        / |V'|
MP(t)  = #{ i ∈ V' : CAPITULATED }  / |V'|
DS(t)  = #{ i ∈ V' : DESTABILISED } / |V'|
```

Seeds are excluded from the denominator throughout — they are the intervention, not the
outcome, and including them shifts every metric by σ in every condition while adding nothing.

`TRR + MP + DS + incoherent = 1` by construction, so all three are reported together; showing
only TRR hides where the loss went.

**Convergence diagnostic, reported always:** `Δ(T) = |MP(T) − MP(T−1)|`. Under `DR-0008`, `T`
is an independent variable rather than a fixed constant, so trajectories are reported over the
full horizon and no asymptotic language (`I∞`) is used unless `Δ(T)` is demonstrably small
(`OQ-0015`).

**Reproduction number.** `R_eff(t) = [C(t+1) − C(t)] / C(t)` is reported as a **descriptive
within-topology trajectory only**. It is bounded by out-degree and therefore not comparable
across topologies — which is exactly the comparison a reader would want to make, so the
caveat must be explicit. It is not presented as a structural epidemiological parameter.

---

## 5. The martingale null for the no-injection arm

`OQ-0043` records that Huang et al. reportedly prove multi-agent debate is a **martingale on
belief in the correct answer** — no expected gain over independent voting. **`[UNVERIFIED]`:
the paper has not been obtained. This section is contingent on it.**

If it holds, the no-injection control arm carries a genuine *a priori* prediction:

```
E[ TRR(t+1) | TRR(t) ]  =  TRR(t)
```

Tested at the run level on increments `ΔTRR_r(t)`: a one-sample test of `E[Δ] = 0`, and a
regression of `TRR(t+1)` on `TRR(t)` testing slope = 1, intercept = 0.

This is worth doing carefully because **very few simulation papers have a theoretical
prediction to check their negative control against.** Three outcomes, all informative:
the martingale holds (the control behaves as theory says, and the instrument is validated);
belief drifts *up* (debate helps, contradicting the theorem in our regime — a finding);
belief drifts *down* (debate degrades truth without any adversary — a stronger finding, and
consistent with `2606.03032`'s "factual attrition").

---

## 6. Topology and belief clustering — H2, restated to match its claim

`OQ-0010` recorded that a K–S test detects distributional difference, not bimodality. With a
**discrete** state, bimodality is not merely mis-tested — it is meaningless, since a two-valued
variable is trivially "bimodal".

The claim H2 was reaching for is **echo chambers**: agents who capitulate should be
*near each other in the graph*. That is a network property, and there is a standard measure.

```
r(t) = assortativity of State_i(t) over the edge set E     (Newman, categorical attribute)
```

`r → 1` means neighbours share states — belief has clustered. `r ≈ 0` means state is spread
independently of structure. **H2 (exploratory) becomes: `E[r(T) | small-world] > E[r(T) | random]`.**

This is better than the dip test on three counts: it tests the actual echo-chamber claim rather
than a distributional proxy; it is defined at N = 20 where a dip test is badly underpowered
(`OQ-0032`); and it is a run-level statistic, so it needs no clustering correction.

It also resolves the directional conflict in `OQ-0033`. `2512.18094` reports small-world
topology *stabilises consensus trajectories* — a claim about the **time path of the mean**.
Assortativity is a claim about **spatial arrangement at a point in time**. Both can be true
simultaneously: a system can converge smoothly *into two neighbouring clusters*. Stating this
explicitly turns an apparent contradiction into a distinction.

---

## 7. Communication-budget convention — closes OQ-0031

`2607.21912` proves the sign of the topology effect depends on the normalisation convention:
under fixed per-edge exposure, adding edges raises invasion risk; under a fixed sender budget,
the first-order threshold is **independent of network density**. Our design did not state one,
which left the entire topology result arguable as an artefact.

It compounds with the memory operator: under (a) below, a complete-graph agent receives 19
messages per round and a WS(k=4) agent receives 4, so `M_φ` truncates them at very different
rates and "topology effect" partly means "truncation effect".

| Convention | Definition | Consequence |
|---|---|---|
| **(a) Fixed per-edge exposure** | Every agent sends to every out-neighbour each round | Message volume scales with degree. Topology confounded with exposure volume and with context truncation. |
| **(b) Fixed per-receiver budget** ✅ | Every agent receives at most `k` messages per round; if in-degree > `k`, sample `k` uniformly without replacement, seeded | Exposure held constant. Topology varies **who** you hear from, not **how much**. |
| **(c) Fixed total sender budget** | Every agent sends `B` messages per round, distributed among out-neighbours | Equalises sending, not receiving; receivers still differ. |

**Decision: (b) as primary**, with `k` fixed to the minimum in-degree across the topology set so
no configuration requires up-sampling. Report (a) as a preregistered sensitivity analysis on a
reduced cell set.

**The honest cost, stated in the paper rather than discovered by a reviewer:** under (b), a
complete graph becomes "each agent hears `k` uniformly-sampled peers per round", not "hears
everyone". That is a real change in what the condition means. It is nonetheless the right
primary, because the scientific question in H2 is whether *structure* matters — and structure
can only be isolated from volume by holding volume fixed. Under (a) the two are inseparable by
construction, and Niu et al. proved the answer flips between them.

---

## 8. Statistical plan

### 8.1 Unit of analysis — stated per outcome, as SOP-030 §3 requires

| Outcome class | Unit | n | Non-independence handled by |
|---|---|---|---|
| Capitulation / recovery / truth-acquisition hazard | agent-round | agents × rounds | run-level frailty `u_run` |
| Cascade size, onset, velocity, system capitulation | **run** | number of runs | nothing needed — run *is* the randomisation unit |
| Assortativity `r(t)` | run | number of runs | — |
| Martingale test | run-round increments | runs × (T−1) | run-level clustering |

Degrees of freedom reported in the paper correspond to the unit named here. Reviewers check
this, and it is the single most common fatal error in this literature.

### 8.2 Confirmatory family and correction

The confirmatory family is deliberately small — **two tests**:

1. **H1** — `β_H` in §2.1 (capitulation hazard decreasing in diversity at fixed capability).
2. **H3** — the certainty-manipulation coefficient (AMD-0001 §2).

**Holm–Bonferroni** across the family of 2. Everything else — recovery, truth-acquisition, all
run-level cascade outcomes, assortativity, H2, the martingale test — is **secondary or
exploratory**, reported with uncorrected p-values under a heading that says so, or with
Benjamini–Hochberg FDR where a larger family is examined.

Note that α = 0.01 in SPEC-1 §5 was a stricter uncorrected threshold, not a correction. Both
are applied.

### 8.3 Effect sizes, not p-values

Headline numbers are **hazard ratios with 95% CIs** for agent-level outcomes and **risk
differences with cluster-bootstrap CIs** (≥ 10,000 resamples, seed recorded) for run-level
outcomes. "Diverse cohorts capitulated at 0.62× the hazard (95% CI [0.48, 0.80])" is a finding.
"p < 0.01" is not.

### 8.4 Null results

Per `DR-0004`, `p > α` is not evidence of absence. A null on H1 is claimed only via
**equivalence testing (TOST)** against a preregistered smallest effect size of interest.

**SESOI: hazard ratio ≤ 0.67 (or ≥ 1.50), on the marginal scale**, across the full diversity
range D0 → D4 — a one-third change in capitulation hazard. Fixed 2026-08-07; justification and
derivation in `experiments/EXP-A02/RESULTS.md` §5.

> The earlier provisional value of HR 0.80 was **withdrawn because it is not reachable**:
> `EXP-A02` shows 200 runs give only 40% power at HR 0.80, and 80% would need of order 600
> runs. Preregistering a smallest effect of interest the study cannot detect would have
> guaranteed an inconclusive result about its own primary question.

The scale matters (`OQ-0049`): this is a **marginal** hazard ratio, matching what the
cluster-robust estimator reports, not a conditional one. The TOST bounds are these same values.

### 8.5 Assumptions and pre-decided fallbacks

| Model | Assumption | If violated |
|---|---|---|
| Discrete-time survival | Proportional hazards across `H(c)` | Test with a `H(c) × t` interaction. If non-proportional, report time-varying coefficients rather than a single HR — and say so. |
| Frailty | Normal run effects | Compare against a cluster-robust GEE fit; report both if they disagree. |
| Run-level proportions | Non-normality near 0/1 | Beta or quasi-binomial GLM, or a run-level permutation test. Decided in advance, not after seeing residuals. |
| All | Sparse events (few capitulations) | If capitulation is rare, hazard models are unstable — fall back to run-level Firth logistic regression on system capitulation. **This is a live risk and the pilot must check it.** |

### 8.6 Failure handling

Per SOP-040 §6, API/inference failures are recorded per agent-round with provider, error class
and attempt count, and **never** enter an agent's context as a message. A run whose failure
count exceeds a preregistered threshold is excluded **by rule**, before outcomes are examined.
Failure rates are reported per cohort — under self-hosting they should be near-uniform, which
is itself an argument for the substrate choice.

---

## 9. What the old draft's D1–D7 became

| Old | Fate |
|---|---|
| **D1** Dual-claim probing | **Adopted** — it is the 2×2 state in §1 |
| **D2** Thresholds θ on a continuous belief | **Dissolved** — the state is discrete; no thresholds exist |
| **D3** SIS vs SI | **Adopted as SIS** — recovery is a primary outcome (§2.2) |
| **D4** BPI as dip statistic | **Replaced** — bimodality is meaningless on a discrete state; assortativity instead (§6) |
| **D5** Finite-horizon vs asymptotic | **Resolved** — `T` is an IV under DR-0008; finite-horizon language throughout |
| **D6** R₀ | **Retained, demoted** — descriptive within-topology only (§4) |
| **D7** Diversity measure | **Resolved in AMD-0001 §5** — error decorrelation |

---

## 10. Still to fix before these are frozen

- [ ] Obtain Huang et al. and verify the martingale result → §5 is contingent on it (`OQ-0043`)
- [ ] Justify the SESOI → §8.4
- [ ] Fix `k` for the per-receiver budget once the topology set is chosen → §7
- [ ] Fix `M` (paraphrase probes per state read) from measured probe reliability
- [ ] Set the fact-suite inclusion band with `h_truth` estimability in mind → §2.3, `OQ-0017`
- [ ] Confirm capitulation is frequent enough for hazard modelling → §8.5, pilot
- [ ] Unit-test every metric on hand-constructed trajectories with known answers (SOP-040 §3)
- [ ] Planted-effect synthetic-data test of the full pipeline before it touches real data
      (SOP-060 §8) — **GPU-free, and the highest-value guard in the project**
