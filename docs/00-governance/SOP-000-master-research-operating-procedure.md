---
id: SOP-000
title: Master Research Operating Procedure
status: ACTIVE
version: 1.0
created: 2026-08-07
supersedes: none
---

# SOP-000 — Master Research Operating Procedure

This is the constitution of the project. Every other SOP derives from it. If any
document, plan, or instinct conflicts with this file, this file wins until it is
formally amended via the process in §7.

**Project:** Diversity as a Defense Against Misinformation in LLM Societies
**Artefact:** `llm-society-sim`
**Repository root:** this folder. It is simultaneously the knowledge base, the lab
notebook, and (later) the codebase. Nothing that matters lives outside it.

---

## 1. Why this SOP exists

Research fails in predictable ways. Almost none of them are "the idea was bad."
They are:

- The result was already published two years ago and nobody checked.
- The dependent variable did not measure what it claimed to measure.
- The analysis was chosen after seeing the data.
- The pipeline could not be re-run six weeks later because a config drifted.
- The deadline arrived and the honest version of the result was inconvenient.

Every rule below exists to make one of those failures harder. The rules cost time
up front. That is the point — they are cheaper than the failure they prevent.

---

## 2. The nine standing principles

### P1 — Evidence before assertion
No factual claim enters any document in this repository without one of:
a citation (`docs/02-literature/references.bib`), an experiment identifier
(`EXP-xxx`), or an explicit `[UNVERIFIED]` tag. `[UNVERIFIED]` claims may not
appear in the paper, the abstract, or any external communication.

### P2 — The specification is a source of record, not a working draft
`docs/01-specifications/` holds the v1.0 documents exactly as received. They are
read-only. They are the historical record of what we intended at the start.
All changes are **amendments** in `docs/03-design/`, each backed by a decision
record. This makes intellectual drift visible instead of invisible.

### P3 — Preregister before you collect confirmatory data
The frozen protocol (`docs/03-design/PREREGISTRATION.md`) must be complete and
timestamped *before* the confirmatory experimental matrix is launched. It fixes:
hypotheses, dependent variables and their exact formulae, the analysis for each
hypothesis, the exclusion rules, the stopping rule, and the multiple-comparison
correction. Pilot runs may inform the preregistration. Confirmatory runs may not.

### P4 — Exploratory and confirmatory analyses are labelled, always
Any analysis not named in the preregistration is exploratory. It may be reported,
and it may be interesting, but it is reported under a heading that says
"Exploratory". This is not a weakness in a paper; unlabelled exploration is.

### P5 — Negative and null results ship
We commit now, in writing, before we know the answer: if H1 is not supported, the
paper reports that H1 is not supported. The `llm-society-sim` framework, the
metrics, and the finding itself are the contribution. Reframing a null result as a
positive one after the fact is the single most damaging thing we could do to this
project's credibility, and reviewers detect it.

> Note: SPEC-4 §6 Risk 3 currently proposes to reframe non-significance as "a
> discovery regarding model alignment convergence." That is acceptable *only* as
> honest post-hoc interpretation of a clearly-reported null result. It is not
> acceptable as a change to what was tested. See `DR-0004`.

### P6 — Every run is reproducible from the repository alone
A run is only real if `run_id`, config hash, git commit, RNG seeds, model
identifiers *with provider-reported version strings*, timestamps, and prompt
template hashes are all recorded with the output. If we cannot re-derive a figure
from the repository six months from now, the figure does not go in the paper.

### P7 — Append-only history
`logs/` is append-only. Correct an earlier entry with a new dated entry that
supersedes it. Never silently edit or delete. The value of a lab notebook is that
it records what we believed at the time, including when we were wrong.

### P8 — One task, one artefact, one owner, one done-condition
Work that is not attached to a named deliverable with a written definition of done
does not get started. See SOP-010 §4.

### P9 — Deadline pressure never changes method, only scope
When time runs short we cut *scope* — fewer facts, fewer topologies, fewer
conditions — and we say so in the paper. We do not cut seeds, drop the
preregistration, weaken the correction, or quietly widen alpha. Scope reduction is
a limitation. Method reduction is misconduct.

---

## 3. SOP index

| ID | Title | Governs |
|---|---|---|
| SOP-000 | Master Research Operating Procedure | Everything |
| SOP-010 | Documentation & Logging | How work is recorded |
| SOP-020 | Literature Management | Finding, reading, citing, tracking prior art |
| SOP-030 | Experimental Design & Preregistration | Hypotheses, design, freezing the protocol |
| SOP-040 | Code & Reproducibility | Repo hygiene, environments, determinism |
| SOP-050 | Data Management | Trajectories, schemas, provenance, retention |
| SOP-060 | Analysis & Statistics | Tests, assumptions, corrections, reporting |
| SOP-070 | Writing & Submission | Paper, arXiv, workshop, release |
| SOP-080 | Research Integrity & AI Assistance | Authorship, disclosure, human subjects, ToS |

