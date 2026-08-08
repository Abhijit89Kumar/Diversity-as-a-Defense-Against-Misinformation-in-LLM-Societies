---
id: PRIOR-ART-REVIEW
title: Prior Art Review
status: DRAFT — round 1 of 2 complete
version: 0.1
created: 2026-08-07
closes: OQ-0001 (partially)
---

# Prior Art Review

> ## ⚠ Verification status
>
> Everything below was gathered by an automated multi-source sweep with adversarial
> verification (each claim challenged by three independent refuters; vote counts shown).
> **Under SOP-020 §4 that is not sufficient to cite.** No entry has been added to
> `references.bib`. Before any of this reaches the paper, a human must open each source
> and confirm (a) the paper exists with that title, those authors, that venue and year,
> and (b) each attributed claim appears in the paper.
>
> Treat this document as a **high-confidence reading list and threat assessment**, not as
> a citable literature review.
>
> A second sweep is in progress covering seven additional leads, belief-measurement
> validity, statistical standards, and feasibility. This document will be revised.

---

## Bottom line

**The generic contribution is gone.** "Injected misinformation propagates through
communities of communicating LLM agents" is published at least twice in peer-reviewed
venues. "Network topology modulates misinformation/error spread in LLM agent systems" is
published at least three times, with effect sizes and, in one case, significance tests.

SPEC-1 §4's related-work matrix — which frames the gap against Park et al. 2023, AutoGen,
TruthfulQA and classical SIR — describes a 2023 field. The field moved.

**What survives, narrowly:** cross-model-family heterogeneity as a *defence* against
misinformation was untested in every misinformation-propagation paper checked. That is
H1, and it is the project's strongest remaining claim. But the closest paper's authors
announced it as their own next step in June 2026, so it is a race, not an open field.

A striking pattern in the verification: **every claim of the form "this paper already did
Y" was confirmed; nearly every claim of the form "this leaves axis X open" was voted down
3-0.** The verifiers could find prior art for almost every axis and could not establish
that any axis is untouched. Read that as *not proven open* rather than *proven closed* —
but the asymmetry is the headline.

---

## Tier A — direct competitors

| # | Paper | Venue | Agents | Topology varied? | Model mix within system? | Seeding density varied? | DV | Threat |
|---|---|---|---|---|---|---|---|---|
| A1 | Becker et al., *Misinformation Propagation in Benign Multi-Agent Systems* | arXiv 2606.16710 (Jun 2026, preprint) | 3 | No | No — separate homogeneous groups | Partially (2 vs 3 uninformed) | Answer-repetition propagation rate | **5/5** |
| A2 | Ju et al., *Flooding Spread of Manipulated Knowledge in LLM-Based Multi-Agent Communities* | arXiv 2407.07791 → Sci. China Inf. Sci. 69:172103 (2026) | ~5 | No — single chatroom | No — three families run separately | No | acc / rephrase-acc / locality-acc | **4/5** |
| A3 | Yu et al., *NetSafe: Exploring the Topological Safety of Multi-agent System* | Findings of ACL 2025 (arXiv 2410.15686) | 6 | **Yes** — Chain, Cycle, Binary Tree, Star, Complete | No | No | MJA (mean over agents) | **4/5** |
| A4 | Shen et al., *Understanding the Information Propagation Effects of Communication Topologies in LLM-based MAS* | EMNLP 2025 Main, pp. 12347–12361 (arXiv 2505.23352) | 4–6 | **Yes** — sparsity spectrum | No — role/prompt variation only | No | Task accuracy + TCTE insight propagation | **4/5** |
| A5 | Li et al., *LLM-driven Multi-Agent Simulation for News Diffusion Under Different Network Structures* | arXiv 2410.13909 (Oct 2024, preprint) | ~300 | **Yes** — random, scale-free, high-brokerage, **density-matched** | No — GPT-3.5 only | No | SIR-like states (Spreader/Dead-end/Reached) | **3/5** |

---

### A1 — Becker, Wahle, Ruas, Gipp (2026) — the closest paper

*Misinformation Propagation in Benign Multi-Agent Systems*, arXiv:2606.16710, 15 Jun 2026,
cs.MA/cs.CL. Göttingen / GippLab.

**What they did.** Injected intent-based misinformation into benign single-agent and
multi-agent systems across reasoning, knowledge and alignment tasks: WinoGrande (382
items), Complex Web Questions (381), Ethics-commonsense (379), with 10,278 misinformation
texts across nine categories. 3 agents, 5 turns. Backbones Llama-3.3-70B-Instruct and
GLM-4.7-Flash, **run as separate homogeneous groups**. Their "group composition" variable
is the number of uninformed vs misinformed agents.

**What they found.**
- Multi-agent debate reduces degradation versus single-agent prompting, especially when
  most agents are unexposed. Like-for-like: single-agent **−12.9% to −17.2%**;
  multi-agent **−2.2% to −10.3%**.
- Error correction is **threshold-like, not gradual**: it "depends on whether correct
  information is represented by a majority". Self-correction rate rises from **8.0%** with
  2 uninformed agents to **20.5%** with 3.
- Robustness is model-dependent: GLM-4.7 loses 16.16% on CWQ and 25.56% on Ethics but
  *gains* 4.61% on WinoGrande; Llama-3.3 loses 26.75% / 25.71% / 19.51%. They conclude
  robustness "is not only a property of the decision protocol, but also of the underlying
  model."
