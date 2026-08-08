---
id: SOP-060
title: Analysis & Statistics
status: ACTIVE
version: 1.0
created: 2026-08-07
---

# SOP-060 — Analysis & Statistics

Governs statistical practice. Derives from SOP-000 P3, P4.

---

## 1. The order of operations

Analysis follows this order, without exception:

1. **Negative controls and sanity checks** — before looking at any hypothesis test.
   Does the no-injection condition show no infection? Does an isolated-agent baseline
   (`G_empty`) reproduce known model accuracy on the fact suite? Are there runs with
   impossible values?
2. **Descriptive statistics and plots** — distributions of every primary metric per
   cell, with the raw data visible (strip/violin, not bar charts of means).
3. **Assumption checks** — for each planned test, stated in the preregistration.
4. **Preregistered confirmatory tests**, with corrections applied.
5. **Exploratory analyses**, clearly labelled.

Looking at step 4 before steps 1–3 is how people end up defending an artefact.

## 2. Assumption checking is mandatory and pre-planned

For every preregistered test, the preregistration names the assumptions, how they are
checked, and **what we do if they fail** — decided in advance, so the fallback is not
chosen based on which gives a better p-value.

| Planned test | Key assumptions | If violated |
|---|---|---|
| Two-way ANOVA (H1) | Independence of observations; approximate normality of residuals; homogeneity of variance | TRR is a bounded proportion in [0,1] and will not be normal near ceiling/floor. Preferred alternatives stated a priori: beta regression, logit-transformed linear model, or a permutation test on the same design. |
| Two-sample K–S (H2) | Continuous distributions; **independent observations** | Belief values within a run are not independent. Either aggregate to one value per run before comparing distributions, or use a run-level permutation test. Naively pooling 8,100 agent beliefs will produce a vanishingly small p-value that means nothing. |
| Linear mixed-effects (H3) | Correct random-effects structure; linearity; residual normality | Specify the maximal justified random-effects structure in advance (random intercepts for run **and** receiving-agent model family; random slopes where identifiable). Report the fitting procedure and any simplification actually needed for convergence. |

**On H2 specifically:** the hypothesis is about *bimodality*, but K–S tests whether two
distributions differ at all — it does not test bimodality. A significant K–S result is
consistent with H2 but does not establish it. Either add a direct bimodality measure
(e.g. Hartigan's dip test, a bimodality coefficient, or a two-component mixture fit
compared to one component) or restate the hypothesis to match the test. Test–claim
mismatch is a reviewer magnet.

**On H3 specifically:** the hypothesis is causal ("certainty *causes* belief shift"),
but a regression on observational simulation data is correlational. Certainty is
confounded with content quality, message length, and which model produced it. To
support a causal claim, run a **manipulation**: hold content fixed and vary stated
certainty via the prompt. Otherwise the claim must be stated as association.

## 3. Multiple comparisons

Four hypotheses, three fact tiers, three topologies, three populations, and multiple
metrics generate a large family of tests. The preregistration must define:

- The **family** of tests for each hypothesis.
- The correction — Holm–Bonferroni for a small confirmatory family, Benjamini–Hochberg
  FDR for larger exploratory families. State which, in advance.
- The corrected threshold. Note that the SPEC-1 choice of α = 0.01 is *not itself* a
  correction; it is a stricter uncorrected threshold. Correction is still required.

Exploratory tests are reported with uncorrected p-values **explicitly labelled as
exploratory and not inferential**.

## 4. Effect sizes and uncertainty, not just p-values

- Every reported test carries an effect size with a confidence interval: η²ₚ or ω² for
  ANOVA, Cohen's d or a difference in proportions with CI for pairwise contrasts,
  standardised β with CI for regression coefficients.
- **The headline result is an effect size, not a p-value.** "Heterogeneous populations
  retained 23% more truth (95% CI [14, 32])" is a finding. "p < 0.01" is not.
- Prefer estimation and interval reporting over binary significance language
  throughout. Reviewers at ML venues increasingly expect this.
- Where a null result is claimed, do not infer it from p > α. Use an equivalence test
  (TOST) against a preregistered smallest effect size of interest, or report a Bayes
  factor. "No significant difference" is not evidence of no difference.

## 5. Bootstrapping and permutation

Given non-normal bounded metrics, small cell counts, and clustered data, resampling
methods are often the most defensible choice:

- **Cluster bootstrap** (resample runs, not agents) for confidence intervals on
  run-level metrics.
- **Permutation tests** that shuffle the condition label at the run level for
  hypothesis tests. These are robust to distributional assumptions and easy for a
  reviewer to trust.
- Fix and record the resampling seed and the number of resamples (≥ 10,000 for
  reported p-values).

## 6. Reporting standard

Every statistical claim in the paper reports: test used, unit of analysis, n at that
unit, test statistic, degrees of freedom, p-value, effect size with CI, and whether
it was preregistered. A results table with only means and asterisks does not meet the
standard.

## 7. Figures

- Show the data. Individual runs as points behind any summary.
- Uncertainty on every estimate.
- No dual y-axes. No truncated axes without an explicit break marker.
- Colour-blind-safe palettes; readable in greyscale; every figure legible at
  single-column width.
- Each figure is produced by a script in `results/`, from processed data, with no
  manual steps. Figure captions state n and the unit of analysis.

## 8. Analysis code discipline

- Analysis lives in scripts or notebooks that run top-to-bottom on a clean kernel.
- The preregistered analysis is written and tested **against synthetic data with a
  planted effect** before the real data exists (SOP-040 §3). This is the strongest
  practical guard against analysis-after-the-fact.
- No number reaches the paper by being typed in by hand. Generate tables
  programmatically.

---

## Changelog

| Version | Date | Change | DR |
|---|---|---|---|
| 1.0 | 2026-08-07 | Initial issue | DR-0001 |
