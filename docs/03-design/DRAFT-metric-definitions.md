---
id: DRAFT-metrics
title: Formal definitions for TRR, MP, BPI, I∞ and R
status: SUPERSEDED by AMD-0002 (2026-08-07)
version: 0.1
created: 2026-08-07
superseded_by: AMD-0002-outcome-metrics-and-analysis-plan.md
---

> # ⚠ SUPERSEDED — retained as historical record only
>
> **Replaced by [`AMD-0002`](AMD-0002-outcome-metrics-and-analysis-plan.md) on 2026-08-07.**
> Do not use these definitions. Retained per SOP-010 §2 — superseded documents are marked,
> never deleted.
>
> **Why it was superseded.** This draft assumed a **graded credence** dependent variable in
> [0,1] and framed outcomes as means over it. Two decisions invalidated that premise:
>
> - `OQ-0038` — 7–9B models respond to counter-arguments **binarily**, so a graded credence
>   would have measured probe noise for most agents. AMD-0001 §8 moved the DV to a discrete
>   state.
> - `DR-0008` — the contribution reframed to **multi-round cascade dynamics**, making the
>   primary outcomes tail and dynamic quantities rather than means.
>
> Of the seven decisions this draft raised, D2 (thresholds) and D4 (bimodality via dip test)
> **dissolved** rather than resolved — thresholds do not exist on a discrete state, and
> bimodality is meaningless for a two-valued variable. See AMD-0002 §9 for the full disposition.
>
> One idea from this draft survived intact and became load-bearing: **D1, probing the true and
> false claims separately.** It is now the 2×2 state space in AMD-0002 §1.

# Draft: formal metric definitions

**Why this exists.** TRR, MP, BPI, I∞ and R₀ carry all four hypotheses and appear in
SPEC-2's output schema, but no formula for any of them exists in any of the four v1.0
documents (`OQ-0003`). Every one involves a choice that changes the results. This
document proposes definitions and marks each open choice as **`DECISION NEEDED`**. It is
a draft for discussion, not a decision — nothing here is binding until it is carried into
the preregistration via a `DR-xxxx`.

---

## 0. Notation and one structural proposal

For a single run: `N` agents indexed `i ∈ V`, rounds `t = 0…T`. `S ⊂ V` is the set of
seeded (infected) agents, `ρ = |S|/N` the seeding density. `s_true` is the ground-truth
claim; `s_false` is the injected counter-claim.

**Proposal — probe both claims, not one.** SPEC-1 §2.4 defines a single belief `B_i(s)`.
But `s_false` is not the logical negation of `s_true` — it is a different, specific claim
("NIST guidelines state 112 °C"). Probing only one collapses two distinguishable states:
an agent that has *abandoned* the truth and an agent that has *adopted* the falsehood are
not the same thing, and telling them apart is scientifically interesting.

Define two credences per agent per round:

```
B_i(t) ∈ [0,1]   credence in s_true
M_i(t) ∈ [0,1]   credence in s_false
```

This gives a 2-D belief state and a free diagnostic: `B` low **and** `M` low is
*destabilised but not converted* — a distinct and reportable outcome that a
single-probe design cannot see. Cost: doubles probe volume (relevant to `OQ-0007`).

> **`DECISION NEEDED — D1`.** Dual-claim probing (richer, 2× probe cost) or
> single-claim probing (cheaper, loses the destabilised/converted distinction)?

---

## 1. Truth Retention Rate — TRR

**Proposed primary (continuous):**

```
TRR(t) = (1 / |V \ S|) · Σ_{i ∈ V \ S}  B_i(t)
```

**Proposed secondary (thresholded, for interpretability):**

```
TRR_θ(t) = (1 / |V \ S|) · Σ_{i ∈ V \ S}  1[ B_i(t) > θ ],   θ = 0.5
```

Two choices are doing real work here:

**Seeds are excluded from the denominator.** Seeded agents are the *intervention*, not
the outcome. They are instructed to hold the false belief, so including them mechanically
depresses TRR by approximately `ρ` in every condition and adds nothing. It also makes TRR
incomparable across any future ρ sweep (`OQ-0004`). Exclude them, and say so.

**Continuous is primary.** Thresholding discards most of the signal and makes the result
sensitive to an arbitrary cut. Report the continuous version as primary and the
thresholded version alongside because it is easier to talk about.

