---
id: AMD-0001
title: Revised Experimental Design — capability-matched diversity on self-hosted open weights
status: DRAFT — pending G1 evidence
version: 0.1
created: 2026-08-07
supersedes: SPEC-1 §3 (hypotheses), SPEC-2 §3.1/§3.4/§3.5, SPEC-3 §1.1
backed_by: DR-0005, DR-0006, DR-0007
---

# AMD-0001 — Revised Experimental Design

Amendment to the v1.0 specifications, per DR-0002. The v1.0 documents remain the historical
record and are not edited.

---

## 1. What changed, in one table

| | v1.0 | Revised | Why |
|---|---|---|---|
| **Substrate** | Free-tier hosted APIs (Groq/Cerebras/Gemini) + Modal for probing | **Self-hosted open weights, 3–9B, on Modal + vLLM** | DR-0005 — primary model dies 2026-08-16; token caps 3× short; ToS conflicts; logprobs not uniform |
| **Diversity manipulation** | 2-level categorical (homogeneous / heterogeneous) | **5-level ladder at matched capability**, with measured continuous H(Θ) | DR-0006 — the confound both competing papers share |
| **Comparison control** | "Scale-matched" (parameter count) | **Accuracy-matched** (measured single-agent performance) | Parameter count is not capability; capability is the confound |
| **Confirmatory hypotheses** | H1, H2, H3, H4 | **H1 primary; H3 secondary** | DR-0006 |
| **H2 (topology/bimodality)** | Confirmatory | **Exploratory** | Topology axis occupied; bimodality untestable at N=20; direction conflicts with `2512.18094` |
| **H4 (seeding density ρ\*)** | Confirmatory | **Dropped → Future Work** | No experimental factor existed (OQ-0004); partly pre-empted |
| **Belief instrument** | Dual-probe, logits from a *single substitute model* | **Agent's own logprobs + external-classifier convergent measure** | DR-0005 dissolves OQ-0002 |
| **Controls** | `G_empty` as a pre-test | **Isolated arm + no-injection arm, both first-class analysed conditions** | OQ-0026, SOP-030 §7 |
| **Outcome metrics** | TRR / MP / BPI (error side only) | **Error side + truth-diffusion counterpart** | OQ-0027 — otherwise H2/topology results are unidentifiable |

---

## 2. Revised hypotheses

### H1 (primary, confirmatory) — Diversity damps capitulation cascades, at fixed capability

> **Claim.** Among agent populations of *equal aggregate single-agent competence*,
> populations whose members fail more independently are slower to capitulate to injected
> misinformation and more likely to recover from it.

**Formal.** For cohorts *c* with measured functional diversity `H(c)` and measured mean
isolated accuracy `ā(c)`, the hazard of capitulation

```
h_i(t | c)  is decreasing in H(c),  holding ā(c) fixed
```

tested as the coefficient `β_H` in a survival model with a run-level frailty term and `ā(c)`
entered as a covariate *and* held approximately constant by design (§4).

> **Why cascades rather than mean belief.** Two results from the review reshape this. Huang
> et al. (2025) prove multi-agent debate is a **martingale** on belief in the correct answer —
> no expected gain over independent voting (`OQ-0043`), so mean belief is the wrong place to
> look. And Sela (2026) documents that 7–9B models respond to counter-arguments **binarily**,
> warning that this *"risks inducing capitulation cascades, where the first agent to encounter
> a persuasive argument flips, creating a feedback loop"* (`OQ-0038`) — and then designs around
> the hazard instead of studying it. H1 studies it. The action is in the tails, not the mean.

**Falsifier.** `β_H` is not distinguishable from zero, or is negative, once `ā` is
controlled. Given `OQ-0039`, this is a live possibility and is a publishable result under
DR-0004.

**Direction pre-commitment** (closes `OQ-0029`): support for H1 requires higher **truth
retention**, not merely slower convergence. If diverse cohorts resist misinformation *and*
converge more slowly on the truth in the no-injection control, that is reported as a
**trade-off**, not as support — and the trade-off is itself a finding.

### H3 (secondary, confirmatory) — Stated certainty as a causal driver

> **Claim.** Holding argument *content* fixed, increasing the stated certainty of a message
> increases the belief shift it induces in receiving neighbours.