- Misinformation "persists across multi-agent debate, with agents often retaining answers
  introduced by misinformed peers"; voting is more sensitive to misinformed peer pressure
  than consensus.

**Threat: 5/5, and it is a live race.** Their Future Work reads: *"Future work should
evaluate human-written or retrieved misinformation, larger agent networks, and comparisons
with Chain-of-Thought, Self-Refinement, and monitoring methods"*, and their Limitations
add *"additional model families… and more complex agent architectures"*. An established
lab publicly announced **both of this project's axes** — larger networks and additional
model families — as their next step, two months ago.

**What it leaves open.** Their ρ resolution is a 2-vs-3-agent comparison; our N=20 permits
a continuous density sweep. They do not vary topology at all. They do not mix model
families within a system. They use answer-repetition, not a credence probe.

**Implication for H4.** H4 must be framed as *increasing the resolution of a known
threshold effect*, not as discovering one. See `OQ-0004`.

---

### A2 — Ju et al. (2024/2026)

*Flooding Spread of Manipulated Knowledge in LLM-Based Multi-Agent Communities*,
arXiv:2407.07791 (Jul 2024); peer-reviewed as Science China Information Sciences vol. 69,
art. 172103, 2026.

**What they did.** A two-stage attack — "Persuasiveness Injection and Manipulated
Knowledge Injection" — seeds a malicious agent that persuades benign peers with
counterfactual and toxic knowledge. Critically, seeding is by **parameter modification**,
not prompting. ~5 agents, ~3 rounds, single all-see-all chatroom. Three model families
(Vicuna-7B-v1.5-16k, LLaMA-3-8B-Instruct, Gemma-7B-Instruct) run as **separate homogeneous
communities**. Manipulated knowledge persists through RAG.

**What it leaves open.** A full-text scan returns **zero** occurrences of "heterogeneous",
"heterogeneity", "mixed", "diversity", "topology" or "network structure". Their proposed
defences are explicitly guardian- and verification-based: *"…such as introducing
'guardian' agents and advanced fact-checking tools"* — **not population composition.**
That gap is precisely where H1 lives.

---

### A3 — NetSafe / Yu et al. (Findings of ACL 2025)

*NetSafe: Exploring the Topological Safety of Multi-agent System*, arXiv:2410.15686.

**What they did.** Misinformation, bias and harmful-information injection as a function of
topology. 6 nodes, 1 attacker, 10 RelCom rounds, mean of 3 runs. Names two failure modes
verbatim: *"Agent Hallucination, where misinformation from a single node leads to
network-wide hallucination"* and *"Aggregation Safety"*.

Fact dataset, Table 1: Chain 93.46→84.18 · Cycle 93.86→78.17 · Binary Tree 93.86→75.03 ·
Star 95.03→66.80 · Complete 94.12→80.39.

> **⚠ Numeric correction that must travel with any citation.** The headline "29.7% drop"
> is **decay over 10 rounds with the attacker present throughout** — 95.03 is turn 1 with
> the attacker already in the network, not a clean baseline. It must not be cited as
> "accuracy dropped 29.7% when misinformation was injected". The true no-attacker
> ablation is in their appendix Table 6.

**What it leaves open.** Full-text keyword scan: `Erdős` = 0, `random graph` = 0,
`scale-free` = 0, `polariz` = 0, `bimodal` = 0, `Kolmogorov` = 0. "Watts" and "small-world"
appear only in the bibliography. Their metric MJA is a **mean over agents — a first moment,
which cannot detect bimodality by construction.** No heterogeneous populations.

**Two problems in their paper worth flagging in our related-work section.** (i) An internal
contradiction: the abstract says *"networks with greater average distances from attackers
exhibit enhanced safety"* while §4.5 Trait 2 says *"the smaller the average distance from
nodes to the attacker, the safer the topology"* — one is wrong. (ii) Their own data
contradicts "denser = more vulnerable": on Fact, Complete (80.39) beats the sparser Cycle
(78.17) and Binary Tree (75.03).

**Rigor benchmark.** n = 3 runs, no significance testing, no effect sizes. We cannot cite
this as precedent for our replication count — but it does mean a properly-powered study is
itself a differentiator. See `OQ-0019`.

---

### A4 — Shen et al. (EMNLP 2025 Main) — the confound paper

*Understanding the Information Propagation Effects of Communication Topologies in
LLM-based Multi-Agent Systems*, arXiv:2505.23352, pp. 12347–12361. GPT-4o main results,
GPT-3.5 for analysis; 4–6 agents, K=3 rounds; MMLU / GSM8K / MultiArith / SVAMP / AQuA /
HumanEval. Uses counterfactual interventions where agents are prompted to deliberately
emit incorrect outputs — structurally analogous to our seeded agents.

**The finding that matters most to us**, verbatim:

> *"moderately sparse topologies, which effectively suppress error propagation while
> preserving beneficial information diffusion, typically achieve optimal task performance."*

and, crucially **measured rather than asserted**:

> *"sparse topologies tend to impede the propagation of accurate and informative signals,
> preventing them from influencing the final output"*

On questions the system originally answers incorrectly, Chain (maximally sparse) yields the
lowest TCTE insight-propagation value; full connectivity raises it by **10.5%**. Their
EIB-Learner drops only 1.24% under adversarial injection where chain and tree topologies
drop up to 11.8%.

