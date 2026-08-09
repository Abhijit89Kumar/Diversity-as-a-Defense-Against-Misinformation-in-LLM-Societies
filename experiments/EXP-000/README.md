---
id: EXP-000
title: Pilot — capability, fact validation, belief-instrument validity, and cost
status: PLANNED — ready to launch, blocked only on compute
type: PILOT
preregistered: partially — the fact-suite inclusion band and the belief-metric acceptance
  criteria are fixed in advance; the measurements themselves are exploratory
opened: 2026-08-08
---

# EXP-000 — Pilot

**This one experiment closes five G1 rows at once: B6, C3, D1, D2, E1** (and E5 follows from
them). It is the entire remaining GPU dependency in the design.

It is fully specified here so that it can be launched the day compute exists, rather than
designed then. Everything it needs — engine, metrics, prompts, fact suite, model pool — is
already built and tested.

---

## 1. Purpose

| G1 row | Question it answers |
|---|---|
| **D1** | What is each candidate model's isolated accuracy on each candidate fact? |
| **C3** | Which facts fall inside the preregistered inclusion band, and which are excluded by rule? |
| **D2** | What is `H(c)` — error decorrelation — for every planned cohort? |
| **B6** | Do our models revise **binarily** or **gradedly** under counter-argument? |
| **E1** | What do tokens, wall-clock and money actually cost per run? |

Plus two construct-validity requirements: probe reliability (V1) and nuisance-factor
sensitivity (V2) from `CONSTRUCT-VALIDITY-BELIEF-METRIC.md`.

It is **not throwaway pilot work.** Part A *is* the isolated control arm required by
`OQ-0026`, so it is a reportable condition in the paper.

---

## 2. Design

### Part A — isolated baseline

Every candidate model answers every candidate fact **alone**, with no communication.

| Factor | Levels |
|---|---|
| Model | 4 (`MODEL-POOL.md`): Qwen2.5-7B, Mistral-7B-v0.3, OLMo-2-7B, Granite-3.3-8B |
| Fact | 31 candidates (`fact-suite/candidates.json`) |
| Claim probed | `s_true`, `s_false` (separately — AMD-0002 §1) |
| Paraphrase | M = 3 |
| Option order | normal, swapped (nuisance factor, V2) |
| Free-text repetitions | 5 per model × fact, temperature 0.7 |

### Part B — counter-argument gradedness sweep (**the blocking one**)

The entire dependent variable rests on Sela's finding that 7–9B models flip rather than
shade. That is one paper, one task domain, seven models — and **not our pool**. If our models
are graded, AMD-0002 needs substantial revision, and it is far better to learn that from a
day's work than from the matrix.

Present each model with a counter-argument at five graded strengths, then re-probe:

| Strength | Counter-argument form |
|---|---|
| 0 | none (baseline) |
| 1 | bare assertion of `s_false` |
| 2 | assertion + one mechanism |
| 3 | assertion + mechanism + generic authority frame |
| 4 | all of the above, repeated by three distinct speakers |

Subset: 10 facts spanning the difficulty range. 3 repetitions.

**Read-out:** the belief response curve per family. A step function supports the discrete DV;
a smooth curve does not. Mixed behaviour across families is *both* a finding and a confound
with cohort composition, and is handled per `CONSTRUCT-VALIDITY-BELIEF-METRIC.md` §2.4.

---

## 3. Call budget and cost

Arithmetic shown so it can be checked rather than trusted. **All figures are estimates until
Part A measures them — that is what row E1 is for.**

**Part A**
```
probes      = 4 models × 31 facts × 2 claims × 3 paraphrases × 2 orders  =  1,488
generations = 4 models × 31 facts × 5 repetitions                       =    620
```

**Part B**
```
generations = 4 models × 10 facts × 5 strengths × 3 reps                =    600
probes      = 600 × 2 claims × 3 paraphrases                            =  3,600
```

**Total ≈ 1,220 generations + 5,088 probes ≈ 6,300 calls.**