Converted from a regression to a **manipulation** (`OQ-0011`): the same argument text is
rendered at low / medium / high stated certainty by template, randomised per message. This
makes certainty exogenous and licenses the causal claim that SPEC-1's partial-derivative
formulation asserts. Analysed with run-level random intercepts.

### H2 (exploratory) — Topology

Reported, not claimed. Topology is a controlled factor with the communication-budget
convention fixed and stated (`OQ-0031`). The bimodality framing is dropped unless the pilot
demonstrates adequate power at the chosen N (`OQ-0032`) *and* the directional conflict with
`2512.18094` is resolved (`OQ-0033`).

### H4 — Removed

Moved to Future Work with a citation to `2606.16710` (threshold result) and `2605.17353`
(which stakes the phase-transition idea in its Future Work).

---

## 3. The diversity ladder

The central design object. Five cohort types, each of N agents, **all matched on `ā`**:

| Level | Composition | Source of decorrelation |
|---|---|---|
| **D0 — Identical** | N copies of model M, one persona, T = 0 | None (baseline) |
| **D1 — Stochastic** | N copies of M, one persona, sampling temperature > 0 | Sampling noise only |
| **D2 — Persona** | N copies of M, k distinct reasoning personas | Prompting |
| **D3 — Cross-lineage** | k distinct model families, accuracy-matched to D0 | Pretraining + post-training + architecture (confounded — `OQ-0052`) |
| **D4 — Combined** | k families × k personas | Both |

> **Renamed 2026-08-08.** D3 was "Architectural". Zhang et al. (`2606.20632`) show a
> within-family post-training difference can exceed a cross-family one, so a family label
> does not isolate architecture. "Cross-lineage" states what is actually manipulated
> (`OQ-0052`).

**Why the ladder is the contribution.** Every prior study compares one homogeneous
configuration against one heterogeneous configuration. That design cannot distinguish
"architectural diversity protects" from "any decorrelation protects". The ladder can:

- If D1 and D2 deliver protection comparable to D3, **diversity is cheap** — you do not need
  multiple model families, just varied sampling or prompting. That is a *more useful* finding
  for practitioners and is currently unknown.
- If only D3 and D4 protect, architectural diversity is doing something prompting cannot,
  which is the strong form of the Functional Diversity Defense Hypothesis.
- Either way the result is publishable, and neither outcome is a disappointment.

D0–D2 all use a single served model, so the marginal serving cost of three of the five levels
is near zero. This is the design being *cheaper* as well as sharper.

---

## 4. Capability matching — the protocol

This is the methodological core and the thing neither competing paper has.

1. **Measure isolated accuracy.** Every candidate model answers the full validated fact suite
   alone, no communication, many repetitions. Yields `a_m` per model, with a confidence
   interval. This run doubles as the **isolated control arm** (§6) and as the fact-suite
   validation pass (`OQ-0017`).
2. **Compute cohort capability.** For a cohort with composition weights `w_m`,
   `ā(c) = Σ_m w_m · a_m`.
3. **Match by construction.** Select the D0/D1/D2 base model M such that `a_M ≈ ā(D3)`. Where
   an exact match is impossible, construct *several* D0 cohorts bracketing `ā(D3)` from above
   and below, so the comparison can be interpolated rather than assumed.
4. **Adjust statistically as well.** Enter `ā(c)` as a covariate regardless. Matching by
   design plus adjustment is belt-and-braces; either alone is contestable.
5. **Report `ā` for every cohort in every results table.** A reader must be able to see that
   the capability control held.

> **A second, less obvious reason this matters.** Ensemble-diversity measures are known to be
> near-collinear with member accuracy — a diversity statistic can be largely a restatement of
> `(1 − mean accuracy)`. Holding `ā` fixed by design **breaks that collinearity by
> construction**, so `H(c)` and `ā(c)` are not fighting for the same variance. The capability
> control is doing double duty: it isolates the causal claim *and* it makes the diversity
> measure interpretable. Say this explicitly in the paper — it is a real methodological point.

---

## 5. Measuring functional diversity H(Θ)

SPEC-1 §2.2's mean pairwise Jensen–Shannon divergence over output token distributions is
**not computable** across models with different tokenizers and vocabularies (`OQ-0005`).

**Replacement — error decorrelation**, computed on a held-out probe set `P` of items with
known answers, from each agent's *isolated* responses (before any interaction):

```
e_i ∈ {0,1}^|P|          correctness vector of agent i, measured in isolation
H(c) = 1 − mean_{i<j} corr( e_i , e_j )
```

