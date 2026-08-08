# Working in this repository

Operating rules for AI-assisted sessions. Read this and `docs/00-governance/SOP-000-master-research-operating-procedure.md`
before doing anything else.

This is an active research project, not a software project that happens to be about
research. The difference matters: here, **being fast is worth much less than being
correct and traceable.** A wrong number that reaches a preprint costs far more than a
slow session.

---

## Start of every session

1. Read the last entry in `logs/RESEARCH-LOG.md`.
2. Read the P0/P1 rows of `logs/OPEN-QUESTIONS.md`.
3. Check which phase gate is current (`README.md` → Status).

## End of every session

Append a research-log entry using `meta/templates/log-entry.md`. Name the model.
No exceptions — a session with no log entry did not happen.

---

## Hard rules

**Never edit `docs/01-specifications/`.** Those files are the source of record (DR-0002).
Corrections are amendments in `docs/03-design/`, backed by a decision record.

**Never edit past entries in `logs/`.** Append. Supersede. Never rewrite history.

**Never invent a citation.** Every reference must be verified against the actual source
before it enters `references.bib` or any document. AI-suggested citations are
`[UNVERIFIED]` until a human has opened the paper and located the claim. This is the
fastest way to destroy a first paper's credibility and it is entirely preventable.

**Never state a number without its provenance.** Any number that came from a computation
carries a pointer to the script or notebook that produced it. Numbers are not typed by
hand into documents.

**Never soften a finding to fit the narrative.** If something you find makes the project
look harder, that is the most valuable thing you can report. Say it plainly, in the
"Found" section of the log, and raise an `OQ-xxxx`.

**Tag uncertainty explicitly.** Use `[UNVERIFIED]` for anything not yet checked. Do not
write around uncertainty with confident prose.

---

## Making changes

| Change | Required record |
|---|---|
| Design, metric, hypothesis, or analysis | `DR-xxxx` **before** implementing |
| Deviation from a v1.0 spec | `DR-xxxx` + amendment in `docs/03-design/` |
| New unresolved question | `OQ-xxxx` with a priority |
| New risk | `RK-xxxx` with a **trigger** |
| Paper read (Tier A/B) | `LIT-xxxx` note |
| Experiment | Experiment card before launch, results after |

Cross-reference by ID. A decision record that does not cite the question it closes or the
evidence it rests on is not finished.

---

## Code (from Phase 1)

- Package under `src/llm_society_sim/`. Experiment logic must be importable and testable.
- Config in versioned files under `configs/`, never as literals or ad-hoc CLI flags for
  confirmatory runs.
- Every module docstring names the specification section it implements.
- Tests required for anything that produces a number in the paper: topology builders, the
  memory operator, the belief metric, the metric computations, and the analysis functions.
- The analysis pipeline is tested against **synthetic data with a planted effect** before
  it touches real data. This is the main guard against a pipeline bug that manufactures
  significance.
- Analysis reads from logged data only. Never re-hit an API to regenerate an analysis —
  provider outputs are not reproducible, and the logged trajectory dataset is the durable
  artefact.
- Never commit secrets. `.env` is gitignored; `.env.example` lists variable names only.

---

## Statistics — the traps specific to this project

These have already bitten the v1.0 design. Watch for them in anything you write or review:

- **Pseudoreplication.** Agents are nested in runs and talk to each other. They are not
  independent observations. The unit of analysis must be stated for every test, and
  run-level outcomes are analysed at the run level.
- **Test–claim mismatch.** A K–S test detects distributional difference, not bimodality.
  A regression on observational data does not license a causal claim. Match the test to
  the claim, or change the claim.
- **Bounded outcomes.** TRR/MP/BPI live in [0,1] and will be non-normal near the
  boundaries. Plan the alternative (beta regression, logit transform, permutation test)
  in advance, not after seeing that ANOVA assumptions failed.
- **Null ≠ no effect.** `p > α` is not evidence of absence. Use equivalence testing
  against a preregistered smallest effect of interest.
- **Free parameters on the dependent variable.** Anything like the dual-probe α must be
  fixed a priori or swept as a documented sensitivity analysis. Never chosen after
  seeing outcomes.

---

## Tone for documents in this repo

Write for a reviewer who is smart, busy, and looking for the weak point. Be concrete.
Prefer a number to an adjective. State limitations before someone else does. Never write
"proves"; write "provides evidence that".