---

## 4. Repository map

```
.
├── README.md                  Entry point and current project status
├── CLAUDE.md                  Operating rules for AI-assisted sessions in this repo
├── docs/
│   ├── 00-governance/         SOPs. This directory. Read before working.
│   ├── 01-specifications/     v1.0 source documents. READ-ONLY.
│   │   └── source-docx/       Original .docx files as received
│   ├── 02-literature/         Prior art, reading notes, references.bib
│   ├── 03-design/             Amendments, preregistration, protocol v2+
│   ├── 04-analysis/           Analysis plans, notebooks, statistical output
│   └── 05-paper/              LaTeX source, figures, submission artefacts
├── logs/
│   ├── RESEARCH-LOG.md        Append-only dated session log
│   ├── DECISION-REGISTER.md   Numbered decision records (DR-xxxx)
│   ├── OPEN-QUESTIONS.md      Numbered open questions (OQ-xxxx)
│   ├── RISK-REGISTER.md       Numbered risks (RK-xxxx)
│   └── CHANGELOG.md           Repository-level changes
├── meta/templates/            Templates for the record types above
├── src/                       llm_society_sim package (Phase 1)
├── configs/                   Versioned experiment configurations
├── experiments/               Per-experiment directories (EXP-xxx)
├── data/                      Raw and derived data (see SOP-050)
└── results/                   Figures, tables, statistical output
```

---

## 5. Identifier scheme

Everything referenceable gets a stable ID. Never reuse or renumber.

| Prefix | Meaning | Lives in |
|---|---|---|
| `SOP-xxx` | Standard operating procedure | `docs/00-governance/` |
| `SPEC-n` | v1.0 source specification | `docs/01-specifications/` |
| `AMD-xxxx` | Amendment to a specification | `docs/03-design/` |
| `DR-xxxx` | Decision record | `logs/DECISION-REGISTER.md` |
| `OQ-xxxx` | Open question | `logs/OPEN-QUESTIONS.md` |
| `RK-xxxx` | Risk | `logs/RISK-REGISTER.md` |
| `H1..Hn` | Formal hypothesis | Preregistration |
| `EXP-xxx` | Experiment | `experiments/` |
| `RUN-<hash>` | Single simulation run | `data/` |
| `LIT-xxxx` | Literature note | `docs/02-literature/notes/` |

Cross-reference liberally. A decision record that does not cite the open question
it closes, or the evidence it rests on, is not finished.

---

## 6. Phase gates

The project does not advance to the next phase until the gate is signed off in
`logs/RESEARCH-LOG.md`. Gates exist to stop us spending compute on a design that
has a known hole in it.

| Gate | Cannot start until | Evidence required |
|---|---|---|
| **G0 → Foundation complete** | SOPs written, specs converted, logs initialised | This SOP set exists |
| **G1 → Design frozen** | Prior-art review complete; novelty position stated; every P0 open question closed; construct validity of the belief metric resolved | `docs/02-literature/PRIOR-ART-REVIEW.md`, `docs/03-design/PREREGISTRATION.md` |
| **G2 → Pilot passed** | Engine runs end-to-end; belief metric validated against a held-out signal; power analysis says the design can detect the effect | `EXP-000` pilot report |
| **G3 → Matrix launched** | Preregistration timestamped and immutable; cost and rate-limit budget verified empirically, not estimated | Frozen prereg + budget verification note |
| **G4 → Analysis complete** | All preregistered analyses run; assumptions checked; corrections applied | `docs/04-analysis/` |
| **G5 → Submission** | Paper reproduces every number from the repository; limitations section written; code released | Submission checklist |

**The single most important gate is G1.** Almost every avoidable way this project
can fail is decided before a single simulation runs.

---

## 7. Amending this SOP

1. Open an entry in `logs/OPEN-QUESTIONS.md` stating the problem.
2. Write a decision record in `logs/DECISION-REGISTER.md` with: context, options
   considered, decision, consequences, and who decided.
3. Edit the SOP, bump its `version`, and note the `DR-xxxx` in its changelog section.
4. Log the amendment in `logs/RESEARCH-LOG.md`.

Never amend an SOP silently. The rule and the reason it changed must travel together.

---

## Changelog

| Version | Date | Change | DR |
|---|---|---|---|
| 1.0 | 2026-08-07 | Initial issue | DR-0001 |
