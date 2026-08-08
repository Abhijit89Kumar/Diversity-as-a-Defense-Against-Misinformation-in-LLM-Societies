---
id: SOP-080
title: Research Integrity & AI Assistance
status: ACTIVE
version: 1.0
created: 2026-08-07
---

# SOP-080 — Research Integrity & AI Assistance

Governs conduct. This SOP is the one that protects the people involved, not just the
paper.

---

## 1. Integrity commitments

We commit, in advance:

- **We report what we find.** Including nulls, including results that undercut the
  framing, including bugs discovered after a result was shared.
- **We do not tune the analysis to the answer.** Preregistration + planted-effect
  testing of the analysis code (SOP-060 §8) exist to make this checkable.
- **We disclose deviations.** Every departure from the preregistration is stated in
  the paper with its date and whether data had been seen.
- **We correct in public.** If an error is found after posting a preprint, we post a
  corrected version and say what changed. A corrected v2 costs a little pride; a
  discovered-by-someone-else error costs the paper.
- **We do not cite what we have not read** (SOP-020 §4).
- **We do not oversell.** The scope of the claim equals the scope of the experiment.

## 2. Human-subjects considerations (annotation study)

The plan involves paying human annotators to rate agent-generated text. Before any
data is collected:

- **Ethics review:** determine whether the institution(s) involved require IRB/ethics
  approval or an exemption determination for paid crowdsourced annotation. If either
  co-researcher is affiliated with a university, ask — do not assume it is exempt
  because the data is text. Record the determination. Retro-fitting approval is not
  possible, and some venues ask.
- **Fair pay:** annotators are paid at or above the platform's minimum and at or above
  a defensible hourly floor for their jurisdiction. Compute pay **per hour** from
  measured median task time, not per item. Verify the platform's current minimum-pay
  policy at the time of launch — the per-judgement figures in SPEC-3/SPEC-4 ($0.30 and
  $0.25) predate verification and are internally inconsistent; treat both as
  provisional. Record the actual realised hourly rate and report it in the paper.
- **Informed consent:** a consent screen stating who is running the study, what the
  data will be used for, that responses will be released publicly in de-identified
  form, expected duration, and contact details.
- **Content warning:** annotators will read confidently-stated scientific falsehoods.
  The instructions must say so, and must debrief at the end with the correct facts.
  This costs one screen and is the right thing to do.
- **Data minimisation and de-identification:** SOP-050 §6.

## 3. AI assistance — use and disclosure

AI assistance (including this one) is used in this project. That is fine and
increasingly normal. The rules:

**Permitted, with disclosure:** literature search support, code drafting, refactoring,
test writing, documentation drafting, editing and proofreading, analysis scaffolding,
brainstorming designs and counterarguments.

**Requires human verification before it counts as done:**
- Any citation or factual claim (SOP-020 §4). Treat AI-supplied references as false
  until opened.
- Any code that computes a number that reaches the paper.
- Any statistical reasoning.
- Any text entering the specification, preregistration, or paper.

**Not permitted:**
- Fabricating, extending, or "smoothing" data or results.
- Generating a related-work section without reading the works.
- Presenting AI-generated text as if independently authored where the venue requires
  disclosure.

**Disclosure:** check the target venue's AI-use policy at submission time and comply.
Maintain a short AI-use statement in `docs/05-paper/AI-USE-STATEMENT.md` describing
what AI was used for, updated as the project proceeds. Every AI-assisted session is
logged in `RESEARCH-LOG.md` naming the model (SOP-010 §5).

**AI cannot be an author.** Responsibility for every claim rests with the human
authors.

## 4. Dual-use and responsible disclosure

This project builds a tool that **optimises the spread of misinformation through
networks of AI agents**, and characterises which topologies and populations are most
vulnerable. That is genuinely dual-use, and it needs to be handled deliberately rather
than discovered by a reviewer.

Required before release:

- A **Broader Impact** section that states the dual-use tension plainly and argues why
  publication is net-positive (defenders need measurement; the attack surface is
  already reachable by anyone who can call an API; the framework's primary output is a
  *defence* finding).
- A judgement, recorded as a `DR-xxxx`, on what to release: the framework and the
  benchmark facts almost certainly yes; a tuned "most effective persuasion prompt"
  ranking deserves an explicit decision rather than a default.
- The 15 diagnostic facts are deliberately absurd, verifiable falsehoods about physics
  and arithmetic — not politically or socially charged misinformation. **Keep it that
  way.** It is the right scientific choice (clean ground truth, no annotator harm) and
  it removes an entire category of ethical objection. If a reviewer asks for
  real-world misinformation, that is Future Work, with an ethics review attached.
- No content in the repository should function as a ready-to-use disinformation kit
  targeting real people, organisations, or live public controversies.

## 5. Collaboration conduct

- Decisions that affect both researchers are recorded as `DR-xxxx` with both named.
- Author order and CRediT roles agreed in writing before submission (SOP-070 §7).
- Either researcher may block a G-gate on an integrity concern. Raising one is never
  penalised, and the concern is recorded even if it is resolved as unfounded.
- Budget spend is logged the day it happens, by whoever spent it.

---

## Changelog

| Version | Date | Change | DR |
|---|---|---|---|
| 1.0 | 2026-08-07 | Initial issue | DR-0001 |