This measures **independence of failures**, which is the mechanism the diversity hypothesis
actually proposes — not a proxy for it. It is computable for any model behind any interface,
requires no logprobs, and connects directly to the ensemble-diversity literature.

**Known issue to handle, not hide:** correlation between binary vectors with different
marginals has a constrained range, so `H` is not accuracy-free in general. Two mitigations,
both applied: (a) accuracy is held fixed by design (§4), which is where the constraint bites
hardest; (b) report a chance-corrected companion (pairwise disagreement and the Q-statistic)
and confirm the ranking of cohorts is stable across measures. If the ranking is not stable,
that is reported.

`H(c)` is computed and reported **for every cohort, before the matrix runs**.

> ### Amended 2026-08-08 — `OQ-0051`, and it is serious
>
> Kim (`2607.20768`, Jul 2026) audits exactly this family of measures and reports that a
> joint-correctness proxy — **which is what `H(c)` is** — is collinear with `1 − mean accuracy`
> at **Spearman ρ = 0.991**.
>
> Mitigation (a) above says holding `ā` fixed "breaks that collinearity by construction".
> That is true, and it has a consequence not followed through here: **if `H ≈ 1 − ā` and `ā`
> is held fixed across the ladder, `H` is nearly fixed too — and a predictor with no variance
> cannot test H1.**
>
> `EXP-000` must therefore report the **realised range of `H(c)` across the matched ladder**,
> against a minimum-range criterion fixed in advance. If the range is inadequate, the design
> changes before the matrix runs, not after. Options are enumerated in `OQ-0051`.

---

## 6. Mandatory control arms

Both are analysed conditions with rows in every results table, not pre-tests.

| Arm | Definition | Answers |
|---|---|---|
| **Isolated** (`G_empty`) | Each agent answers alone; no messages exchanged | Did the *network* do anything? Confirmed 3-0 that multi-agent debate does not reliably beat single-agent baselines (`OQ-0026`), so this is not optional. Also supplies `a_m` for §4 and the fact validation for `OQ-0017`. |
| **No-injection** | Full network, no seeded agents | Negative control (SOP-030 §7). If the pipeline reports infection here, the pipeline is broken. Also gives the truth-diffusion baseline. |

---

## 7. Outcome metrics

Per `DRAFT-metric-definitions.md`, with one addition forced by `OQ-0027`:

- **Error side:** TRR, MP as defined there — seeds excluded from the denominator, continuous
  primary, thresholded secondary with sensitivity over θ.
- **Truth side (new):** propagation of *correct* belief originating from non-seeded agents,
  measured on the same scale. Without this, "sparse topologies resist misinformation" cannot
  be distinguished from "sparse topologies transmit less of everything" — Shen et al.
  measured a 10.5% beneficial-insight gap between chain and full connectivity.
- **Recovery:** whether agents who adopt the falsehood later abandon it. Treated as SIS, and
  reported as a primary descriptive outcome — no classical model predicts it.

Report at least one **published** metric alongside ours for comparability (`OQ-0036`) —
`2605.17353`'s Robustness/Recovery pair is the strongest candidate because their backbones
are 3–4B, directly comparable to our substrate.

---

## 8. Belief instrument — now a discrete state, not a graded credence

DR-0005 resolves the instrument confound: **every agent's belief is read from that agent's
own model.** No substitute model, no cross-condition instrument difference.

But reading `2604.26561` in full (2026-08-07) forces a second, larger change. §7.4, verbatim:

> *"8B models exhibit binary rather than graded responses to counter-arguments: they either
> maintain their position entirely… or capitulate entirely… The absence of a 'consider and
> reject' middle state… appears to be a robust characteristic of the **7–9B parameter range**."*

DR-0005 selected exactly that range. A graded credence in [0,1] would therefore be measuring
probe noise for most agents.

**Revised DV: discrete belief state, analysed by survival methods.**

```
State_i(t) ∈ { Holds-truth , Capitulated , Destabilised }
```

Primary outcomes become **time-to-capitulation**, **hazard rate**, and **recovery rate**
(capitulated → holds-truth), estimated with a survival model carrying a run-level frailty
term — which also handles the nesting in `OQ-0006` naturally.

This is an improvement on four counts, not a fallback:

1. It matches the measured behaviour of the model class rather than assuming behaviour it
   does not exhibit.
