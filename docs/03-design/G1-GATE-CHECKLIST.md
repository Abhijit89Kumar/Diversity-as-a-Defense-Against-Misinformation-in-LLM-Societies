---
id: G1-CHECKLIST
title: G1 Design-Freeze Gate — evidence checklist
status: ACTIVE — gate OPEN, not passed
version: 1.0
created: 2026-08-07
backed_by: DR-0003, DR-0007, DR-0009
---

# G1 — Design Freeze: evidence checklist

**Gate status: OPEN. Not passed.** No confirmatory compute may be spent until every blocking
row below is satisfied and the sign-off block at the end is completed in
`logs/RESEARCH-LOG.md` (DR-0003).

`DR-0007` holds this gate rather than the delivery date. This document exists so that
"holding the gate" is a checkable state rather than an intention.

**GPU column** added per `DR-0009` — compute is currently unfunded (`OQ-0048`), so it matters
which rows are blocked on money and which are not. **13 of 18 rows need no GPU at all.**

---

## Legend

| | |
|---|---|
| **Blocking** | ❌ gate cannot close · ⚠️ can close with a documented exception |
| **GPU** | 🖥️ needs inference compute · — GPU-free |
| **Status** | ☐ not started · ◐ in progress · ☑ done |

---

## A — Contribution and prior art

| # | Requirement | Evidence | Block | GPU | Status |
|---|---|---|---|---|---|
| A1 | Prior-art review complete across all mandated channels | `PRIOR-ART-REVIEW.md`, `SEARCH-LOG.md` coverage checklist | ❌ | — | ◐ |
| A2 | Positioning statement written, ≤150 words, with the four evidence claims | `PRIOR-ART-REVIEW.md` → "Positioning statement v1.0 FINAL" | ❌ | — | ☑ |
| A3 | Every Tier-A paper has a `LIT-xxxx` note with a threat rating | `docs/02-literature/notes/` | ❌ | — | ◐ (2 of ~11) |
| A4 | Remaining unverified leads fetched or explicitly deferred | `OQ-0037`, `OQ-0047` | ⚠️ | — | ☐ |
| A5 | Huang et al. martingale result obtained and verified | `OQ-0043` — AMD-0002 §5 is contingent on it | ⚠️ | — | ☐ |

> **A1 is not `☑` despite the review being substantial.** `SEARCH-LOG.md`'s channel checklist
> has zero boxes ticked: OpenReview reviews, AAMAS/WWW/ICWSM/CSCW, and the mandatory forward-
> and backward-citation traversals on each Tier-A paper have not been run. The sweeps were
> broad but not systematic in the way SOP-020 §1 requires, and forward-citation search is
> precisely how one finds the paper that already did your experiment.

## B — Design and measurement

| # | Requirement | Evidence | Block | GPU | Status |
|---|---|---|---|---|---|
| B1 | Hypotheses restated with claim, formal statement, operationalisation, test, decision rule, falsifier | AMD-0001 §2 | ❌ | — | ☑ |
| B2 | All outcome metrics formally defined | AMD-0002 §§1–4 | ❌ | — | ☑ |
| B3 | Unit of analysis stated for every outcome | AMD-0002 §8.1 | ❌ | — | ☑ |
| B4 | Communication-budget convention fixed and justified | AMD-0002 §7 | ❌ | — | ☑ |
| B5 | Construct-validity argument for the belief instrument | `CONSTRUCT-VALIDITY-BELIEF-METRIC.md` — argument complete, evidence V1–V7 pending | ❌ | — | ◐ |
| B6 | **State-discreteness verified in our models, on our task** | Pilot `EXP-000` | ❌ | 🖥️ | ☐ |
| B7 | Confound register: every confound controlled / measured / acknowledged | AMD-0001 §4, `OQ-0046` | ❌ | — | ◐ |
| B8 | SESOI justified, not asserted | AMD-0002 §8.4 | ❌ | — | ☐ |

> **B6 is the one genuinely irreducible GPU dependency in the design.** The entire DV rests on
> Sela's finding that 7–9B models respond binarily — one paper, one task domain, seven models.
> If our models are graded, the DV is wrong. If some families are graded and others are not,
> that is itself a finding *and* a confound with cohort composition. This cannot be reasoned
> around; it must be measured.

## C — Materials

| # | Requirement | Evidence | Block | GPU | Status |
|---|---|---|---|---|---|
| C1 | 25–30 candidate facts curated across tiers | `fact-suite/candidates.json` — 31 items | ❌ | — | ☑ |
| C2 | Fact-suite inclusion band preregistered **before** validation | `fact-suite/README.md` §2 — band fixed at [0.25, 0.85] | ❌ | — | ☑ |
| C3 | Facts validated against isolated accuracy; out-of-band items excluded by rule | `EXP-000` | ❌ | 🖥️ | ☐ |
| C4 | Candidate model pool confirmed served, licence-checked, and downloadable | `MODEL-POOL.md` — 4 families, Apache-2.0, ungated | ❌ | — | ☑ |
| C5 | Prompt templates versioned and **byte-identical across agents** | `OQ-0046` | ❌ | — | ☐ |