**Design implication — this is a P0-adjacent problem for H2.** Any finding that sparser
graphs resist misinformation better is confounded: sparsity suppresses *true* information
too. TRR and MP as specified measure only the error side. **H2 is not identifiable without
a truth-diffusion counterpart metric** — e.g. the spread of correct belief originating from
non-seeded agents. Consistent with an interior optimum: Li et al., *Improving Multi-Agent
Debate with Sparse Communication Topology* (Findings of EMNLP 2024) report neighbour-
connected MAD at +2% on MATH and parity on GSM8K versus fully connected.

**Second design implication.** Our planned comparison — complete (density 1.0) vs ER p=0.2
(density ≈0.2) vs WS k=4 at N=20 (density ≈0.21) — **does not equalise edge count.** Any
"topology effect" would be confounded with connectivity. A5 below held density constant at
0.08 ± 0.002 and is a citable precedent that we did not.

---

### A5 — Li, Xu, Zhang, Malthouse (2024)

*Large Language Model-driven Multi-Agent Simulation for News Diffusion Under Different
Network Structures*, arXiv:2410.13909. 300 / 288 / 300 agents; GPT-3.5-Turbo-1106 at T=0;
5 FakeNewsNet fake political news items; 7-day horizon; random / scale-free /
high-brokerage graphs with **density held approximately constant (0.08 ± 0.002)**.

Reports *"News spreads most rapidly in scale-free networks, followed by random networks,
with the slowest spread occurring in high-brokerage network"*, with Wilcoxon rank-sum
p < 0.05 for all network-pair comparisons.

**Two things to take from this.** (i) They did the density control we did not — cite it and
match it. (ii) They operationalise spread as **observable forwarding behaviour** with
SIR-like states, requiring no logprob access at all. A reviewer-accepted, API-only
alternative to our Modal/vLLM logit infrastructure. (They also exhibit the pseudoreplication
exposure of `OQ-0006`: agents nested within runs, tests applied across runs.)

---

## Tier B — load-bearing

### B1 — Chuang et al., *Simulating Opinion Dynamics with Networks of LLM-based Agents*
Findings of ACL: NAACL 2024, pp. 3326–3346 (arXiv:2311.09618).
Code: `github.com/yunshiuan/llm-agent-opinion-dynamics`

**This is the gift.** It is a validated, peer-reviewed precedent for measuring agent belief
**without logits**: the agent produces a free-text verbal report, which is then classified
to a numeric scale by a *separate model*.

> *"The verbal report is then classified into a numeric opinion scale o_j^t in
> {−2,−1,0,1,2} through an opinion classifier, denoted f_oc."*

The classifier is FLAN-T5-XXL — a different model from the agents (gpt-3.5-turbo-16k,
T=0.7). Human-validated: Appendix N reports an agreement matrix against human ratings
showing "no systematic bias". And the authors report that the classifier output is **"more
reliable than self-reported ratings of the agents' own beliefs"** — a direct argument
against verbalised self-report.

**This substantially resolves `OQ-0002`.** It gives a uniform, provider-independent
measurement instrument applicable identically to Llama, Qwen and Gemini agents, removing
both the wrong-model-logits confound and the necessity of the Modal/vLLM infrastructure.

**Qualifications to carry forward.** Their construct is a bipolar attitude toward a
contested proposition on a signed scale, not a binary factual credence — a template, not a
drop-in protocol. And their own limitations concede that reducing "opinions to a
one-dimensional scalar" oversimplifies, a critique that applies verbatim to our scalar
Dual-Probe.

**Note — contested characterisations.** Two claims about this paper were put to
verification and did *not* survive: that its agents showed a strong intrinsic pull toward
factual accuracy regardless of assigned role (voted 0-3 refuted), and that polarization had
to be manufactured by prompt-engineering confirmation bias (voted 1-2). Both bear directly
on our floor-effect risk (`RK-0009`) and on whether H2's polarization is topology-driven or
prompt-driven. **Read this paper in full before relying on either reading.**

---

### B2 — The multi-agent-debate reliability literature

Confirmed 3-0, and it forces a design change.

- **Zhang et al.**, *Stop Overvaluing Multi-Agent Debate — We Must Rethink Evaluation and
  Embrace Model Heterogeneity* (arXiv:2502.08788): *"Surprisingly, our findings reveal that
  MAD often fail to outperform simple single-agent baselines such as Chain-of-Thought and
  Self-Consistency, even when consuming significantly more inference-time computation."*
  Advocates heterogeneity as *"a universal antidote"* across 5 MAD methods × 9 benchmarks ×
  4 models.
  > ⚠ The arXiv comments field marks this a **position paper** with no listed venue
  > acceptance. The claim that it empirically settles H1 was voted **0-3 refuted**. Never
  > cite it alone for the debate-underperformance finding — pair it with B3 and B4.
- **B3 — Smit, Duckworth, Grinsztajn, Barrett, Pretorius**, *Should we be going MAD?*
  (arXiv:2311.17371): *"multi-agent debating systems, in their current form, do not reliably
  outperform other proposed prompting strategies, such as self-consistency and ensembling"*
  — with the key qualifier that MAD is *"more sensitive to different hyperparameter settings
  and difficult to optimize"*. The honest reading is **unreliable/unoptimised**, not
  categorically worse.