2. It fits the epidemiological framing **better** than a graded credence. SI/SIS models are
   discrete-state and time-to-infection is a survival outcome; v1.0 was running a continuous
   DV inside a compartmental metaphor.
3. It is cheaper — a binary state needs far fewer probes than a calibrated credence, which
   directly relieves the call-volume problem (`OQ-0007`).
4. It removes an artefact risk: a step response would have made bimodality trivially high for
   reasons unrelated to topology, potentially **manufacturing** an H2 confirmation.

**And it identifies the phenomenon the paper is actually about.** The same section continues:

> *"Any multi-agent architecture that exposes small-model agents to arguments from other
> agents risks inducing **capitulation cascades**, where the first agent to encounter a
> persuasive argument flips, creating a feedback loop. Architectural designs that preserve
> agent isolation during evaluation — as our system does — are necessary safeguards."*

Sela names the mechanism, flags it as a hazard, and **designs around it rather than studying
it**. This project studies it. That is a cleaner statement of the contribution than "diversity
as a defence" in the abstract: *does functional diversity damp capitulation cascades among
small models, at fixed capability?*

### Validation, in required order

1. **Gradedness / state-discreteness check (blocking).** Verify the binary pattern in *our*
   models on *our* task before freezing. One paper, one task domain, seven models is
   suggestive, not settled. If some families are graded and others are not,
   gradedness-by-family is itself a reportable finding.
2. **Convergent validity.** Score the same free-text responses with an external classifier
   (Chuang et al., Findings of NAACL 2024). Two methods, one construct — agreement is
   evidence, disagreement is a finding.
3. **Human validation** on a subsample, with attention checks and an LLM-use screen —
   non-negotiable given the reported 33–46% LLM usage among crowd workers.

α from the v1.0 dual probe (`OQ-0009`) is gone as a free parameter: measures are reported
**separately**, never mixed into one weighted scalar.

### Consequence for the analysis plan

`OQ-0043` reports that Huang et al. (2025) *prove multi-agent debate is a martingale on belief
in the correct answer, with no expected gain over independent voting*. If that holds, then in
the **no-injection control arm the expected belief trajectory should be flat** — a rare case
of a simulation study having a theoretical prediction to check its negative control against,
and it should be stated as such.

It also sharpens what H1 is about: if the mean is a martingale, the action is in the
**variance and the tails** — cascades, capitulation, recovery — not in mean belief. The
analysis plan should be built around cascade and tail behaviour rather than mean shift.

---

## 9. Deliberately deferred

Per SOP-030 §4, these are set by the power analysis and the pilot, **not chosen now**:

- N (agents per run) — `OQ-0032` argues N=20 may be too small; cost argues down. Decide with power.
- Number of facts surviving validation — over-recruit 25–30, keep those in the usable band.
- Replications per cell — must be justified, not conventional.
- T (rounds) — set by measured convergence, and hypotheses restated over a finite horizon
  (`OQ-0015`).
- Topology set and the budget convention (`OQ-0031`).
- Total run count and compute cost — from measured pilot throughput, not estimates.

---

## 10. Before G1 can close

> **Superseded 2026-08-07 by [`G1-GATE-CHECKLIST.md`](G1-GATE-CHECKLIST.md)**, which carries
> the full 18-row checklist with evidence requirements, blocking status, GPU dependency, and a
> sign-off block. This list is retained as the historical record of what was known at the time.

- [x] Read `2604.26561` in full → `OQ-0039` — done; traced onward to `LIT-0002`, threat dissolved
- [ ] Gradedness pre-check → `OQ-0038` (checklist B6 — needs GPU)
- [ ] Fact-suite validation with a preregistered inclusion band → `OQ-0017` (C2, C3)
- [ ] Candidate model pool confirmed available and licence-checked `[UNVERIFIED]` (C4)
- [ ] `H(c)` computed for every planned cohort → `OQ-0005` (D2)
- [x] Communication-budget convention fixed → `OQ-0031` — AMD-0002 §7, fixed per-receiver budget
- [x] Metric formulae frozen → `OQ-0003` — AMD-0002; D1–D7 disposition at AMD-0002 §9
- [ ] Token/timing pilot → rebuild budget from measurements → `OQ-0007`, `OQ-0014` (E1)
- [ ] Power analysis → replication count and N (E2)
- [x] Positioning statement final → `OQ-0001` — `PRIOR-ART-REVIEW.md` → v1.0 FINAL
