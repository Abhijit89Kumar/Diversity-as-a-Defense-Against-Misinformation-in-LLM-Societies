# Diversity as a Defense Against Misinformation in LLM Societies

Studying information propagation, collective intelligence, and resilience in multi-agent
LLM ecosystems.

**Artefact:** `llm-society-sim` — a simulation framework for measuring how misinformation
spreads through networks of communicating language-model agents, and whether
architectural heterogeneity in the population confers resilience.

**Core hypothesis (H1, the *Functional Diversity Defense Hypothesis*):** for a fixed
total parameter budget, a population of architecturally diverse agents resists
misinformation better than a scale-matched homogeneous population.

---

## Status

| | |
|---|---|
| **Phase** | G1 — design freeze in progress |
| **Last updated** | 2026-08-07 |
| **Design of record** | [AMD-0001](docs/03-design/AMD-0001-revised-experimental-design.md) (design) · [AMD-0002](docs/03-design/AMD-0002-outcome-metrics-and-analysis-plan.md) (metrics & analysis) |
| **Gate status** | [G1 checklist](docs/03-design/G1-GATE-CHECKLIST.md) — 10 of 18 rows closed. **Blocked on work, not money**: 5 remaining rows need GPU, all satisfied by one ~$5 pilot |
| **Code** | Analysis core built and tested — 25 tests passing. Simulation engine next. |
| **Compute** | Unfunded ([DR-0009](logs/DECISION-REGISTER.md)). All work to date is GPU-free. |
| **Timeline** | No committed date. The gate is held, not the date ([DR-0007](logs/DECISION-REGISTER.md)). |

Progress is tracked in [logs/RESEARCH-LOG.md](logs/RESEARCH-LOG.md). Read the most
recent entry first.

### Where the project stands

Three things were established in the first review and changed the plan substantially:

1. **The generic contribution is published.** Misinformation propagating through LLM agent
   communities, and topology modulating it, are each published several times over
   (2024–2026). See [PRIOR-ART-REVIEW.md](docs/02-literature/PRIOR-ART-REVIEW.md).
2. **But two 2026 papers report *contradictory* effects of model heterogeneity, and neither
   controls for capability.** That live disagreement, not an empty field, is what this
   project now answers — by isolating diversity from competence.
3. **The v1.0 execution plan was not runnable.** The primary model is deprecated on
   2026-08-16, free-tier token caps fall ~3× short, one provider's terms prohibit
   benchmarking, and the compute plan assigned a 141 GB model to a 24 GB card. See
   [FEASIBILITY-ASSESSMENT.md](docs/03-design/FEASIBILITY-ASSESSMENT.md).

The response: self-host small open weights ([DR-0005](logs/DECISION-REGISTER.md)), lead with
capability-matched diversity ([DR-0006](logs/DECISION-REGISTER.md)), and hold the gate rather
than the date ([DR-0007](logs/DECISION-REGISTER.md)).

Since then the question sharpened again. Two papers prove multi-agent debate is a
**martingale on belief in the correct answer** — *under homogeneous agents*. Our design
violates that condition by construction, so H1 became a well-posed theoretical question with
a proved null: **does architectural heterogeneity break the martingale, and does it break
toward truth when an adversary is present?** ([DR-0008](logs/DECISION-REGISTER.md),
[OQ-0050](logs/OPEN-QUESTIONS.md).)

Two validation experiments are complete, both with no compute:
[EXP-A01](experiments/EXP-A01/RESULTS.md) shows the analysis pipeline does not manufacture
significance — and that with naive standard errors the false-positive rate would **double**.
[EXP-A02](experiments/EXP-A02/RESULTS.md) fixes the design at 200 runs, N=20, and shows the
originally proposed smallest-effect-of-interest was unreachable at any feasible scale.

---

## How to use this repository

This folder is the whole project: knowledge base, lab notebook, and (from Phase 1)
codebase. Nothing that matters lives outside it.

**If you are new here, read in this order:**

1. [`docs/00-governance/SOP-000-master-research-operating-procedure.md`](docs/00-governance/SOP-000-master-research-operating-procedure.md)
   — the rules of the project, and why each one exists.