- **B4 — Wang, Wang, Su, Tong, Song**, *Rethinking the Bounds of LLM Reasoning: Are
  Multi-Agent Discussions the Key?* (arXiv:2402.18272, ACL 2024): *"a single-agent LLM with
  strong prompts can achieve almost the same performance as the best existing discussion
  approach"*.
- **B5 — Du, Li, Torralba, Tenenbaum, Mordatch**, *Improving Factuality and Reasoning in
  Language Models through Multiagent Debate* (arXiv:2305.14325) — the canonical pro-debate
  paper. It positions debate as complementary to self-consistency rather than benchmarked at
  matched compute, so it does not contradict the above.

**Design implication, confirmed 3-0: a non-communicating single-agent control condition is
mandatory.** We cannot assume debate propagates truth. Without an isolated-agent arm
(`G_empty`), we cannot tell whether the network helped, hurt, or did nothing — and a
reviewer will ask.

**Framing implication.** H1 must cite Zhang et al. as the framing precedent. "Heterogeneity
helps" cannot be presented as an unanticipated discovery. Counterweight to pre-register
against: at least one 2026 source reportedly finds heterogeneous groups converge *more
slowly* due to "deliberative friction" — which reads as a benefit (cascade resistance) or a
cost (failure to reach truth) depending entirely on framing. **Pre-register which direction
counts as support for H1 before looking.**

---

## Where the contribution now stands

| Hypothesis | Status after round 1 |
|---|---|
| **H1** — heterogeneity as defence | **Strongest remaining claim.** Untested in every misinformation-propagation paper checked. But framed already by Zhang et al. as a position, and announced by Becker et al. as their next step. Race, not open field. |
| **H2** — small-world bimodal polarization | **Weakest.** Topology is thoroughly occupied. The only defensible residue is the *specific measurement*: bimodality of a belief distribution under ER vs WS at N=20 — no verified prior work uses ER/WS families or a distribution-shape DV. Threatened by unverified lead arXiv:2512.18094 on small-world debate topology. Also confounded (A4) and density-unmatched (A5). |
| **H3** — certainty drives belief shift | Least examined by the sweep. Likely the most defensible if converted to a **manipulation** rather than a regression (`OQ-0011`). |
| **H4** — critical seeding density | **Partially pre-empted** by Becker et al.'s threshold finding. Defensible only as a resolution refinement: their 2-vs-3-agent comparison versus our continuous sweep at N=20 — and only if a density factor is actually added (`OQ-0004`). |

### Provisional positioning statement (SOP-020 §6)

> **[DRAFT — do not finalise until round 2 and the seven leads are verified.]**
>
> Prior work establishes that injected misinformation propagates through LLM agent
> communities (Ju et al.; Becker et al.) and that communication topology modulates error
> spread (NetSafe; Shen et al.). All of it uses **homogeneous** agent populations. We test
> whether *population composition itself* is a defence: measuring functional diversity
> directly, and relating it to misinformation resilience across a range of cohorts at a
> scale (N=20) and with a belief-trajectory instrument that prior work has not applied. We
> additionally report the truth-diffusion counterpart that topology studies omit, so that
> resistance to falsehood is separated from suppression of information in general.

That is honest and narrower than the original framing. Whether it is *enough* for a
workshop is a judgement call — see the discussion questions at the end of the session.

---

## Design changes this review forces

Each becomes a `DR-xxxx` once decided.

1. **Add a non-communicating control arm.** Mandatory (B2, 3-0). Without it the study
   cannot attribute anything to the network.
2. **Add a truth-diffusion metric.** H2 is not identifiable measuring only the error side
   (A4). Track the spread of *correct* belief from non-seeded agents alongside TRR/MP.
3. **Match graph density across topologies**, or add density as an explicit factor. A5 did
   this; we do not; a reviewer who knows A5 will raise it (`OQ-0006` companion).
4. **Replace logit probing with an external-classifier protocol** (B1). Uniform across
   providers, human-validatable, removes the wrong-model confound, and deletes the entire
   Modal/vLLM dependency — which also removes most of the budget risk. This may be the
   single highest-value change available.
5. **Measure H(Θ) and build ≥4 cohorts spanning a range**, so H1 tests the continuous
   relationship it is stated as rather than a two-level categorical (`OQ-0005`).
6. **Convert H3 into a manipulation** — hold argument content fixed, vary stated certainty
   (`OQ-0011`).
7. **Add a seeding-density factor** or move H4 to a dedicated sub-experiment (`OQ-0004`).
8. **Pre-register the direction of the H1 prediction**, given that "slower convergence"
   under heterogeneity is reportable as either support or refutation.
9. **Report significance tests and effect sizes.** The comparable papers mostly do not
   (NetSafe: n=3, no tests). This is a cheap differentiator.
10. **Re-run the Tier-A sweep immediately before submission.** Becker et al. appeared in
    June 2026. The novelty framing has a shelf life measured in weeks.

---

## Reading queue

**Read in full, before G1:**
1. Becker et al. 2606.16710 — closest competitor, scoop risk
2. Chuang et al. 2311.09618 — the measurement protocol we should probably adopt
3. Shen et al. 2505.23352 — the confound
4. NetSafe 2410.15686 — including appendix Table 6
5. Ju et al. 2407.07791
6. Li et al. 2410.13909 — for the density control

**Not yet covered by any verified claim** — mixture-of-agents and diversity-of-thought
ensembling; JS-divergence functional-diversity measurement and its tokenizer confounds;
logit calibration after RLHF; sycophancy; ordering bias; and the validity of scoring one
model's belief with another model's logits. Round 2 covers these.

