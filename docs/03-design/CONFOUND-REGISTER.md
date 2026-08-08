---
id: CONFOUND-REGISTER
title: Confound register — every confound controlled, measured, or acknowledged
status: ACTIVE
version: 1.0
created: 2026-08-08
required_by: SOP-030 §5 · G1 checklist row B7
---

# Confound register

SOP-030 §5 requires that for **every** identified confound the design states one of three
things — *controlled by X*, *measured and reported as a covariate*, or *acknowledged as a
limitation*. **Silence is not an option.** This document is that statement.

The reason it is a blocking gate item rather than a writing-up task: the central claim of
this project is that four published heterogeneity results are confounded with capability. A
paper that makes that argument and then carries an unexamined confound of its own would not
survive its first review, and would deserve not to.

**Status key:** ✅ controlled by design · 📏 measured and reported · ⚠️ acknowledged limitation
· ❓ open

---

## 1. Population and capability

| # | Confound | Why it threatens H1 | Handling | Status |
|---|---|---|---|---|
| P1 | **Aggregate capability** | A mixed cohort is usually also *better on average*, so "diversity helped" and "the mix contained a stronger model" are indistinguishable. This is the flaw in all four published results. | Cohorts constructed at matched mean isolated accuracy `ā`, *and* `ā` entered as a covariate. Bracketing cohorts where exact matching fails (AMD-0001 §4). | ✅ |
| P2 | **Capability spread** | Matching the *mean* does not match the *variance*. A cohort of {40, 60, 80}% is not the object a cohort of {58, 60, 62}% is, and Li et al. (arXiv:2509.05396) report weak members can drag heterogeneous debate down. | Report per-cohort accuracy SD and range in every results table. If spread differs materially across the ladder, enter it as a covariate. | 📏 `OQ-0047` |
| P3 | **Calibration / response style by family** | One family may simply emit "TRUE" more readily, making a cohort difference an instrument difference. | Every agent probed with its **own** model (`DR-0005`), removing the cross-condition instrument difference that was fatal in v1.0. Residual style handled by baseline correction: the outcome is *change from* the isolated baseline. | ✅ + 📏 |
| P4 | **Role / persona diversity** | Prompt-role heterogeneity alone is worth up to 3.5% on a single base model (`LIT-0002`). If diverse cohorts also varied persona, H1 would be a mixture of two interventions. | System prompts are **byte-identical** across agents; persona varies only where the ladder makes it the manipulation (D2/D4). Enforced in code — `CohortSpec` rejects >1 persona for D0/D1/D3. | ✅ `OQ-0046` |
| P5 | **Sampling temperature** | Stochastic decorrelation is a *different* diversity mechanism from architectural. | Temperature is the D1 rung, held fixed within every other cohort; D0 is validated as temperature 0. | ✅ |
| P6 | **Refusal / safety-training differences** | Some families refuse to argue for falsehoods more readily. That is a confound **and** an interesting finding. | Refusal rate measured per family and reported. Seeded agents are drawn from all families in D3/D4 so refusal is not concentrated in one arm. | 📏 |
| P7 | **Verbosity** | Longer, more assertive messages may persuade regardless of model identity. | Message length logged per call; entered as a covariate in the H3 analysis, where it is the most direct competitor to stated certainty. | 📏 |

## 2. Structure and communication

| # | Confound | Why it threatens the topology claims | Handling | Status |
|---|---|---|---|---|
| S1 | **Communication-budget convention** | Niu et al. (arXiv:2607.21912) prove the *sign* of the topology effect depends on whether per-edge exposure or sender budget is held fixed. | Fixed per-receiver budget as primary, per-edge as preregistered sensitivity (AMD-0002 §7). Implemented in `topology.sample_incoming`. | ✅ `OQ-0031` |
| S2 | **Context truncation varying with degree** | Under per-edge exposure a complete-graph agent receives 19 messages and a WS(k=4) agent receives 4, so `M_φ` truncates them at very different rates — "topology effect" would partly be "truncation effect". | Dissolved by S1: with a per-receiver budget, exposure volume is constant. Truncation statistics logged per call regardless, so the assumption is checkable rather than assumed. | ✅ + 📏 |
| S3 | **Graph density vs topology family** | Complete (density 1.0) vs ER p=0.2 vs WS k=4 (≈0.21) differ 5× in edge count, so any effect involving the complete graph is confounded with connectivity. Li et al. (arXiv:2410.13909) held density at 0.08 ± 0.002 for exactly this reason. | **Open.** Note the ER-vs-WS contrast — which is what H2 actually claims — is already density-matched, so the problem is confined to the complete graph. Leading option: treat complete as a labelled *reference condition* excluded from topology-effect inference. | ❓ `OQ-0028` |
| S4 | **Seed placement relative to structure** | A seed at a hub spreads differently from a seed at a periphery, and hub-ness differs by topology. | Distance-to-nearest-seed and in-degree entered as agent-level covariates (AMD-0002 §2.1). Seed assignment is a separately-seeded randomisation. | 📏 |
| S5 | **Single graph realisation per topology** | SPEC-2 v1.0 hard-coded `seed=42`, so topology variance was never sampled and topology conclusions rested on one draw. | `seed_topology` is an explicit per-run parameter, resampled across replications. Realised density, clustering and path length logged per run — "Watts-Strogatz" is a recipe, not a measurement. | ✅ + 📏 |

