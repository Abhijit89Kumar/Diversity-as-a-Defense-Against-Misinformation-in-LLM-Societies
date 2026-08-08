---
id: SOP-050
title: Data Management
status: ACTIVE
version: 1.0
created: 2026-08-07
---

# SOP-050 — Data Management

Governs simulation data, derived datasets, and human-annotation data.

---

## 1. Data tiers

| Tier | Location | Mutability | Backed up | Released |
|---|---|---|---|---|
| **Raw** — every API request/response, verbatim | `data/raw/<run_id>/` | **Immutable.** Write once, never edit. | Yes | Yes (after PII review) |
| **Interim** — parsed trajectories, belief matrices | `data/interim/` | Regenerable from raw | No | No |
| **Processed** — analysis-ready tables | `data/processed/` | Regenerable from interim | No | Yes |
| **Human annotation** | `data/annotations/` | Immutable | Yes | Yes, de-identified |
| **Results** — figures, tables, model output | `results/` | Regenerable | No | Yes |

The rule that matters: **raw is immutable and everything else is derivable.** If a
processing bug is found, fix the code and regenerate — never patch a derived file by
hand. A hand-patched derived file is undetectable six weeks later.

## 2. Raw capture

Capture more than you think you need. Storage is free; re-running 40,500 calls is not.

Per API call, log: `run_id`, agent, round, provider, model_id, any version string the
provider returns, the **full resolved prompt** (system + messages), the full response,
finish reason, token counts, latency, HTTP status, attempt number, UTC timestamp, and
any logprobs returned.

Per round, log the full context window of every agent *as sent*. Reconstructing
context after the fact from a memory-operator implementation that has since changed is
not possible, and this is exactly the sort of thing a reviewer asks about.

## 3. Schemas

- Every dataset has a written schema in `docs/03-design/schemas/` with field name,
  type, units, allowed range, and meaning.
- Schemas are versioned. A schema change is a `DR-xxxx`.
- Prefer JSONL (one record per line, append-safe, streamable) over one large JSON
  document for trajectory logs. The v1.0 spec's single `results_trajectory.json` is
  fine per run but should be complemented by an append-only JSONL call log.
- Validate on write. A malformed record discovered at analysis time is a lost run.

## 4. Storage and backup

- Raw data is backed up to a second location before analysis begins. "It's on my
  laptop" is not a backup. Cloud storage or an external drive, with the location and
  date recorded in `logs/RESEARCH-LOG.md`.
- Estimate size early: ~40,500 calls × (prompt + completion), plus per-round context
  snapshots, is plausibly single-digit GB. Confirm from the pilot's actuals and record
  it — running out of disk mid-matrix is an avoidable and expensive failure.
- Git tracks code and documents. Data over ~10 MB goes to a release artefact,
  Hugging Face dataset, or Zenodo, referenced by URL and checksum from the repo.

## 5. Provenance

Every derived artefact records what produced it: input file checksums, script path,
git commit, parameters, timestamp. Figures embed (or ship alongside) the ID of the
analysis run that produced them. When the paper says "Figure 3", there is exactly one
answer to "which code and which data made this?".

## 6. Human-annotation data

Handled under SOP-080 §2 for ethics. Data rules:

- No annotator identifiers in released data. Store the platform participant ID
  separately from responses, in a file that is never released, and only for as long
  as payment reconciliation requires.
- Record the exact instructions, interface, qualification criteria, pay rate, and
  median completion time alongside the responses. Reviewers ask about pay rate.
- Store per-annotator per-item raw judgements, not just aggregates. Fleiss' κ cannot
  be recomputed from aggregates, and reviewers will want the disagreement structure.
- Preregister the exclusion rule for low-quality annotators (attention checks,
  completion time) *before* seeing the correlation with our metric. Excluding
  annotators after seeing that they hurt the correlation is p-hacking.

## 7. Retention and release

- Retain raw data for at least 5 years past publication.
- Release: raw call logs (after a scan for anything sensitive), processed tables,
  annotation data (de-identified), and all analysis code, under the same MIT/CC-BY
  arrangement as the code.
- Publish a `DATASET-CARD.md`: what it contains, how it was generated, known
  limitations, and what it should *not* be used for.

---

## Changelog

| Version | Date | Change | DR |
|---|---|---|---|
| 1.0 | 2026-08-07 | Initial issue | DR-0001 |