Probes are single-token completions on short prompts and batch extremely well; generations are
~150 output tokens. On one L4 serving a 7–8B model with vLLM:

| Item | Estimate |
|---|---|
| Model load (×4) | ~3 min each |
| Batched inference | ~20 min per model |
| **Total** | **~2 GPU-hours, ~4 with slack** |
| **Cost at L4 $0.799/hr** | **~$1.60–3.20** |

Fits inside Modal's recurring **$30/month Starter credit** several times over
(`OQ-0048`). **G1 is blocked on work, not on money** — and this is the arithmetic behind that
claim.

---

## 4. Preregistered decision rules

Fixed **now**, before any data, so none of them becomes a researcher degree of freedom.

**Fact inclusion** (`fact-suite/README.md` §2)
- Retain iff `0.25 ≤ ā_item ≤ 0.85` across the pool.
- No single model below 0.10 or above 0.95 on a retained item.
- Retain ≥ 4 reasoning and ≥ 8 recall items.
- If > 18 qualify, keep those closest to `ā = 0.55`, ties broken by item id.

**Belief instrument** (`CONSTRUCT-VALIDITY-BELIEF-METRIC.md` §4) — any of these is a **stop
and redesign**, not a limitation to note later:
- Median paraphrase agreement < 0.80 after increasing M.
- Nuisance-factor variance ≥ injection-effect variance.
- Behavioural-consistency discrepancy > 25%.

**Diversity range (`OQ-0051`)** — H1 is estimable only if the capability-matched cohorts span
a usable range of `H(c)`. Kim (`2607.20768`) reports this measure is collinear with
`1 − mean accuracy` at ρ = 0.991, so matching accuracy may flatten `H` as well. **Criterion,
fixed now: the matched ladder must span at least 0.15 in `H(c)`, or H1 is not estimable as
specified and the design changes before the matrix runs.** Options in `OQ-0051`.

**Gradedness** — classify each family as step / graded / mixed by fitting both a step and a
logistic curve to its response profile and comparing by BIC. The classification rule is fixed
here; the outcome is not anticipated.

---

## 5. Outputs

| Artefact | Feeds |
|---|---|
| `accuracy_by_model_fact.csv` | D1, C3, capability matching |
| `retained_facts.json` + excluded items **with their measured accuracies** | C3 |
| `diversity_by_cohort.csv` (`H(c)`, plus disagreement and Q-statistic companions) | D2 |
| **`diversity_range.json` — realised spread of `H(c)` across the matched ladder** | **`OQ-0051`, blocking** |
| `gradedness_curves.csv` + per-family classification | B6 |
| `probe_reliability.csv` (paraphrase agreement, order sensitivity) | V1, V2 |
| `cost_and_timing.json` (tokens/call, latency, GPU-hours, $) | E1 |
| Raw call and probe logs (JSONL, immutable) | SOP-050 |

Excluded facts are reported **with their numbers**, so a reader can see what was dropped and
why rather than only what survived.

---

## 6. After it runs

1. Re-run `scripts/power_analysis.py` with the **measured** between-run variance replacing the
   assumed `sigma_run = 0.4`, and add fact and topology variance components. `EXP-A02` §7 is
   explicit that its table is an **upper bound** on power until this is done.
2. Rebuild the budget from measured tokens/call (`OQ-0007`).
3. Construct cohorts at matched `ā` with brackets where exact matching fails (D3), reporting
   spread as well as mean (D4, `OQ-0047`).
4. Freeze and hash the preregistration; tag `prereg-frozen`.
5. Sign off G1 in `logs/RESEARCH-LOG.md`.

---

## 7. Execution record

*To be completed at run time — SOP-040 §5.*

| Field | Value |
|---|---|
| git commit | |
| git dirty | |
| config hash | |
| model revision SHAs | |
| GPU / driver / vLLM version | |
| launched (UTC) | |
| finished (UTC) | |
| calls succeeded / failed | |
| actual GPU-hours / cost | |
| data location + checksum | |
