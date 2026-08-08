---
id: CONSTRUCT-VALIDITY
title: Construct validity of the belief instrument
status: DRAFT — argument complete, evidence pending EXP-000
version: 0.1
created: 2026-08-07
required_by: SOP-030 §1 · G1 checklist row B5
---

# Construct validity of the belief instrument

SOP-030 §1 puts this before every other design question, for a reason worth restating:

> Everything in this project — every hypothesis, every metric, every hazard — is a function
> of the belief state. If the instrument is invalid, a perfectly executed matrix produces
> nothing.

The instrument is defined in AMD-0002 §1: two independent binary probes per agent per round,
`b` (endorses `s_true`) and `m` (endorses `s_false`), each read by `M` paraphrases and taken
by majority, yielding a 2×2 discrete state.

This document states what must be true for that to measure belief, what could make it fail,
and what evidence closes each question. **Arguments are here; measurements come from
`EXP-000`.**

---

## 1. What the instrument claims to measure

**Claim.** `State_i(t)` reflects agent *i*'s disposition, at round *t*, to assert and act on
`s_true` versus `s_false`, given the conversation it has seen.

**What it does not claim.** It does not claim to measure an internal representation, a
"real" credence, or anything mental. That is not modesty — it is what makes the construct
testable. A dispositional claim is checkable against behaviour; a mentalistic one is not.

The paper must state this. Reviewers in this area are alert to over-claiming about LLM
"beliefs", and the defensible position is available at no scientific cost.

---

## 2. Five threats, and what closes each

### 2.1 The instrument might not be reading a stable state at all

If probe responses are near-random, the "state" is noise with a majority vote laid over it.

**Evidence required:** paraphrase agreement — the fraction of the `M` probes agreeing with
the majority — reported per model, per item, per round. **Acceptance: median agreement ≥ 0.8
across the retained fact suite.** Below that, `M` increases or the item is dropped.

> **The distinction that must not collapse.** Probe *noise* is not belief *gradedness*.
> Sela's result (`OQ-0038`) is that 7–9B models revise binarily in response to
> counter-arguments; it says nothing about whether a single probe is deterministic. A
> reviewer will conflate these. Agreement is reported as an **instrument reliability
> statistic**, explicitly separated from the gradedness of revision. Low agreement invalidates
> the measurement; it does not indicate "partial belief".

### 2.2 The state might be an artefact of prompt format, not of the conversation

**Evidence required**, from `EXP-000`, holding context fixed and varying only the nuisance
factor:

| Nuisance factor | Manipulation |
|---|---|
| Paraphrase | `M` templates, already part of the instrument |
| Option order | "true or false?" vs "false or true?" |
| Token surface | `TRUE`/`True`/`Yes` as the affirmative token |
| Position | Probe before vs after any conversation recap |

**Acceptance: the state must move less under nuisance variation than under the experimental
manipulation.** That is the whole ballgame, and it is quantifiable: report the variance in
state attributable to nuisance factors against the variance attributable to injection. If
nuisance dominates, the instrument is measuring the probe, not the agent.

This number goes in the paper whatever it says. It is a methodological contribution in its
own right, and the comparable literature does not report it.

### 2.3 The state might not be comparable across model families

This is the one that matters most, because H1 **is** the cross-family comparison. If Qwen and
OLMo differ systematically in how readily they emit `TRUE`, then a cohort difference could be
an instrument difference.

**What `DR-0005` already fixed.** Every agent's state is read from that agent's own model —
no substitute model, no cross-condition instrument difference. That dissolves the original
`OQ-0002`, which was fatal.

**What remains.** Response-style differences: one family may be more agreeable, more hedging,
or more literal about "endorse". Two mitigations, both applied:

1. **Baseline correction.** `EXP-000` measures each model's isolated state on every item with
   no conversation. Differences at baseline are instrument-plus-knowledge; the outcome of
   interest is *change from baseline* under injection, which differences the instrument bias
   out to first order.
2. **Capability matching pushes in the same direction** (AMD-0001 §4). Cohorts matched on
   measured isolated accuracy are, by construction, matched on the aggregate of knowledge and
   response style, which is what baseline accuracy actually confounds.

**Evidence required:** per-family baseline state distributions, and a demonstration that the
family effect on *change* is smaller than the family effect on *level*. If it is not, report
it and analyse change-scores only.