---

# Round 2 — the seven leads, verified

**All seven arXiv IDs are real.** Each was fetched from the primary source (abs page plus
full HTML or PDF text, not search snippets), with keyword absence checks run over the full
text. None was hallucinated.

| # | Paper | Date | N | Mixes model families? | Topologies | Injects misinfo? | Threat |
|---|---|---|---|---|---|---|---|
| C1 | **The Deliberative Illusion** (Wan, Wu, Luo, Li, Wang, Chen, Kan) — `2606.03032` | 2 Jun 2026 | 4 | **Yes** | full / binary tree / chain | Yes (1 malicious) | **4/5** |
| C2 | **Conformity Dynamics** (Han, Tan, Yu, Zheng, Tang) — `2601.05606` | 9 Jan 2026 | 7 | **Yes** | star / hierarchical / rings m=2–6 / complete | **No** | 3/5 |
| C3 | **You Can't Fool Us** (Lin, Jin, Hu, Fan, Xiao, Wang, Ying, Zhao) — `2605.17353` | 17 May 2026 | **200** | No | one fixed WS graph | Yes (ρ=0.1 per round) | 3/5 |
| C4 | **Reliability-Contagion Feasibility** (Niu, Shu, Zhao) — `2607.21912` | 24 Jul 2026 | 6 LLM / 32 sim | No | circulant regular | Yes (1 seed) | 3/5 |
| C5 | **From Spark to Fire** (Xie, Zhu, Zhang, Zhu, Ye, Qi, Chen, Zhou) — `2603.04474` | 4 Mar 2026 | 5 | No | chain / mesh / star | Yes (1 seed at t=0) | 3/5 |
| C6 | **Small-World Networks** (Wang, Li, Huang, Dong) — `2512.18094` | 19 Dec 2025 | 8 | No | full / ring / resampled-random / **WS-rewired** | No | 2/5 |
| C7 | **ARGUS / Goal-Aware Rectification** (Li, Mi, Zhou, Jiang, Zhang, Wang, Fang) — `2506.00509` | 31 May 2025 | 3–6 | No | self-determined / chain / full | Yes (1 agent) | 2/5 |

## The good news: H1's central wedge got sharper

**Two papers now publish a directional "diversity helps" result — and both are confounded
with capability in exactly the way a scale-matched design would fix.**

- **C1 §5.4** mixes families within one system and finds cross-series agents retain more
  critical facts than same-series (**.598 vs .357**). But their "same-series" arm is
  GPT-5 + GPT-4.1 + **GPT-3.5-turbo**. That is not a scale-matched control — it is a
  capability-degraded one. Their diversity effect is plausibly a capability effect.
- **C2** sweeps a GPT-3.5:GPT-4o mixing ratio from 0:7 to 7:0 and concludes the *opposite*:
  *"the accuracy of the emergent consensus is ultimately determined by the capability of the
  prevailing model class"* and *"peripheral diversity does not reliably compensate for
  central incompetence."* Also confounded — their heterogeneity is capability heterogeneity.

So the literature contains **two contradictory published results on diversity, neither of
which controls for capability.** That is a much better place to stand than an empty field:
the project's contribution becomes *the causal isolation* — does diversity help once you
hold capability fixed? — which is a real question with a real disagreement behind it, and
neither group can retrofit the control cheaply.

**Also untouched: heterogeneity × adversary is never crossed.** C1's injection experiment
(58.9% of final outputs contaminated under full connectivity; 37.4% of normal agents; stance
reversal up to 82.4%) is **homogeneous GPT-4.1 only**. Their own Table 4 makes the crossed
cell the obvious next experiment, and nobody has run it.

## The bad news, itemised

**C2 kills a framing.** "First to jointly vary topology and model heterogeneity in an LLM
setting" is gone — C2 did exactly that in January 2026. It is a mandatory
cite-and-differentiate. What survives: C2 has **no seeding or injection of any kind**
(keyword search for *seed*, *inject*, *adversar*, *malicious*, *attack* returns zero hits),
fixed N=7, no WS/ER graphs, and a Conformity Index bounded [0.5, 1] that is structurally
incapable of detecting a bimodal split.

**C6 predicts the opposite sign to H2.** *"Small-world exhibits smoother convergence and
lower variance than any other baselines"* and *"long-range shortcuts… substantially
stabilizes the consensus dynamics."* H2 predicts small-world structure *polarizes*. This
must be reconciled explicitly in related work, not left for a reviewer. Two honest
reconciliations exist: the DVs differ (trajectory stability vs final-distribution shape —
genuinely different quantities that can coexist), or misinformation injection changes the
regime. C6 also stakes an **untested** claim that *"sparse long-range SW links can act as
backchannels that intercept or override local misinformation"* — which the project could
actually adjudicate. That is a strong positioning move.

**C3 stakes H4 conceptually.** Its Future Work proposes, in prose, almost exactly H4:
*"a community may recover when exposure is sparse but retain support once exposure exceeds a
critical level."* They ran nothing, so H4 is empirically open — but "nobody thought of this"
is no longer available, and C3 must be cited at the point ρ\* is introduced.

**C3 also sets an uncomfortable scale bar: N = 200 agents, T = 10, 5 seeds.** Our N = 20
will look small against a May-2026 preprint in the same problem space. Worth confronting
directly.