> **`DECISION NEEDED — D2`.** Confirm seed exclusion. Confirm continuous-primary.
> Sensitivity: report all thresholded results at θ ∈ {0.5, 0.6, 0.7} (SOP-060 §2).

---

## 2. Misinformation Prevalence — MP

```
MP(t)   = (1 / |V \ S|) · Σ_{i ∈ V \ S}  M_i(t)                 continuous
MP_θ(t) = (1 / |V \ S|) · Σ_{i ∈ V \ S}  1[ M_i(t) > θ ]        thresholded
```

TRR and MP are **not** redundant, which is the argument for D1: an agent can lose
confidence in the truth without adopting the falsehood.

### Infection state

Epidemiological language requires a discrete state. Proposed:

```
Infected_i(t)      ⇔  M_i(t) > θ_inf  ∧  B_i(t) < θ_true
Destabilised_i(t)  ⇔  B_i(t) < θ_true ∧  M_i(t) ≤ θ_inf
Susceptible_i(t)   ⇔  B_i(t) ≥ θ_true
```

with `θ_inf = θ_true = 0.5` proposed, swept as sensitivity.

**Is infection absorbing?** Classical SI models never recover; SIS models do. LLM agents
demonstrably can recover — an agent may accept a false claim in round 2 and reject it in
round 4. **Proposal: treat this as SIS (recovery permitted) and report the recovery rate
as a finding in its own right.** Recovery dynamics are arguably more interesting than the
infection dynamics and no classical model predicts them. Do not force an absorbing state
onto the data because the epidemiological framing is tidier.

> **`DECISION NEEDED — D3`.** SIS (recovery permitted) confirmed? Report recovery rate as
> a primary descriptive outcome?

---

## 3. Belief Polarization Index — BPI

This is where the v1.0 plan and its statistics come apart (`OQ-0010`). H2 claims
**bimodality**; the planned two-sample K–S test detects *any* distributional difference,
which is a much weaker statement and is not what the hypothesis says.

**Proposed primary — Hartigan's dip statistic.** Computed over the run's final belief
vector `{B_i(T) : i ∈ V \ S}`:

```
BPI(t) = D_n( {B_i(t)} )          Hartigan & Hartigan dip statistic
```

It measures departure from unimodality directly, it comes with an actual test of
unimodality, and it is exactly the claim H2 makes.

**Proposed secondary — belief variance**, as a descriptive companion only:

```
Var(t) = (1 / (|V\S| − 1)) · Σ (B_i(t) − mean)²
```

Variance is *not* a polarization measure. A uniform spread and a clean two-cluster split
can have identical variance. Reporting variance as "polarization" would be a test–claim
mismatch of the same kind as the K–S problem.

**Optional tertiary — mixture-model comparison.** Fit 1- and 2-component beta mixtures to
`{B_i(T)}` and compare by BIC. Slower, but gives an interpretable cluster structure and
locations, which makes a nice figure.

Note on sample size: `N = 20` per run, minus seeds, is a small sample for a dip test.
Options: aggregate the statistic across runs within a cell, or increase `N`, or restrict
this analysis to a subset of cells run at higher `N`. **This should be checked in the
pilot before H2 is committed to** — it is entirely possible that `N = 20` cannot support
a bimodality claim at all, and it is much better to learn that now.

> **`DECISION NEEDED — D4`.** Adopt dip statistic as BPI? Resolve the small-`N` problem at
> pilot before freezing H2.

---

## 4. Asymptotic infection — I∞

H1 is stated over `I∞`; H4 over `t → ∞`. The protocol runs `T = 5` (`OQ-0015`). Five
rounds is very unlikely to be asymptotic, and claiming an asymptotic quantity from it
would not survive review.

**Proposed — two-part treatment.**

*(a) Primary, honest, finite-horizon:*

```
I(T) = MP(T)
```

Reported as "prevalence at round T", never as `I∞`. H1 restated over `I(T)`.

*(b) Secondary, if and only if the data support it:* fit a saturating curve to the
per-round trajectory

```
MP(t) = A · (1 − e^(−λt))
```

and report the fitted asymptote `A` **with its confidence interval**. Only report `A` if
the fit is good and the CI is not absurdly wide. A five-point curve often will not
support this; that is a finding, not a failure.