2. [`docs/01-specifications/`](docs/01-specifications/) — the v1.0 design as originally
   written. **Read-only.** This is what we intended at the start.
3. [`logs/OPEN-QUESTIONS.md`](logs/OPEN-QUESTIONS.md) — what we know is wrong or unresolved.
4. [`logs/DECISION-REGISTER.md`](logs/DECISION-REGISTER.md) — why the project looks the way
   it does now.
5. [`docs/03-design/`](docs/03-design/) — the current design, as amendments to the specs.

**Before you start any work session:** read the last research-log entry and the P0 rows
of the open-questions register. **After every session:** append a log entry (SOP-010 §1.1).

---

## Map

```
docs/
  00-governance/     SOPs — the method. Read SOP-000 first.
  01-specifications/ v1.0 source documents. READ-ONLY (DR-0002).
    source-docx/     Original .docx files as received.
  02-literature/     Prior art, reading notes, references.bib, search log.
  03-design/         Amendments, preregistration, current design.
  04-analysis/       Analysis plans and statistical output.
  05-paper/          LaTeX source, figures, submission artefacts.
logs/
  RESEARCH-LOG.md    Append-only lab notebook. Start here.
  DECISION-REGISTER.md  Numbered decisions (DR-xxxx).
  OPEN-QUESTIONS.md  Numbered open questions (OQ-xxxx), prioritised P0–P3.
  RISK-REGISTER.md   Numbered risks (RK-xxxx) with triggers.
  CHANGELOG.md       Structural changes to the repository.
meta/templates/      Templates for decisions, log entries, lit notes, experiments.
src/                 llm_society_sim package (Phase 1).
configs/             Versioned experiment configurations.
experiments/         One directory per experiment (EXP-xxx).
data/                raw/ (immutable) · interim/ · processed/ · annotations/
results/             Figures, tables, statistical output.
```

---

## The governing rules, in brief

The full set is SOP-000 §2. The three that get broken most often:

- **Evidence before assertion.** Every factual claim carries a citation, an experiment
  ID, or an explicit `[UNVERIFIED]` tag. `[UNVERIFIED]` never reaches the paper.
- **Preregister before confirmatory data.** Hypotheses, metric formulae, analyses,
  exclusions and corrections are frozen and hashed before the matrix runs. Anything not
  preregistered is labelled exploratory.
- **Deadline pressure changes scope, never method.** When time runs short we drop
  conditions and say so. We do not drop seeds, widen alpha, or unfreeze the plan.

And one commitment made in advance, in [DR-0004](logs/DECISION-REGISTER.md): **if the
central hypothesis is not supported, the paper says the central hypothesis was not
supported.** The framework, the belief-measurement protocol, and the benchmark are
contributions either way.

---

## Phase gates

Work does not advance until the gate is signed off in the research log.

| Gate | Meaning |
|---|---|
| **G0** | Foundation — repository, SOPs, registers ✅ |
| **G1** | Design frozen — prior art reviewed, P0 questions closed, belief metric validated |
| **G2** | Pilot passed — engine runs end to end, power analysis done, negative controls clean |
| **G3** | Matrix launched — preregistration frozen and hashed, budget verified empirically |
| **G4** | Analysis complete — preregistered tests run, assumptions checked, corrections applied |
| **G5** | Submitted — every number reproducible, claims audited, code released |

G1 is the gate that matters most. Nearly every avoidable way this project can fail is
decided before a single simulation runs.

---

## Target outputs

- arXiv preprint (`cs.MA`, cross-listed `cs.CL` / `cs.AI` / `cs.SI`)
- Workshop submission — AI safety / multi-agent systems track
- `llm-society-sim` open-source package (MIT)
- Interactive dashboard visualising misinformation spread (built after G4)

---

## Version control

`git` is not yet initialised here. Every reproducibility guarantee in SOP-040 depends on
commit-level provenance, so this should be the first action taken:

```bash
git init && git add -A && git commit -m "Initial commit: governed research repository"
```
