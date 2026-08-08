---
id: SOP-030
title: Experimental Design & Preregistration
status: ACTIVE
version: 1.0
created: 2026-08-07
---

# SOP-030 — Experimental Design & Preregistration

Governs how experiments are designed and frozen. Derives from SOP-000 P3, P4, P9.

---

## 1. Construct validity comes first

Before any design question — how many agents, how many seeds, which topology — one
question must be answered:

> **Does our dependent variable measure what we say it measures?**

The dependent variable here is agent belief `B_i^(t)(s)`. Everything in this project
— TRR, MP, BPI, R₀, ρ\*, all four hypotheses — is a function of it. If the belief
metric is invalid, 405 runs of beautiful engineering produce nothing.

**Mandatory before G1:** a written construct-validity argument for the belief metric
covering at minimum:

1. **Convergent validity** — does the metric agree with an independent measure of the
   same construct (human judgement of the agent's stated position; the agent's own
   behaviour in downstream tasks)?
2. **Robustness to nuisance factors** — how much does the metric move under
   paraphrase, option ordering ("True or False?" vs "False or True?"), few-shot
   framing, and temperature, holding context constant? Quantify it; report it.
3. **Comparability across model families** — a probability of 0.7 from model A and
   0.7 from model B must be interpretable on the same scale, or every
   heterogeneous-vs-homogeneous comparison is confounded by differential calibration.
4. **Provider feasibility** — the metric must be *computable* for every model in
   every condition. Any component of the metric unavailable for some agents (e.g.
   token logprobs behind a closed API) makes the metric non-comparable across
   conditions unless explicitly handled and justified.
5. **Free-parameter justification** — any weighting constant (e.g. α mixing logit and
   verbal probes) must be either derived, fixed a priori with a stated rationale, or
   swept as a documented sensitivity analysis. It may **not** be tuned on
   confirmatory data.

Record as `docs/03-design/CONSTRUCT-VALIDITY-BELIEF-METRIC.md`.

---

## 2. Hypothesis specification

Every hypothesis in the preregistration must state all six:

| Field | Requirement |
|---|---|
| **Claim** | In plain English, one sentence |
| **Formal statement** | The inequality or model being tested |
| **Operationalisation** | Exact variables, exact formulae, exact units |
| **Test** | The statistical procedure, including assumptions to be checked and what happens if they fail |
| **Decision rule** | The threshold *and* the corrected alpha, decided in advance |
| **Falsifier** | What observation would count as the hypothesis being wrong |

A hypothesis with no falsifier is not a hypothesis. Write the falsifier before you
have the data; it is remarkably hard to write afterwards.

---

## 3. Unit of analysis and independence

This is the most common fatal statistics error in multi-agent simulation papers, and
the current design is exposed to it.

Agents are **nested within runs**. Agents in the same run share a topology, a fact, a
seed, and — critically — they talk to each other. Their outcomes are *not*
independent. Treating 20 agents × 405 runs as 8,100 independent observations inflates
the effective sample size by an order of magnitude and produces p-values that mean
nothing.

**Rules:**

- The unit of randomisation is the **run**. State the unit of analysis explicitly for
  every hypothesis.
- Run-level outcomes (TRR, MP, BPI at time T) are analysed at the run level. n = number
  of runs in the relevant cells, not number of agents.
- Agent-level or message-level analyses (H3) **must** use a model with a random effect
  for run — and, where models differ, for model family — or cluster-robust standard
  errors clustered at the run.
- The degrees of freedom reported in the paper must correspond to the unit of analysis.
  Reviewers check this.

---

## 4. Replication and power

- **Seeds are not free parameters.** The number of independent replications per cell
  is fixed in the preregistration and justified by a power analysis, not by
  convenience. Three seeds per cell is a starting proposal, not a justification.
- **Power analysis is mandatory before G3.** Required inputs: the smallest effect size
  that would be scientifically meaningful (decided by us, in advance, and written
  down), the observed between-run variance from the pilot, the alpha after correction,
  and target power ≥ 0.80. If the design is underpowered, the honest options are:
  increase replications, reduce the number of cells, or preregister the study as
  exploratory. Running it anyway and reporting p-values is not one of the options.
- **Variance sources to separate:** sampling temperature, prompt seed, topology
  realisation, and agent-to-node assignment are four different randomisations. Decide
  which are held fixed and which are resampled per replication, and record it. Reusing
  a single graph realisation across all "seeds" means topology variance is not
  estimated at all.

---

## 5. Confounds to control by design

For the central H1 comparison (heterogeneous vs homogeneous), the following are
confounded with the manipulation unless deliberately controlled. Each needs a
documented position in the design:

| Confound | Why it matters |
|---|---|
| **Aggregate capability** | A mixed pool may simply be *more capable on average* than the homogeneous pool. Then "diversity helps" reduces to "better models help." Requires a capability-matched control. |
| **Calibration differences** | Different families produce differently-calibrated probabilities; a belief metric difference may be a scale artefact. |
| **Response length / verbosity** | Longer, more assertive messages may drive persuasion independent of model identity. |
| **Refusal and safety-training differences** | Some families refuse to argue for false claims more often, which is a confound *and* an interesting finding — but it must be measured, not absorbed. |
| **Provider-side variation** | Serving stack, quantisation, and silent model updates differ across providers and over time. Record version strings; re-check at the end of the matrix. |
| **Prompt-template fit** | A single template may suit one family better than another. Counterbalance or measure. |

For every confound the preregistration says one of: *controlled by X*, *measured and
reported as a covariate*, or *acknowledged as a limitation*. Silence is not an option.

---

## 6. Preregistration and freezing

`docs/03-design/PREREGISTRATION.md` is written before the confirmatory matrix runs.
It contains: hypotheses (§2), metrics with formulae, design and cells, unit of
analysis (§3), replications and power (§4), confound handling (§5), exclusion rules,
stopping rule, multiple-comparison correction, and the analysis code path for each
test.

**Freezing procedure:**

1. Complete the document; set `status: FROZEN` and the freeze date.
2. Compute and record its SHA-256 hash in `logs/RESEARCH-LOG.md`.
3. Commit. Tag the commit `prereg-frozen`.
4. Optionally deposit publicly (OSF or an arXiv-timestamped appendix) — a public
   timestamp is worth a great deal at review time and costs nothing.

After freezing, changes are **amendments only**: a dated `AMD-xxxx` stating what
changed, why, and — crucially — whether any confirmatory data had already been seen
at the time of the change. Amendments made after seeing data are disclosed as such in
the paper. This is normal, respectable practice. Hiding them is not.

---

## 7. Pilot before matrix

`EXP-000` (pilot) precedes G2 and must produce, at minimum:

- End-to-end engine execution on a reduced cell set;
- Empirical between-run variance for each primary metric, to feed the power analysis;
- Empirical per-call latency, token counts, failure rate, and cost per run, to feed
  the budget verification at G3;
- Belief-metric robustness numbers per §1.2;
- At least one deliberate **negative control**: a condition where the effect must be
  absent (e.g. no misinformation injected, or a disconnected graph `G_empty`). If the
  pipeline reports an effect in the negative control, the pipeline is broken.

A pilot that only demonstrates "it runs" has not done its job.

---

## Changelog

| Version | Date | Change | DR |
|---|---|---|---|
| 1.0 | 2026-08-07 | Initial issue | DR-0001 |