**C5 collides on notation.** Its amplification criterion is `β·ρ(A) > δ` where **ρ is the
adjacency spectral radius**, while H4's ρ is seeding density. Rename ours before this
reaches review.

## Two design controls this round forces

**1. Communication-budget convention (new P0-class issue).** C4's most useful result:
*"Under fixed exposure per communication edge, reliability and error control impose opposing
graph constraints… Under a fixed sender budget, the homogeneous first-order threshold is
independent of network density."*

Translation: whether adding edges increases infection risk **depends entirely on whether you
hold per-edge exposure or total sender budget fixed.** If we compare complete vs ER vs WS
without fixing and stating this convention, a reviewer can argue the entire topology effect
is an artefact of exposure normalisation. This compounds the density-matching problem
(`OQ-0028`) and must be an explicit, preregistered design control. Logged as `OQ-0031`.

**2. Seeding definition.** C3 re-exposes 10% of agents to the misinformation **every round**;
SPEC-2's manifest seeds two agents **once**. These are not comparable quantities and cannot
be cited against each other without care. Logged as `OQ-0034`.

## Reusable assets

- **C3's summary metrics** are clean and directly adoptable, and using them makes comparison
  to their N=200 baseline immediate: `Robustness = 100 − normalised trust AUC` and
  `Recovery = 100 · (τ_peak − τ_T) / (τ_peak − τ_0 + ε)`. Their backbones are all 3–4B
  (Qwen3-4B, Qwen2.5-3B, Phi-4-mini, Gemma3-4B), so a parameter-matched heterogeneity design
  at that scale runs directly against their published homogeneous baselines.
- **C7 supplies a dataset and a DV**: MisinfoTask (108 tasks) and Misinformation Toxicity
  (LLM-judge, [0,10]) with TSR. Baseline vulnerability: MT 1.28 → 4.71, TSR 87.47% → 67.70%.
  A reviewer who knows C7 will ask why we did not report MT alongside our own metric. Cheap
  to add.
- **C5 gives a free baseline argument for H1**: *"five [of six frameworks] reach 100% final
  infection, including settings with explicit reviewer or QA roles."* Role-based verification
  inside a homogeneous population fails. That sets up diversity-as-defence rather than
  undercutting it.

## ⚠ Methodological warning from the verification itself

The agent verifying C2 reported that **WebFetch's built-in summariser fabricated that
paper's entire experimental setup** — it claimed 3/5/7/9 agents, separately-run homogeneous
groups, random graphs, and an adversarial fraction swept at 0/20/40/60%. All four are false;
the ground truth from the PDF is N=7 fixed, families *mixed* within one network, no random
graphs, and no adversarial agents at all. The summariser inverted the single most
decision-relevant fact.

**Operational consequence, now written into SOP-020 §4.6:** never characterise a paper from
a prose summary of a PDF. Extract the text and read it. This is the exact failure mode our
citation-integrity rule exists to catch, and it fired on the highest-priority paper in the
queue.

## Round 2b — two further leads, fetched directly

Both real. Metadata read from the arXiv abs pages (`citation_title` / `citation_date` /
`citation_author` meta tags), abstracts quoted verbatim.

### D1 — `2604.26561` — **the closest paper to H1 found anywhere**

**Sela, Ariel.** *Preserving Disagreement: Architectural Heterogeneity and Coherence
Validation in Multi-Agent Policy Simulation.* 29 April 2026. Single author.

Framework "AI Council", three-phase deliberation, **120 deliberations across two policy
scenarios**. And critically:

> *"architectural heterogeneity (assigning a different **7-9B parameter model** to each value
> perspective) significantly reduces first-choice concentration compared to a homogeneous
> baseline (child welfare: 70.9% to 46.1%, p < 0.001, r = 0.58; housing: 46.0% to 22.9%,
> p < 0.001, r = 0.50)."*

**This is a scale-matched architectural-heterogeneity experiment with significance tests and
effect sizes.** It is the design H1 proposes, executed four months ago — on a different task.

**Why it does not kill H1, and why it still matters enormously:**

- Their DV is *first-choice concentration in a values-based policy deliberation with no
  ground truth*. Ours is truth retention under adversarial misinformation injection. Those
  are different constructs.
- No misinformation is injected. No topology is varied.
- **But their abstract contains a direct challenge to H1's premise:**
  > *"This contrasts with accuracy-oriented multi-agent debate, where heterogeneity **does
  > not** reduce convergence, suggesting model diversity operates differently when no
  > objectively correct answer exists."*

  Our task is squarely accuracy-oriented — factual claims with ground truth. This sentence
  says heterogeneity's benefit may not transfer to our regime. **`[UNVERIFIED]` whether this
  contrast is their own experiment or a reference to prior work — the abstract page does not
  resolve it, and it must be settled by reading the paper.** If it is their own result, it is
  the strongest single piece of evidence against H1 in the entire literature. Highest-priority
  read.

- **And a finding that threatens the measurement, not just the hypothesis:**
  > *"8B models exhibit **binary rather than graded** responses to counter-arguments"*

  The v1.0 design's primary population is 20× Llama-3.1-**8B**, and the entire dependent
  variable is a *graded* belief in [0,1]. If 8B-class models flip rather than shade, the
  belief trajectory is a step function and most of the metric's resolution is illusory.
  Raised as `OQ-0038`.