*Convergence diagnostic, reported either way:*

```
Δ(T) = | MP(T) − MP(T−1) |
```

If `Δ(T)` is not small, the system had not settled and every claim is explicitly about a
5-round horizon.

> **`DECISION NEEDED — D5`.** Restate H1 and H4 over a finite horizon `T`? (Recommended.)
> Or extend `T` — which multiplies cost, and `T` is already a large cost driver.

---

## 5. Reproduction number — R

**Proposed — effective reproduction number, reported descriptively, not structurally.**

```
R_eff(t) = ( #{ i ∉ S : Infected_i(t+1) ∧ ¬Infected_i(t) } ) / ( #{ i : Infected_i(t) } )
```

with `R₀ ≡ R_eff(0)`, the round in which the population is still essentially fully
susceptible.

**The honest caveat, which must appear in the paper.** In classical epidemiology `R₀` is a
property of pathogen × population. Here it is bounded above by the out-degree of the
seeded agents and therefore by the topology — in a complete graph every agent is exposed
in round 1, so `R₀` is capped by `N`. That makes `R₀` **not comparable across
topologies**, which is precisely the comparison the study wants to make.

So: report `R_eff(t)` as a descriptive trajectory *within* topology; do not use it for
cross-topology inference; and do not present it as a structural epidemiological parameter.
Overclaiming here is an easy and unnecessary way to lose a reviewer.

> **`DECISION NEEDED — D6`.** Keep R as a descriptive within-topology trajectory only?
> Or drop it and rely on TRR/MP, which carry the same information with fewer caveats?

---

## 6. Functional diversity — H(Θ)

Carried from `OQ-0005`. SPEC-1 §2.2 defines `H(Θ)` as mean pairwise Jensen–Shannon
divergence over output token distributions. **This is not computable as written across
Llama / Qwen / Gemini**: JS divergence requires a shared support, and these models have
different tokenizers and vocabularies. Gemini also does not expose full output
distributions.

Candidate redefinitions, all computable over a fixed probe set `X`:

| Option | Definition | Pro | Con |
|---|---|---|---|
| **A — Answer-space JS** | Restrict to a fixed closed answer set (e.g. `{TRUE, FALSE}`) and compute JS over the renormalised probabilities of those answers | Faithful to the original formula; computable | Needs logprobs; very low-dimensional |
| **B — Behavioural disagreement** | `1 − ` mean pairwise agreement on a held-out probe set of items | Works for any model, any API; trivially interpretable | Coarse; ignores confidence |
| **C — Embedding dispersion** | Mean pairwise distance between sentence embeddings of free-text responses on `X` | Captures reasoning style, not just answers; works via any API | Depends on the embedding model; harder to interpret |
| **D — Error-correlation** | `1 − ` mean pairwise correlation of per-item correctness vectors | Directly measures *independence of errors*, which is the actual mechanism the diversity hypothesis proposes | Needs a probe set with known answers — which we have |

**Recommendation: D as primary, B as a robustness check.** Option D is not a compromise —
it is a better fit to the theory. The Functional Diversity Defense Hypothesis is
essentially an argument that diverse agents *fail independently*, so an errors-become-
uncorrelated measure is measuring the mechanism rather than a proxy for it. It also
connects directly to the ensemble-diversity literature.

Whichever is chosen, `H(Θ)` must actually be **computed and reported per cohort**, so H1
can be tested as the continuous relationship it is stated as, rather than as a two-level
categorical.

> **`DECISION NEEDED — D7`.** Which diversity measure? And: do we build ≥4 cohorts
> spanning a range of `H(Θ)` so the relationship can be estimated, rather than 2 points?
> This is the difference between "mixed cohorts did better" and "resilience increases
> with measured functional diversity" — the second is a substantially stronger paper.

---

## 7. What must be true before these are frozen

- [ ] D1–D7 decided and recorded as `DR-xxxx`
- [ ] Each metric implemented with unit tests on hand-constructed trajectories with known
      answers (SOP-040 §3)
- [ ] Threshold sensitivity plan written into the preregistration
- [ ] Dip-test small-`N` feasibility checked in the pilot (§3)
- [ ] Convergence behaviour at `T = 5` measured in the pilot (§4)
- [ ] `H(Θ)` computed for every planned cohort, before the matrix runs (§6)
