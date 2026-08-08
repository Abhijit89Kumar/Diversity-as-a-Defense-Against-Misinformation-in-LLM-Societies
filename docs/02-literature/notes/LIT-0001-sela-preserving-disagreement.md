---
id: LIT-0001
citekey: sela2026preserving
tier: A
threat: 4
read_by: AI-assisted (Claude Opus 5) — FULL TEXT READ; requires human confirmation per SOP-020 §4
read_on: 2026-08-07
---

# LIT-0001 — Preserving Disagreement: Architectural Heterogeneity and Coherence Validation in Multi-Agent Policy Simulation

**Full citation:** Sela, Ariel. "Preserving Disagreement: Architectural Heterogeneity and
Coherence Validation in Multi-Agent Policy Simulation." arXiv:2604.26561v1 [cs.MA],
29 April 2026. Preprint. CC BY 4.0.
**Link:** <https://arxiv.org/abs/2604.26561>
**Code:** none found.

> Read from the arXiv HTML full text (`/html/2604.26561v1`), extracted and parsed locally
> with MathML alttext preserved — not from a prose summary (SOP-020 §4.6). Metadata from the
> abs page `citation_*` meta tags. **A human must still confirm before citation.**

## One-sentence claim

Assigning a *different* 7–9B model to each value perspective substantially reduces artificial
consensus in normative policy deliberation, where — unlike in accuracy-oriented tasks —
convergence is a failure mode rather than a success criterion.

## Setup

| | |
|---|---|
| Agents / N | 7 evaluators (5 effective value perspectives; 3 share "Security Focus") |
| Models | **Qwen3-8B, Mistral-NeMo, Mistral-7B-Instruct-v0.3, Qwen2.5-Coder-7B, Dolphin3-8B, DeepSeek-R1-8B, Gemma2-9B** — all 7–9B, **locally hosted via Ollama on consumer hardware**. Plus one frontier API call (Claude Sonnet 4) for coherence validation. |
| Topology | None varied. Three-phase pipeline: structured debate → independent evaluation → coherence validation |
| Rounds | Multi-round debate phase; 120 deliberations total |
| Task | Two policy scenarios: child welfare intervention; urban housing. Chosen for structural contrast (dominant option vs genuinely competitive options) |
| Manipulation | (a) architectural heterogeneity vs homogeneous single-model baseline; (b) coherence validation on/off |
| DV | First-Choice Concentration (FCC); coherence score; "trustworthy tension rate" |
| Statistics | Significance tests with effect sizes (r); N=120 deliberations |

## Findings

- **Heterogeneity reduces artificial consensus, with large effects.** Child welfare
  70.9% → 46.1% (p < 0.001, r = 0.58); housing 46.0% → 22.9% (p < 0.001, r = 0.50).
- **Fidelity–diversity trade-off.** Coherence validation further reduces concentration on a
  dominant-option scenario (46.1% → 40.8%, p = 0.004) but *increases* it on a competitive one
  (22.9% → 26.6%, p = 0.96), by amplifying high-coherence evaluators who happen to cluster.
- **Two named causes of artificial consensus:** *shared inductive bias* ("the agents are
  fundamentally the same reasoner asked to wear different hats") and *debate capture*.
- **Profiling alignment anti-correlates with coherence** (r = −0.83, p = 0.079; r = −0.94,
  p = 0.019). Mistral-7B had the highest persona-vocabulary alignment and the *lowest*
  reasoning coherence; DeepSeek-R1-8B the reverse.
- **Trustworthy tension rate ≈ 50%** for this model class.
- **Negative results reported** from three failed Delphi designs.
- **FCC is discretely valued** at N=7, K=3 — only five possible values (14.3 / 35.7 / 57.1 /
  78.6 / 100%). Intermediate values are impossible. A cautionary note on small-N metrics.

## Threat to us — 4/5

Closest published execution of H1's *design*: scale-matched (7–9B) architectural
heterogeneity, significance-tested, with effect sizes. But it is **not** our experiment:

- DV is first-choice concentration in a values task with **no ground truth**; ours is truth
  retention under adversarial injection.
- **No misinformation is injected.** No adversary at all.
- No topology variation.
- Their cohorts are not accuracy-matched — they are *perspective*-matched, and the paper
  itself concedes coherence scores confound model capability with perspective–model fit.

> They did architectural heterogeneity in **normative** deliberation without an adversary.
> We do it in an **accuracy-oriented** setting **with** an adversary, at matched capability.
> Their own framework predicts these differ; nobody has tested the middle case.

## Gift to us — this paper reshaped the design

**1. The capitulation-cascade mechanism (§7.4).** The single most useful paragraph found in
the entire review:

> *"8B models exhibit binary rather than graded responses to counter-arguments: they either
> maintain their position entirely (including when asked to self-reflect) or capitulate
> entirely… The absence of a 'consider and reject' middle state… appears to be a robust
> characteristic of the 7–9B parameter range."*

> *"Any multi-agent architecture that exposes small-model agents to arguments from other
> agents risks inducing **capitulation cascades**, where the first agent to encounter a
> persuasive argument flips, creating a feedback loop. Architectural designs that preserve
> agent isolation during evaluation — as our system does — are necessary safeguards at this
> model scale."*

They name the mechanism, call it a hazard, and **design around it instead of studying it.**
That is our contribution restated in their words. It also forced our DV from a graded credence
to a discrete state with survival analysis (`OQ-0038`, AMD-0001 §8).

**2. Two citations we did not have**, both P0/P1:
- **Fang et al. (Springer, Nov 2025), "A-HMAD"** — *"heterogeneity does not reduce convergence
  in accuracy-oriented tasks."* The direct null for our regime → `OQ-0042`.
- **Huang et al. (OpenReview, 2025), "Debate or vote"** — debate is a *martingale* on belief in
  the correct answer, no expected gain over independent voting → `OQ-0043`.
- Also: **Li et al., arXiv:2509.05396** — weak models in heterogeneous debate can *degrade*
  outcomes. A competing explanation our capability matching must separate out.

**3. A validated model pool at our exact scale**, runnable on consumer hardware via Ollama —
directly reusable for DR-0005's self-hosted substrate, and it makes our results comparable to
theirs.

**4. A mechanism claim we can test.** Their explanation for the Fang contrast:

> *"architectural diversity disrupts shared inductive bias, which drives artificial consensus
> only when no objective ground truth constrains the outcome."*

Our setting has ground truth **and** an adversary pushing against it. Their theory makes a
falsifiable prediction about that cell. Testing it is a genuine contribution.

**5. Precedent for reporting negative results** (three failed Delphi designs) — consistent
with DR-0004.

## Weaknesses (fair to note in related work)

- Two scenarios only; one model pool; authors concede both.
- Coherence scores confound model capability with perspective–model fit — they say so.
- No frontier single-model baseline, so multi-agent architecture vs model capability is not
  isolated — they say so.
- Three of seven evaluators share one perspective, structurally weighting vote-based metrics.
- FCC's five-value discreteness at N=7 makes small vote changes produce large metric jumps.
- Single author, preprint, no venue listed.

## Where we cite it

- [x] Related Work — closest heterogeneity design; the normative/accuracy distinction
- [x] Method — justification for the discrete-state DV and the model-pool scale
- [x] Discussion — their capitulation-cascade hypothesis as the mechanism we test
- [x] Limitations — the domain-specificity caveat on our own result

## Verification

- [x] arXiv ID resolves; title matches character-for-character
- [x] Full text read (HTML), not a summary
- [ ] **Human confirmation of metadata and every attributed quote — REQUIRED before citation**
- [ ] Check whether a peer-reviewed version has appeared