- Useful precedent: they *"report negative results from three failed Delphi designs"* — a
  model for how to publish honest process failure, consistent with DR-0004.

**Threat: 4/5.** Cite-and-differentiate mandatory. Also the strongest argument that the
project should run the isolated-agent control (`OQ-0026`) and check gradedness before
committing to the belief metric.

### D2 — `2605.15343` — a competing belief instrument

**Yang, Joshua C.; Flechtner, Maurice; Dailisan, Damian; Bakker, Michiel A.** *Belief Engine:
Configurable and Inspectable Stance Dynamics in Multi-Agent LLM Deliberation.* 14 May 2026.

> *"an auditable belief-update layer that treats 'belief' as an evidential state over a
> proposition and exposes it as scalar stance. BE extracts arguments into structured memory
> and updates stance with a **log-odds rule** controlled by evidence uptake u and prior
> anchoring a."*

Validated against **DEBATE**, a human deliberation dataset with pre/post opinions.

**Threat to our hypotheses: 2/5. Value as a method: high.** Two things to take:

1. It is a third option for `OQ-0002`, alongside our dual-probe and Chuang et al.'s external
   classifier — but note the crucial difference: BE **imposes** a belief-update rule rather
   than measuring an emergent one. That is a different scientific object. Our question is what
   agents actually do; theirs is a controllable substrate. Worth stating explicitly, because
   a reviewer may otherwise ask why we did not just use BE.
2. Their framing names our H3 confound structure precisely: stance movement *"may reflect
   evidence uptake, anchoring, role drift, echoing, or changed prompt and retrieval context."*
   That is the list H3's regression must disentangle — and it is the argument for converting
   H3 into a manipulation (`OQ-0011`) rather than a regression.

## Round 2c — `2604.26561` read in full; two P0 citations traced

Full text read 2026-08-07 (arXiv HTML, extracted locally). Note: **LIT-0001**.

**The abstract's threatening sentence was a citation, not their result.** From their Related
Work, verbatim:

> *"**Fang et al. [10]** introduce **A-HMAD**, a heterogeneous multi-agent debate framework,
> and critically find that **heterogeneity does not reduce convergence in accuracy-oriented
> tasks**."*

Sela uses that null as a *contrast* supporting a domain-specific mechanism:

> *"architectural diversity disrupts shared inductive bias, which drives artificial consensus
> **only when no objective ground truth constrains the outcome**."*

**This is the sharpest available statement of the risk to H1 — and it makes a falsifiable
prediction about a cell nobody has run.** Fang's setting has ground truth and no adversary.
Sela's has an adversary-free setting with no ground truth. **Ours has ground truth *and* an
adversary actively pushing against it.** Sela's theory predicts diversity should not help
there; the capitulation-cascade mechanism (below) predicts it should. Testing between them is
a real contribution.

### Three references traced, all previously unknown to us, all `[UNVERIFIED]`

| Ref | Why it matters | OQ |
|---|---|---|
| **Fang, Yizuo, et al.** *"A-HMAD: Heterogeneous multi-agent debate for enhanced LLM reasoning."* Springer, Nov 2025 | The direct null result for H1's regime. **Highest-priority paper to obtain.** | `OQ-0042` |
| **Huang, Qiang, et al.** *"Debate or vote: LLM multi-agent debate is a martingale on belief of the correct answer."* OpenReview, 2025 | Proves debate adds nothing in expectation over independent voting. Supplies a **theoretical null for our no-injection control** and moves the action to variance/tails. | `OQ-0043` |
| **Li, Yanchen, et al.** *"Talk isn't always cheap: Weak models in heterogeneous multi-agent debate."* arXiv:2509.05396 | Weak models in heterogeneous debate can **degrade** outcomes. A competing explanation for Fang's null that our capability matching must separate out. | `OQ-0042` |

Also surfaced from the same bibliography, lower priority: Chen et al., *ReConcile* (ACL 2024,
diverse model pools improve reasoning accuracy); Masłowski & Chudziak, arXiv:2603.27404
(architectural heterogeneity prevents argumentative degeneration); El Kandoussi,
arXiv:2604.00026 (behavioural differentiation without role assignment); Pitre et al.,
*CONSENSAGENT* (Findings of ACL 2025, sycophancy in multi-agent debate); Xiong et al.,
arXiv:2310.13740 (LLM conformity effects); Sharma et al., arXiv:2310.13548 (sycophancy).

### The finding that changed the design

`2604.26561` §7.4, verbatim:

> *"8B models exhibit binary rather than graded responses to counter-arguments: they either
> maintain their position entirely… or capitulate entirely… The absence of a 'consider and
> reject' middle state… appears to be a robust characteristic of the **7–9B parameter range**."*
>
> *"Any multi-agent architecture that exposes small-model agents to arguments from other agents
> risks inducing **capitulation cascades**, where the first agent to encounter a persuasive
> argument flips, creating a feedback loop. Architectural designs that preserve agent isolation
> during evaluation — as our system does — are necessary safeguards at this model scale."*

**Sela names our phenomenon, identifies its mechanism, flags it as a hazard, and designs around
it rather than studying it.** Consequences, all carried into `AMD-0001`:

- The DV moves from a graded credence to a **discrete state with survival analysis** —
  better-fitting, cheaper, and it removes an artefact that could have manufactured an H2
  result (`OQ-0038`).