### 2.4 The state might be graded after all, in some families

The DV is discrete because Sela measured binary revision in 7–9B models. That is one paper,
one task domain, seven models — suggestive, not settled, and our pool (`MODEL-POOL.md`) is
not their pool.

**Evidence required (G1 row B6, blocking, needs GPU):** a counter-argument strength sweep.
Present each model with counter-arguments at graded strength and plot the response curve per
family.

Three outcomes, all handled in advance:
- **Step function everywhere** → the discrete DV is correct as specified.
- **Graded everywhere** → the DV must be reconsidered; AMD-0002 would need substantial
  revision, and better to learn that from a one-day experiment than from the matrix.
- **Graded in some families, binary in others** → this is the awkward case, and it is
  *reportable as a finding* — but it is also a confound with cohort composition, because a
  cohort containing a graded model would show different apparent dynamics for instrument
  reasons. Handling: report gradedness per family, and analyse the discrete state as primary
  with a family-gradedness covariate.

### 2.5 The instrument might disagree with an independent measure

**Evidence required:**

1. **External classifier.** Score the same free-text agent messages with a separate
   classifier, following Chuang et al. (Findings of NAACL 2024), who validated exactly this
   design and reported it as *more reliable than agents' self-reported ratings*. Two methods,
   one construct — agreement is convergent validity, disagreement is a finding.
2. **Human validation** on a subsample, with attention checks and an **LLM-use screen** —
   non-negotiable given reported 33–46% LLM usage among crowd workers
   (`FEASIBILITY-ASSESSMENT.md` §6). Fleiss' κ across ≥ 3 annotators, target κ > 0.70.
3. **Behavioural consistency.** The cheapest and least used: does an agent's stated state
   predict what it *argues for* in its next message? An agent recorded as `CAPITULATED` should
   defend `s_false`. Discrepancy rate is computable from data we already log, at zero extra
   cost, and it is the most direct evidence that the state is dispositional rather than
   verbal.

---

## 3. Free parameters — and their removal

SPEC-1 §2.4's dual probe carried a weighting constant α mixing logit and verbal probes, never
given a value or derivation — a free parameter sitting directly on the dependent variable
(`OQ-0009`).

**It is gone.** AMD-0001 §8 reports measures **separately** rather than mixing them into one
weighted scalar. Remaining parameters and their status:

| Parameter | Status |
|---|---|
| `M` (paraphrases per state read) | Fixed a priori from measured reliability (§2.1) before the matrix; not tuned afterwards |
| Majority rule | Fixed: strict majority of `M`. No threshold to tune, since the underlying probe is binary |
| Nuisance-factor set | Fixed in §2.2 |

No parameter on the DV may be chosen after seeing confirmatory outcomes (SOP-030 §1.5).

---

## 4. What would make us abandon the instrument

Stated in advance so the decision is not made under sunk-cost pressure:

- Median paraphrase agreement < 0.8 after increasing `M` → the probe is not reading a stable
  state.
- Nuisance-factor variance ≥ injection-effect variance → the instrument dominates the signal.
- Behavioural-consistency discrepancy > 25% → the state does not predict what the agent
  argues, so it is not the disposition we claim to measure.

Any of these is a **stop and redesign**, not a limitation to note in §7 of the paper.

---

## 5. Evidence checklist

| # | Evidence | Source | GPU | Status |
|---|---|---|---|---|
| V1 | Paraphrase agreement ≥ 0.8 median | `EXP-000` | 🖥️ | ☐ |
| V2 | Nuisance-factor sensitivity quantified vs manipulation | `EXP-000` | 🖥️ | ☐ |
| V3 | Per-family baseline state distributions | `EXP-000` | 🖥️ | ☐ |
| V4 | Counter-argument gradedness curve per family | `EXP-000` (G1 B6) | 🖥️ | ☐ |
| V5 | External-classifier convergent validity | after first runs | 🖥️ | ☐ |
| V6 | Behavioural consistency (state predicts next message) | after first runs | — | ☐ |
| V7 | Human validation, κ > 0.70, with LLM-use screen | annotation study | — | ☐ |

V1–V4 are all satisfied by the single `EXP-000` run. V6 is **GPU-free** and computable from
logged data — it should not wait for the others.
