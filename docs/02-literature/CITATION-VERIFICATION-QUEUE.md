---
id: CITATION-QUEUE
title: Citation verification queue — human sign-off required before submission
status: ACTIVE — 0 of 21 verified
version: 1.0
created: 2026-08-09
required_by: SOP-020 §4 · G5 submission checklist
---

# Citation verification queue

**Nothing in this project has entered `references.bib`.** Every citation below was gathered by
AI-assisted search and is `[UNVERIFIED]` under SOP-020 §4 until a human has (a) opened the
source and confirmed title, authors, venue and year, and (b) located each attributed claim
**in the paper** — not in its abstract, and not in someone else's description of it.

The project lead has elected to do this in one pass at the end. **This document exists so that
pass is a checklist rather than an archaeology exercise.**

> ## Why this is not optional paranoia
>
> This review has already traced **four** mis-citations, and each was caught only because a
> human-equivalent read of the primary source was forced:
>
> 1. A fetch tool's summariser **inverted** `2601.05606`'s entire experimental setup — reporting
>    separately-run homogeneous groups where the paper mixes families within one network. Had it
>    been trusted, we would have concluded H1 was pre-empted and possibly abandoned a valid
>    contribution.
> 2. A **peer-reviewed bibliography** attributed A-HMAD to "Fang, Yizuo et al." The authors are
>    **Zhou & Chen**, and the paper reports the *opposite* of what was attributed to it.
> 3. The martingale result was recorded under the wrong authors — it is **Choi, Zhu & Li**.
> 4. Numeric claims required correction on citation: NetSafe's headline "29.7% drop" is decay
>    over 10 rounds with the attacker present, **not** a clean baseline contrast.
>
> Two of those four came from *published, peer-reviewed* sources. The failure mode is not
> AI-specific.

---

## How to verify one entry

1. Open the DOI / arXiv page. Confirm **title, authors, year, venue** against what we wrote.
2. Find each claim we attribute, **in the body**. Abstracts overstate.
3. Check every **number** we quote, in context — especially baselines and what a percentage is
   a percentage *of*.
4. Tick both boxes. If anything is wrong, correct the source document **and** log it.

Budget roughly 20–40 minutes per Tier-A paper, 10 for Tier-B. **About 6–8 hours total.**

---

## Tier A — cited closely, claims load-bearing

| # | Citation | Used in | Meta ✓ | Claims ✓ |
|---|---|---|---|---|
| 1 | Becker, Wahle, Ruas & Gipp — *Misinformation Propagation in Benign Multi-Agent Systems*, arXiv:2606.16710 | Prior art A1; H4 framing; RK-0015 | ☐ | ☐ |
| 2 | Ju et al. — *Flooding Spread of Manipulated Knowledge…*, arXiv:2407.07791 → Sci. China Inf. Sci. 69:172103 | Prior art A2 | ☐ | ☐ |
| 3 | Yu et al. — *NetSafe*, Findings of ACL 2025, arXiv:2410.15686 | Prior art A3. **Numeric correction attached** | ☐ | ☐ |
| 4 | Shen et al. — *Information Propagation Effects of Communication Topologies*, EMNLP 2025 Main | Prior art A4; OQ-0027 truth-diffusion argument | ☐ | ☐ |
| 5 | Li et al. — *News Diffusion Under Different Network Structures*, arXiv:2410.13909 | Prior art A5; density-matching precedent (OQ-0028) | ☐ | ☐ |
| 6 | Sela — *Preserving Disagreement*, arXiv:2604.26561 | OQ-0038 gradedness; OQ-0039; the whole discrete-state DV | ☐ | ☐ |
| 7 | Nilayam, Ramanna, Tumbade & Nayak — *Heterogeneous LLM Debate Under Adversarial Peers*, arXiv:2606.19826 | DR-0008 reframe; positioning | ☐ | ☐ |
| 8 | Choi, Zhu & Li — *Debate or Vote*, arXiv:2508.17536 | LIT-0003; AMD-0002 §5 martingale null. **Authors already corrected once** | ☐ | ☐ |
| 9 | Zhu, Zhang, Chi, Stafford, Collier & Vlachos — *Demystifying Multi-Agent Debate*, arXiv:2601.19921 | LIT-0004; OQ-0050 — the martingale-scope hook H1 hangs on | ☐ | ☐ |
| 10 | **Kim — *Are Diversity Metrics Measuring Diversity?*, arXiv:2607.20768** | **OQ-0051 (P0). The ρ = 0.991 figure drives a design criterion** | ☐ | ☐ |
| 11 | Zhang, Wang, Xue & Chu — *Post-Training Recipe, More Than Model Family…*, arXiv:2606.20632 | OQ-0052; D3 renamed on this basis | ☐ | ☐ |
| 12 | Zhou & Chen — *A-HMAD*, J. King Saud Univ. CIS 37:330 (2025), DOI 10.1007/s44443-025-00353-3 | LIT-0002; OQ-0046. **Mis-cited once already** | ☐ | ☐ |

## Tier B — load-bearing method or framing

| # | Citation | Used in | Meta ✓ | Claims ✓ |
|---|---|---|---|---|
| 13 | Chuang et al. — *Simulating Opinion Dynamics…*, Findings of NAACL 2024, arXiv:2311.09618 | External-classifier protocol; convergent validity | ☐ | ☐ |
| 14 | Zhang et al. — *Stop Overvaluing Multi-Agent Debate*, arXiv:2502.08788 | Debate reliability. **Position paper — never cite alone** | ☐ | ☐ |
| 15 | Smit et al. — *Should we be going MAD?*, arXiv:2311.17371 | Debate reliability; OQ-0026 | ☐ | ☐ |
| 16 | Wang et al. — *Rethinking the Bounds of LLM Reasoning*, ACL 2024, arXiv:2402.18272 | Debate reliability; OQ-0026 | ☐ | ☐ |
| 17 | Du et al. — *Improving Factuality… through Multiagent Debate*, arXiv:2305.14325 | The canonical pro-debate baseline | ☐ | ☐ |
| 18 | Han et al. — *Conformity Dynamics*, arXiv:2601.05606 | Prior art; OQ-0029. **Setup was fabricated by a summariser once** | ☐ | ☐ |
| 19 | Niu, Shu & Zhao — *Reliability-Contagion Feasibility*, arXiv:2607.21912 | OQ-0031 budget convention — a P0 design control | ☐ | ☐ |
| 20 | Savcisens, Dies, Maynard & Eliassi-Rad — *Belief Coevolution…*, arXiv:2607.27512 | Closest published design; H2 framing | ☐ | ☐ |
| 21 | Yan et al. — *When Truth Is Distributed*, arXiv:2608.03421 | Irreversibility metric support | ☐ | ☐ |

## Also requires verification, not citations

| Item | Why | ✓ |
|---|---|---|
| **All 31 fact-suite ground truths** | We score agents against these. A wrong "truth" silently inverts an outcome. | ☐ |
| Provider figures in `FEASIBILITY-ASSESSMENT.md` | Rate limits and prices move | ☐ |
| NVIDIA ToS §4(c) reading (`OQ-0053`) | Determines the matrix substrate | ☐ |
| Model licences and revision SHAs | `MODEL-POOL.md`; SOP-040 §5 | ☐ |

---

## Standing reminder

At the project lead's request, this is raised in **every** session summary until it is done, and
it is a hard blocker on the G5 submission checklist. Nothing here reaches the paper while it
carries `[UNVERIFIED]`.

The queue is also the reason to do it in one pass rather than never: **21 entries, ~7 hours,
already itemised with what each is used for.**