- Combined with the martingale result, the paper's real subject is **cascade dynamics and tail
  risk**, not mean belief shift.
- Their model pool — Qwen3-8B, Mistral-NeMo, Mistral-7B-Instruct-v0.3, Qwen2.5-Coder-7B,
  Dolphin3-8B, DeepSeek-R1-8B, Gemma2-9B, all local via Ollama on consumer hardware — is
  directly reusable under DR-0005 and makes our results comparable to theirs.

---

# ⚠ Round 3 — `2606.19826` is the closest paper found, and it is close

**Nilayam, Prashanti; Ramanna, Kiran Kumar; Tumbade, Prashil; Nayak, Sankalp (ServiceNow).**
*"Heterogeneous LLM Debate Under Adversarial Peers: Honest Gains, Replacement Costs, and
Resilience."* arXiv:2606.19826, **18 June 2026**. Abstract + full text read directly.

**Threat: 5/5.** Their closing sentence is, in substance, H1:

> *"Heterogeneity is therefore not only an attack surface but, when an adversary is already
> present, also a defense."*

**What they did.** Matched debate *panels* — homogeneous baseline, honest-mixed,
adversarial-mixed — plus contaminated panels already containing a malicious same-family peer.
Four model families, three reasoning benchmarks (MATH-hard primary, SciBench, GSM8K). DV is
*defender-centred revision behaviour*: how often honest agents change answers and whether the
change is corrective or harmful.

**Results.** Llama-3.1-70B defenders on MATH-hard: honest-slot harmful-revision rate
**89% (homogeneous) → 35% (honest peer) → 90% (adversarial peer)**. In contaminated panels,
adding an honest heterogeneous peer cut the flip rate on initially-correct items from
**31% → 6%**. Signs hold across four families and three benchmarks.

## What this costs us

H1's headline — *heterogeneity defends against adversarial influence in accuracy-oriented
tasks* — **is published.** It can no longer be framed as an open question. Say so plainly in
the introduction; a reviewer will find this paper.

## What survives, and it is more than consolation

Four gaps, and the first is the important one.

**1. They deliberately exclude the dynamics we study.** Verbatim:

> *"We analyze the first revision step, R0→R1, where panel composition has its cleanest
> interpretation… **Later rounds compound direct peer influence with path dependence from
> earlier revisions**, so we use R0→R1."*

They measure **one revision step**. Cascades, path dependence, multi-round propagation,
recovery — the entire subject of this project — is what they explicitly set aside as a
complication. This is the same pattern as `2604.26561`: identify the dynamics, design around
them, leave them unstudied. **Two independent groups have now flagged multi-round cascade
behaviour as the thing they are avoiding.** That is a strong signal about where the open
problem is.

**2. Panels, not networks.** No topology, no graph structure, no scale. Influence is
all-to-all within a small panel.

**3. Slot-matched, not capability-matched.** They *"replace a single slot"* — matching is on
composition size. Swapping a Llama slot for a GPT-4.1 slot changes diversity **and**
capability together. **The capability confound is intact in this paper too**, which means all
four published heterogeneity results — `2606.03032` positive, `2601.05606` negative, Fang et
al. null, and this one positive — rest on uncontrolled capability. Our central control is
still unoccupied.

**4. Binary heterogeneity, no measured continuum.** Three conditions, no `H(Θ)`, no diversity
ladder. They cannot distinguish architectural diversity from any other source of
decorrelation.

## Revised honest positioning

> Nilayam et al. (2026) show that an honest heterogeneous peer sharply reduces harmful
> revision under adversarial influence — measured at the **first revision step**, in
> **slot-matched panels**. We ask whether that protection survives what they set aside:
> multi-round cascade dynamics in a network, at **matched capability**, across a measured
> continuum of functional diversity. Given that 7–9B models capitulate rather than shade
> (Sela 2026) and that debate is a martingale in expectation (Huang et al. 2025), a
> single-step benefit need not imply a multi-round one — protection could decay, persist, or
> invert as cascades develop.

That is a narrower claim than the project started with, it is honest, and it is a question a
reviewer would want answered.

---

## Still unverified

IDs unknown; surfaced from search snippets only:

- *Robust Multi-Agent LLMs under Byzantine Faults*
- *Defending LLM-based Multi-Agent Systems Against Cooperative Attacks with Sentence-Level
  Rectification*
- *Social Reasoning in Machines: Investigating Collective Truth-Seeking Dynamics in Large
  Language Model Debate*

## Revised positioning statement

> **[DRAFT v0.2 — supersedes v0.1 above.]**
>
> Recent work establishes that misinformation propagates through LLM agent communities
> (Ju et al.; Becker et al.; Wan et al.) and that communication topology governs cascade
> outcomes (NetSafe; Shen et al.; Niu et al.). Two 2026 studies report *opposite* directional
> effects of model heterogeneity — Wan et al. find mixed-family groups retain more facts,
> Han et al. find consensus accuracy is set by the strongest model class — but **neither
> controls for capability**, so neither isolates diversity from competence. We resolve this
> with a capability-matched design: cohorts spanning a measured range of functional
> diversity at fixed aggregate single-agent accuracy, evaluated under adversarial
> misinformation injection — the heterogeneity × adversary cell that prior work leaves
> empty — and reporting truth diffusion alongside error diffusion so that resistance is
> separated from suppression.

That is a real contribution with a real disagreement behind it, and it is defensible against
every paper found so far.