## 3. Materials and measurement

| # | Confound | Why it threatens the outcome | Handling | Status |
|---|---|---|---|---|
| M1 | **Fact difficulty** | Ceiling items cannot show movement; floor items have no truth to retain. Worse, without intermediate-difficulty items the truth-acquisition risk set is empty and a primary metric is undefined. | Preregistered inclusion band `0.25 ≤ ā_item ≤ 0.85`, fixed **before** validation data is seen, plus a per-model floor (`fact-suite/README.md` §2). | ✅ `OQ-0017` |
| M2 | **Construct: recall vs reasoning** | Retrieving a fact and computing an answer are different psychological operations and should not be averaged. | `construct` is a labelled factor in the suite and is entered as a factor in analysis, never pooled. Minimum cell counts enforced by the retention rule. | ✅ + 📏 |
| M3 | **Probe format sensitivity** | If state moves more under paraphrase or option order than under the manipulation, the instrument is measuring the probe. | M paraphrases with majority vote; option order swapped systematically; nuisance-factor variance quantified against manipulation variance in `EXP-000`, with a stop-and-redesign threshold stated in advance (`CONSTRUCT-VALIDITY-BELIEF-METRIC.md` §2.2). | ✅ + 📏 |
| M4 | **Unparseable probes coerced to a default** | Silently defaulting an unreadable probe would manufacture belief states and bias the very outcome under study. | `parse_true_false` returns `None`; the engine records it and never guesses. Unparseable rate reported per run. | ✅ + 📏 |
| M5 | **Tokenizer mismatch in the memory operator** | SPEC-2 v1.0 used `tiktoken` — OpenAI's BPE — for a pool containing none of OpenAI's models. The "2000-token budget" would have meant a different amount of text per family, and family composition **is** the manipulation. | Each backend supplies its own tokenizer; the heuristic counter is used only when no model is served (`memory.py`). | ✅ |
| M6 | **Chat-template differences across families** | Each family has its own chat template; applying one family's template to another degrades it. | Each model's own chat template is applied, while the *content* placed inside it is byte-identical (P4). The template is part of the model, not part of the manipulation. | ✅ |

## 4. Execution

| # | Confound | Why it threatens the comparison | Handling | Status |
|---|---|---|---|---|
| X1 | **Inference failures correlated with condition** | SPEC-2 v1.0 returned `"[Agent Error: Latency drop]"` on failure, which would have been broadcast into neighbours' contexts as a message — and failure rates differ by model, so the corruption would have tracked the experimental condition. | A failed call produces **no message** (SOP-040 §6), enforced by a regression test. Failure rate reported per model; runs above a preregistered threshold excluded by rule, before outcomes are examined. | ✅ + 📏 |
| X2 | **Provider-side variation and silent model updates** | Hosted models change under you; `llama-3.1-8b-instant` was deprecated mid-planning. | Dissolved by self-hosting open weights (`DR-0005`). Exact revision SHAs recorded, not just model names. | ✅ |
| X3 | **Quantisation** | Quantising one arm and not another would change what those models believe, confounding the primary comparison. | If used at all, applied **uniformly** across the pool, with an equivalence check reported (`MODEL-POOL.md` §5). | ⚠️ decision pending |
| X4 | **Analysis-time pseudoreplication** | Agents within a run share a graph, a fact and a seed and talk to each other. Treating them as independent doubles the false-positive rate — measured at 0.120 vs 0.060 in `EXP-A01`. | Run-level frailty / cluster-robust SEs for agent-level outcomes; run-level analysis for cascade outcomes (AMD-0002 §8.1). | ✅ `OQ-0006` |

## 5. Acknowledged limitations — not controllable, stated in the paper

| # | Limitation |
|---|---|
| L1 | **Scale.** N = 20 agents, T rounds, ~15 facts. Justified for H1 power (`EXP-A02` §4.4) but small relative to real deployed systems, and too small for percolation-threshold claims. |
| L2 | **Model scope.** Four open-weight families at 7–8B. No frontier or closed models, so results may not transfer to systems built from stronger agents. |
| L3 | **Synthetic misinformation.** Deliberately absurd physics/arithmetic falsehoods, not real-world disinformation. That is the right scientific and ethical choice (`RELEASE-SCOPE-AND-DUAL-USE.md` §3), and it limits external validity. |
| L4 | **Simulated agents.** Findings are about simulated populations. Claims about deployed multi-agent systems are hypotheses and must be marked as such. |
| L5 | **Single seeded-persona design.** Seeded agents argue persuasively from a fixed template. Other attack styles (subtle, intermittent, coordinated) are unexplored. |

---

## 6. What must still be resolved

- [ ] **S3 — density matching** (`OQ-0028`). The only ❓ in the register.
- [ ] **X3 — quantisation decision**, before any model is served.
- [ ] **P2 — capability spread** reporting confirmed once `EXP-000` gives per-model accuracy.
- [ ] **M3 — nuisance-factor variance** measured in `EXP-000` against its stated threshold.

Every other row is either controlled by design or has a measurement committed to it.
