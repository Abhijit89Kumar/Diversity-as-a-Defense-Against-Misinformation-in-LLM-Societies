---
id: SOP-070
title: Writing & Submission
status: ACTIVE
version: 1.0
created: 2026-08-07
---

# SOP-070 — Writing & Submission

Governs the paper, the preprint, the code release, and the demo.

---

## 1. Write the paper early, not last

The paper skeleton — title, abstract, contribution bullets, figure list, and the
"Limitations" section — is drafted at **G1**, before the matrix runs. Reasons:

- Writing the contribution bullets is the fastest way to discover you do not have one.
- Writing the figure list forces the analysis plan to be concrete.
- Writing Limitations before you have results means writing them honestly.

The abstract drafted at G1 will contain placeholders for numbers. That is correct.
What it must not contain is a placeholder for the *finding* — that goes in as "we find
X or we find not-X", and both branches must be publishable (SOP-000 P5).

## 2. Structure (workshop paper, 4–8 pages)

1. **Abstract** — problem, what we built, what we found, why it matters. Numbers in.
2. **Introduction** — the shift to agent-to-agent information flow; the gap; our
   contribution as an explicit numbered list.
3. **Related Work** — organised by the Prior Art Matrix. Each Tier-A competitor named
   and positioned against directly. Do not hide close prior work; reviewers find it,
   and finding it themselves is much worse than reading your honest comparison.
4. **Formalism** — graph, memory operator, belief metric, diversity measure.
5. **Method** — simulation protocol, populations, topologies, fact suite, injection.
6. **Belief-metric validation** — its own section. This is a load-bearing methodological
   contribution and hiding it in an appendix undersells it *and* invites scepticism.
7. **Experiments & Results** — per hypothesis, effect sizes first.
8. **Limitations** — see §4.
9. **Broader impact / responsible disclosure** — see SOP-080 §4.
10. **Conclusion & Future Work**

## 3. Claims discipline

Before submission, run a **claims audit**: extract every declarative claim from the
abstract, introduction, and conclusion into a table, and for each one record the
figure, table, or statistical test that supports it. Any claim without support is cut
or softened. This takes two hours and is the highest-return two hours in the writing
phase.

Language rules:
- Never "proves". Use "provides evidence that", "is consistent with".
- Never generalise beyond the models, sizes, tasks, and topologies actually tested.
  We test small open-weight models on 15 factual claims in 20-node graphs over 5
  rounds. That is the scope of every claim.
- Simulation results are about *simulated* agents. Claims about real deployed
  multi-agent systems are hypotheses, and must be marked as such.

## 4. Limitations — written honestly, in the paper

A workshop reviewer's first instinct on a simulation paper is to list its limitations.
Getting there first, in specific and quantified terms, converts an attack into a
demonstration of rigour. At minimum, address:

- Scale: N = 20 agents, T = 5 rounds, 15 facts. Why these, and what generalises.
- Model scope: which families, which sizes, and that closed frontier models are absent.
- The belief-metric construct: what it does and does not capture, with the robustness
  numbers.
- Prompt sensitivity: how much results move across the prompt seeds.
- The synthetic nature of injected misinformation vs real-world misinformation.
- Provider non-determinism and the possibility of silent model updates mid-matrix.
- Statistical power for any test that was underpowered — stated, not hidden.

## 5. Reproducibility package

Submitted alongside the paper: code at a tagged commit with an archived DOI, the
processed dataset, the frozen preregistration, the analysis scripts, and a README
whose quickstart reproduces one headline figure. Fill in the venue's reproducibility
checklist honestly — the checklist is read.

## 6. Preprint and venue sequencing

- **Check the target venue's preprint policy before posting.** Most ML venues permit
  arXiv preprints; some tracks and some ACL venues have anonymity periods with
  specific windows. Getting this wrong can mean desk rejection. Verify per venue, at
  the time of submission, and record the check in `logs/RESEARCH-LOG.md`.
- arXiv `cs.MA` primary, cross-list `cs.CL`, `cs.AI`, `cs.SI`. **First-time arXiv
  submitters may require endorsement in some categories — check and, if needed, secure
  an endorser weeks in advance, not the night before.** Track as a risk.
- Version the arXiv posting; do not silently replace. v1 is the submitted version.

## 7. Authorship

Per SPEC-4, equal contribution and shared ownership. Record the contribution split
using CRediT taxonomy roles in the paper. Agree the author order in writing, in a
`DR-xxxx`, **before** submission — not after results are in. This is standard practice
and prevents the most common collaboration failure.

## 8. The demo

The interactive dashboard is a portfolio asset, not a scientific claim. It must:
- be clearly labelled as a visualisation of logged simulation data;
- never display a number that disagrees with the paper;
- be built *after* G4, from processed data, so it cannot consume time that the
  analysis needs.

## 9. Submission checklist (G5)

- [ ] Every number in the paper regenerated from the repository on a clean machine
- [ ] Claims audit complete; every abstract/intro/conclusion claim traced to evidence
- [ ] Every citation verified against the actual source (SOP-020 §4)
- [ ] Limitations section reviewed by someone who did not write it
- [ ] Preregistration deviations disclosed
- [ ] Code released, DOI archived, LICENSE and CITATION.cff present
- [ ] Venue formatting, page limit, and anonymity requirements verified
- [ ] Preprint policy for the specific venue verified and recorded
- [ ] Broader-impact and responsible-disclosure statement written
- [ ] Author order and CRediT roles agreed in a DR

---

## Changelog

| Version | Date | Change | DR |
|---|---|---|---|
| 1.0 | 2026-08-07 | Initial issue | DR-0001 |