> **C2 before C3, and the order is the point.** The inclusion band must be fixed before the
> validation data is seen, or item selection becomes a researcher degree of freedom on the
> dependent variable. Note also that the band is not merely anti-ceiling hygiene — without
> items at intermediate isolated accuracy, the truth-acquisition hazard (AMD-0002 §2.3) is
> **undefined**, so a primary metric depends on getting this right.

## D — Capability matching and diversity

| # | Requirement | Evidence | Block | GPU | Status |
|---|---|---|---|---|---|
| D1 | Isolated accuracy `a_m` measured per candidate model with CIs | `EXP-000` | ❌ | 🖥️ | ☐ |
| D2 | `H(c)` computed for every planned cohort, before the matrix | AMD-0001 §5 | ❌ | 🖥️ | ☐ |
| D3 | Cohorts constructed at matched `ā`, with brackets where exact matching fails | AMD-0001 §4 | ❌ | — | ☐ |
| D4 | Capability **spread** reported per cohort, not only the mean | `OQ-0047` | ⚠️ | — | ☐ |

## E — Feasibility and analysis

| # | Requirement | Evidence | Block | GPU | Status |
|---|---|---|---|---|---|
| E1 | Token/timing measured; budget rebuilt from measurement not assumption | `EXP-000`, `OQ-0007` | ❌ | 🖥️ | ☐ |
| E2 | Power analysis → N, replications, T | Needs E1 variance | ❌ | — | ☐ |
| E3 | Analysis pipeline passes a **planted-effect synthetic-data test** | `EXP-A01` | ❌ | — | ☑ |
| E4 | Every metric unit-tested on hand-constructed trajectories | `tests/test_metrics.py`, 22 tests | ❌ | — | ☑ |
| E5 | Capitulation frequent enough for hazard modelling; else Firth fallback | AMD-0002 §8.5 | ⚠️ | 🖥️ | ☐ |
| E6 | Dual-use release position taken **before** agent-facing code is committed | `RELEASE-SCOPE-AND-DUAL-USE.md`, `DR-0011` | ❌ | — | ☑ |

> **E3 ☑ 2026-08-07 — `EXP-A01`.** Passed with no compute and no cost. Estimator bias ≤ 3%,
> cluster-robust SE / empirical SD in [0.94, 1.07], false-positive rate on null data 0.060–0.067
> against nominal 0.05. And it earned its keep immediately: with naive standard errors the
> false-positive rate **doubles to 0.120** under run-level frailty, which is the regime our
> design is actually in. A fifth of "significant" findings at α = 0.05 would have been noise.
> That is `OQ-0006` measured rather than asserted.

---

## What is actually blocking

**Not compute.** Of 18 rows, **13 are GPU-free** and can be completed now:
A1–A5, B1–B5, B7, B8, C1, C2, C4, C5, D3, D4, E2 (given E1), E3, E4, E6.

**Five need inference:** B6, C3, D1, D2, E1 (and E5 follows from them). All five are satisfied
by the *single* `EXP-000` run — every candidate model answering every candidate fact in
isolation, plus a counter-argument sweep. Estimated 4–6 GPU-hours ≈ $4–6 (`OQ-0048`,
`[UNVERIFIED]`), which fits inside Modal's recurring $30/month Starter credit.

**Therefore: G1 is blocked on work, not on money.** That should stay true, and if it stops
being true it is worth saying so explicitly rather than letting the gate quietly become a
funding gate.

---

## Standing exceptions

None granted. If a `⚠️` row is closed by exception rather than evidence, record it here with a
`DR-xxxx` and the reasoning, so the exception travels with the gate rather than being forgotten.

| Row | Exception granted | DR | Rationale |
|---|---|---|---|
| — | — | — | — |

---

## Sign-off

G1 passes only when every ❌ row is `☑`, every `⚠️` row is `☑` or has a recorded exception, and
the following is appended to `logs/RESEARCH-LOG.md`:

```
G1 PASSED — YYYY-MM-DD
Checklist state: <commit hash of this file at sign-off>
Preregistration: docs/03-design/PREREGISTRATION.md, SHA-256 <hash>, tagged prereg-frozen
Signed: <names>
Outstanding exceptions: <list, or "none">
```

Until that block exists in the log, **the gate has not passed**, regardless of how much
engineering is complete.
