---
id: LIT-0002
citekey: zhou2025adaptive
tier: B
threat: 1
read_by: AI-assisted (Claude Opus 5) — full text extracted from the open-access PDF
read_on: 2026-08-07
---

# LIT-0002 — A-HMAD: Adaptive Heterogeneous Multi-Agent Debate

**Full citation.** Zhou, Yan; Chen, Yanguang. "Adaptive heterogeneous multi-agent debate for
enhanced educational and factual reasoning in large language models." *Journal of King Saud
University Computer and Information Sciences* **37**:330 (2025). Received 14 Aug 2025,
accepted 18 Oct 2025, published online 24 Nov 2025. Open access.
**DOI:** 10.1007/s44443-025-00353-3
**PDF:** <https://link.springer.com/content/pdf/10.1007/s44443-025-00353-3.pdf> (19 pages)

> ## ⚠ This paper was mis-cited and mischaracterised
>
> It was entered in `OQ-0042` as *"Fang, Yizuo, et al. 'A-HMAD: Heterogeneous multi-agent
> debate for enhanced LLM reasoning'"* and recorded as **the direct null result for H1's
> regime** — the single most threatening paper in the review.
>
> **Every element of that was wrong:**
>
> | Recorded | Actual |
> |---|---|
> | Fang, Yizuo, et al. | **Zhou, Yan; Chen, Yanguang** |
> | Architectural heterogeneity | **Role/prompt heterogeneity on one base model** |
> | Null result for heterogeneity | **Positive result for heterogeneity** |
> | Relevant to adversarial regime | **No misinformation anywhere** (`misinform` = 0 hits) |
>
> The chain was: Sela's bibliography entry `[10]` → `OQ-0039` → `OQ-0042`. Whether the author
> error originated in Sela's bibliography or in transcription from it is **`[UNVERIFIED]`**
> and needs a re-read of Sela's reference list. The DOI, title, publisher and November-2025
> date all match, so it is the same paper.

## One-sentence claim (in our words)

Giving debate agents different **roles** — via prompts, on the same base model — plus dynamic
routing and a learned consensus weighting, improves accuracy on reasoning and factuality
benchmarks over standard homogeneous debate.

## Setup

| | |
|---|---|
| Agents | Multiple; ablations over agent count and rounds |
| **Models** | **Llama-2 70B-chat**, one 80 GB A100 per agent. GPT-4 used only as an optional "expert agent" or for comparison |
| **Heterogeneity type** | **Role/prompt**, not architectural |
| Topology | None — standard all-see-all debate |
| Task | Six benchmarks: arithmetic QA, GSM8K, MMLU, factual biography generation, chess strategy |
| Manipulation | Role specialisation, dynamic routing, learned consensus optimiser |
| **DV** | **Task accuracy** (and factual error rate in biographies) |
| Adversarial injection | **None** |

**The decisive quote**, §3.3, on how roles are implemented:

> *"**Specialized Prompting:** Agents share the same base model architecture but are given
> different role instructions in their prompt."*

and, on the architectural option they explicitly did **not** exercise:

> *"**Different Model Backbones:** We can also choose agents to be different pretrained models
> entirely… **In our experiments, we primarily use the same model class for a fair
> comparison**…"*

## Findings

- A-HMAD beats standard multi-agent debate by **4–6 percentage points** across the six
  benchmarks. GSM8K: **90.2%** vs **84.0%** (standard debate) vs **77.0%** (single agent).
- Reduces factual errors by **over 30%** in biography generation.
- Heterogeneity ablation: *"replacing specialized agents with identical ones drops performance
  by up to **3.5%** on reasoning tasks."*
- Learned consensus improves final accuracy by **5%** when initial agent votes are split.

## Threat to us — rated 1/5

It does not test architectural heterogeneity, does not inject misinformation, does not vary
topology, and does not measure convergence or position diversity. It is a role-specialisation
and aggregation-mechanism paper.

**Net effect on the project: the strongest published threat to H1 dissolves.** `OQ-0039`
recorded Sela's claim that *"heterogeneity does not reduce convergence"* in accuracy-oriented
debate, sourced to this paper. This paper measures **accuracy, not convergence**, and its
heterogeneity is **role-based, not architectural**. It cannot support that claim in either
respect.

## Gift to us

1. **A homogeneous-debate baseline in the same family we plan to use** (Llama-class), with
   published numbers we can position against.
2. **A confound we must control that we had not fully separated.** Role/prompt heterogeneity
   improves accuracy by up to 3.5% *on the same base model*. Our cohorts vary model family —
   but if our agents also differ in persona or prompt, we would be confounding architectural
   diversity with role diversity. **Our prompts must be identical across agents except for the
   seeded-agent manipulation**, and this paper is the citation for why. Raised as `OQ-0046`.
3. It reinforces that "diversity" is a family of distinct interventions (`OQ-0025`) —
   architectural, role, prompt, temperature — that the literature routinely conflates. Saying
   so clearly, with this paper as the example, is a cheap and genuinely useful contribution to
   the framing.

## Weaknesses a reviewer would attack

- Three interventions bundled (roles + routing + learned consensus); the ablation isolates
  heterogeneity at only up to 3.5%, so most of the 4–6% gain is from the other two components.
- No adversarial condition, so nothing about robustness.
- Single base model, so no evidence about architectural diversity despite the title's
  "heterogeneous".

## Where we cite it

- [x] Related Work — as role-heterogeneity, explicitly distinguished from architectural
- [x] Method — justification for holding prompts identical across agents (`OQ-0046`)
- [x] Discussion — the diversity-is-many-things point

## Verification

- [x] Citation metadata confirmed from the source PDF itself (SOP-020 §4.1, §4.7)
- [x] Every claim above located in the paper text (SOP-020 §4.2)
- [ ] Human sign-off (deferred to final citation pass at the project lead's request)
