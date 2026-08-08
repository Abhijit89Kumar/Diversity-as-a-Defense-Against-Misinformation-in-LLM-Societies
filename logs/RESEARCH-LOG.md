# Research Log

Append-only lab notebook. Newest entries at the bottom. Never edit a past entry —
supersede it with a new dated one. Format and rules: SOP-010 §1.1.
Template: `meta/templates/log-entry.md`.

---

## 2026-08-07 — Session 001: Foundation, spec intake, and specification audit

**Participant(s):** Project lead; AI-assisted (Claude Opus 5, Claude Code)
**Phase / Gate:** G0 → Foundation
**Goal:** Read the four v1.0 specification documents, establish the repository as a
governed research environment, and identify anything in the design that must be resolved
before engineering starts.

### Done
- Read all four source documents in full.
- Converted each `.docx` to faithful Markdown; originals preserved in
  `docs/01-specifications/source-docx/`. Conversions marked read-only source-of-record.
- Established the repository structure defined in SOP-000 §4.
- Wrote the governance layer: `SOP-000` (master), `SOP-010` (documentation & logging),
  `SOP-020` (literature), `SOP-030` (design & preregistration), `SOP-040` (code &
  reproducibility), `SOP-050` (data), `SOP-060` (analysis & statistics), `SOP-070`
  (writing & submission), `SOP-080` (integrity & AI assistance).
- Initialised the four registers: decisions, open questions, risks, changelog.
- Recorded `DR-0001`…`DR-0004`.
- Launched a deep literature and feasibility sweep covering novelty/prior art, evidence
  on whether model heterogeneity helps, validity of LLM belief measurement, statistical
  standards for multi-agent simulation studies, and 2026 cost/rate-limit/deadline reality.

### Found

The specifications are unusually well-organised for a project at this stage — the
formalism, the factorial matrix, the fact taxonomy, and the collaboration charter are all
genuinely above the norm for a first research project. The problems are not sloppiness;
they are the specific kind of gap that appears when a plan is written top-down and has not
yet met an executor. Recorded as `OQ-0001`…`OQ-0025`. The seven rated P0:

1. **The logit probe measures the wrong model** (`OQ-0002`). `modal_prober.py` hardcodes
   Llama-3.1-8B and applies it to every agent's context. In the heterogeneous condition
   the agents are Qwen, Gemini and Cerebras-served models. Since H1 *is* the
   heterogeneous-vs-homogeneous comparison, the primary comparison would be confounded
   with the measurement instrument. This is the single most serious issue found.
2. **The primary metrics have no definitions** (`OQ-0003`). TRR, MP, BPI, I∞ and R₀ carry
   all four hypotheses and appear in the output schema, but no formula for any of them
   exists in any of the four documents.
3. **H4 has no experiment** (`OQ-0004`). Testing a critical seeding density ρ\* requires
   varying seeding density; the 405-run matrix holds it fixed.
4. **H(Θ) is defined but never measured** (`OQ-0005`). H1 is formally stated over a
   continuous diversity measure and a threshold τ, but the design manipulates a two-level
   categorical. Separately, pairwise JS divergence over token distributions is not
   well-defined across models with different tokenizers.
5. **Pseudoreplication** (`OQ-0006`). Agents nested within runs are not independent; the
   planned ANOVA and K–S tests read as operating on pooled agent-level data.
6. **Call volume undercounted ~4×** (`OQ-0007`). The 40,500 figure counts message
   generation only and omits belief probing entirely; the true figure is on the order of
   160,000 calls. Every feasibility and budget claim descends from the wrong number.
7. **Novelty unverified** (`OQ-0001`). The related-work matrix reflects a 2023 view of the
   field. The 2024–2026 literature on multi-agent LLM safety and topology effects is not
   represented.

Also notable but sub-P0: the budget is internally inconsistent — SPEC-3 costs the
annotation study at $135 (150 items × 3 annotators) while SPEC-4 budgets $40 (150 ratings
× 1 annotator), and Fleiss' κ cannot be computed from a single annotator, so SPEC-4's
figure corresponds to a study that cannot produce SPEC-3's statistic. The router's error
placeholder string enters neighbouring agents' contexts as a message, and failure rates
will differ by provider, making the contamination correlated with condition. H2's K–S test
does not test bimodality. H3 is written as a causal claim but analysed observationally.

### Decided
- `DR-0001` — adopt the governed structure and SOP set.
- `DR-0002` — v1.0 documents are source of record; corrections happen as amendments.
- `DR-0003` — insert a design-freeze gate (G1) before confirmatory compute; non-critical
  engineering may proceed in parallel.
- `DR-0004` — commit in advance to reporting null results as null, superseding the
  operational reading of SPEC-4 §6 Risk 3.

### Open / Next
- Deep literature and feasibility sweep in flight; results feed `OQ-0001`, `OQ-0013`,
  `OQ-0014`, `OQ-0018`, `OQ-0020`, `OQ-0023`.
- Next: write `docs/02-literature/PRIOR-ART-REVIEW.md` from the sweep, then the
  positioning statement (SOP-020 §6).
- Then: resolve the belief-metric question (`OQ-0002`), which determines the engine's
  requirements and therefore gates most engineering.
- Decision needed from the project lead on scope: see the questions raised at the end of
  session 001.

---

## 2026-08-07 — Session 002: Prior-art sweep, round 1

**Participant(s):** Project lead; AI-assisted (Claude Opus 5, Claude Code)
**Phase / Gate:** G1 — Design freeze (blocked)
**Goal:** Establish whether the core contribution is already published (`OQ-0001`).

### Done
- Completed a multi-source sweep: 5 angles, 27 primary sources fetched, 135 candidate claims
  extracted, 25 adversarially verified by 3 independent refuters each. 12 confirmed,
  13 refuted.
- Wrote `docs/02-literature/PRIOR-ART-REVIEW.md` (v0.1, draft — citations **not** yet
  human-verified per SOP-020 §4, so nothing has entered `references.bib`).
- Launched a second sweep to verify seven unfetched leads and to cover the coverage gaps:
  belief-measurement validity, statistical standards, provider feasibility, and logistics.

### Found

**The generic contribution is gone.** "Injected misinformation propagates through
communities of communicating LLM agents" is published at least twice in peer-reviewed
venues — Ju et al. (Science China Inf. Sci. 69:172103, 2026) and Becker et al.
(arXiv:2606.16710, Jun 2026). "Topology modulates misinformation/error spread in LLM agent
systems" is published at least three times — NetSafe (Findings of ACL 2025), Shen et al.
(EMNLP 2025 Main), Li et al. (2024, with Wilcoxon tests). SPEC-1 §4's related-work matrix
describes a 2023 field.

**The most uncomfortable finding.** Becker et al.'s Future Work names *"larger agent
networks"* and their Limitations name *"additional model families"* — an established lab
publicly announced **both of this project's remaining axes** as their next step, eight weeks
ago. Logged as `RK-0015`, severity 20.

**Pattern worth noting.** Every claim of the form "this paper already did Y" was confirmed
3-0. Nearly every claim of the form "this leaves axis X open" was voted down 3-0. Verifiers
could find prior art for almost every axis and could not establish that any axis is
untouched. That asymmetry is itself the result — read the refutations as *not proven open*,
not *proven closed*.

**Two design threats confirmed at 3-0.**
1. Multi-agent debate does not reliably beat single-agent baselines (Zhang et al.
   arXiv:2502.08788; Smit et al. arXiv:2311.17371; Wang et al. ACL 2024). We cannot assume
   the network propagates truth. A non-communicating control arm is mandatory (`OQ-0026`).
2. Sparse topologies suppress *true* information as well as false — Shen et al. measured a
   10.5% beneficial-insight propagation gap between chain and full connectivity, and conclude
   the optimum is at *moderate* sparsity. TRR/MP measure only the error side, so H2 is not
   identifiable as specified (`OQ-0027`).

**The single most useful find.** Chuang et al., *Simulating Opinion Dynamics with Networks
of LLM-based Agents* (Findings of NAACL 2024, arXiv:2311.09618) is a peer-reviewed,
human-validated precedent for measuring agent belief with an **external classifier over
free-text reports** — no logprobs needed. It applies identically to open-weight and
closed-API agents, and the authors report it is more reliable than agents' self-reported
belief ratings. Adopting it would resolve `OQ-0002`, make the instrument uniform across
conditions, and delete the entire Modal/vLLM dependency — removing most of the budget risk
at the same time.

**Also found:** Li et al. (2024) held graph density constant at 0.08 ± 0.002 across their
topologies. Our design does not (`OQ-0028`). And NetSafe's headline "29.7% drop" is decay
over 10 rounds with the attacker present throughout, not a clean baseline contrast — a
numeric correction that must travel with any citation of it.

### Decided
- No new DRs. The design changes this forces are staged as `OQ-0026`…`OQ-0030` pending the
  round-2 results and a decision from the project lead on repositioning.

### Open / Next
- Round-2 sweep in flight: seven unverified leads (`OQ-0030`), belief-measurement validity,
  statistical standards, provider/cost feasibility (`OQ-0013`, `OQ-0014`, `OQ-0020`,
  `OQ-0023`).
- Highest-priority single item: verify `arXiv:2601.05606`, which reportedly crosses topology
  **and** model heterogeneity. If real, H1 and H2 may be jointly pre-empted.
- Then: repositioning decision, then the belief-metric DR, then the preregistration.

---

## 2026-08-07 — Session 003: Lead verification and feasibility assessment

**Participant(s):** Project lead; AI-assisted (Claude Opus 5, Claude Code)
**Phase / Gate:** G1 — Design freeze (blocked)
**Goal:** Verify the unfetched prior-art leads; establish whether the 8-week / $120 execution
plan is actually executable.

### Done
- Verified all seven round-1 leads plus two newly surfaced ones against primary sources
  (abs pages + full HTML/PDF text, keyword-absence checks). **All nine are real.**
- Fetched and verified Groq deprecations, Groq rate limits, Cerebras rate limits, Google
  rate-limits and pricing, OpenRouter limits, four providers' ToS, Modal pricing, Prolific
  pay policy, and MTurk status — all directly, on 2026-08-07.
- Wrote `docs/03-design/FEASIBILITY-ASSESSMENT.md`.
- Extended `docs/02-literature/PRIOR-ART-REVIEW.md` with rounds 2 and 2b.
- Added `SOP-020 §4.6` and `§4.7` after a verification failure (below).
- Raised `OQ-0031`…`OQ-0041`. Escalated `RK-0005` to **materialised**, severity 25. Added
  `RK-0015` (scoop risk).

### Found

**The primary model dies in nine days.** `llama-3.1-8b-instant` and
`llama-3.3-70b-versatile` both shut down **2026-08-16** — verified directly at
<https://console.groq.com/docs/deprecations>, which states the deprecation *"applies to free
and developer-tier usage"*. `qwen-2.5-32b` has been gone since 2025-04-14. Cerebras no longer
serves any Llama-class model on its free tier. Three of the four models named in SPEC-2's
cohorts are dead or dying.

**Free-tier capacity does not fit, and the request-per-day numbers are a trap.** Groq lists
`llama-3.1-8b-instant` at 14.4K RPD but 500K TPD — 34.7 tokens per request if the RPD cap
were reachable. It is not. Token caps bind everywhere, and multi-turn context re-sends make
it worse than linearly. Corrected volume (~160,000 calls) is roughly 3× over what the
combined free tiers deliver in 56 days.

**One provider's terms prohibit what a paper implies.** Cerebras: users may not use the
service *"for benchmarking or competitive analysis of the Service."* Groq's operative API
terms are not publicly retrievable — silence, not permission. Google's free tier is read by
human reviewers and used for training.

**The compute plan specifies impossible hardware.** SPEC-2 §3.5 assigns Llama-3.1-70B to an
L4 at "~$0.80/hr". The price is exactly right (verified $0.799/hr) — but an L4 has 24 GB and
the model is ~141 GB in bf16. Minimum viable is 2 × A100 80GB at $5.00/hr. Cost is dominated
by warm wall-clock across 675 sequential batch steps, not by tokens, and the uncertainty
range ($100–$300) is wider than the credit pool.

**MTurk closed to new requesters on 2026-07-30.** Prolific's academic fee is 33.3% on top of
rewards; minimum $8/hr, recommended $12/hr. SPEC-3's $0.30/judgement is compliant and in fact
generous; SPEC-4's $40 budget line is wrong under every scenario, and the $120 cash cap is
exceeded in all of them. Separately: reporting on the MTurk closure cites a 2023 finding that
**33–46% of MTurk workers were using LLMs to complete tasks** — a direct threat to the
validity of any human-validation benchmark, whichever platform is used.

**Prior art: all nine leads real, none fatal.** `2601.05606` (the one feared to jointly
pre-empt H1 and H2) came back at threat 3/5 — it varies topology and mixes model families,
but has **no injected misinformation of any kind**. The new highest threat is `2604.26561`
(Sela, Apr 2026): a scale-matched architectural-heterogeneity experiment with p < 0.001 and
effect sizes. It does not run our experiment, but its abstract claims heterogeneity *"does
not reduce convergence"* in accuracy-oriented debate — a direct prior prediction that H1 fails
in our regime (`OQ-0039`) — and that *"8B models exhibit binary rather than graded responses
to counter-arguments"*, which threatens the belief metric at our planned model scale
(`OQ-0038`).

**The strategic picture improved even as the logistics collapsed.** Two 2026 papers now
publish *contradictory* directional results on heterogeneity, and **neither controls for
capability**. That makes the causal isolation — does diversity help at fixed capability? — a
real contribution answering a live disagreement, rather than a first-look question.

**A verification failure worth recording.** A fetch tool's built-in summariser fabricated
`2601.05606`'s entire experimental setup, inverting the single most decision-relevant fact
(it reported separately-run homogeneous groups; the paper mixes families within one network).
Had it been trusted, we would have concluded H1 was pre-empted. Now `SOP-020 §4.6`: never
characterise a paper from a prose summary — extract the text and read it.

### Decided
- No new DRs. The fork (`OQ-0041`, hosted vs self-hosted) needs the project lead.

### Open / Next
- **Blocking on the project lead:** `OQ-0041` (hosting), and the repositioning decision.
- Immediate regardless of that decision: stop naming the deprecated models; read
  `2604.26561` in full; run a token-measurement pilot so §3 and §5 of the feasibility
  assessment can be rebuilt from measurements rather than assumptions.
- Not yet researched (sweep interrupted): workshop deadlines, arXiv `cs.MA` endorsement,
  belief-measurement calibration literature, statistical standards for this class of study.

---

## 2026-08-07 — Session 004: Three strategic decisions and the revised design

**Participant(s):** Project lead (decisions); AI-assisted (Claude Opus 5, Claude Code)
**Phase / Gate:** G1 — Design freeze
**Goal:** Resolve the three forks opened by the feasibility and prior-art findings, and
rewrite the design accordingly.

### Done
- `DR-0005` — self-host small (3–9B) open-weight models on Modal/vLLM; abandon the free-tier
  premise. Substrate choice was delegated; rationale recorded in full.
- `DR-0006` — lead with capability-matched diversity. H1 promoted to sole confirmatory
  hypothesis; H3 retained as a manipulation; H2 demoted to exploratory; **H4 dropped** to
  Future Work.
- `DR-0007` — hold the G1 gate, let the delivery date move. arXiv preprint is the
  deadline-independent deliverable.
- Wrote `docs/03-design/AMD-0001-revised-experimental-design.md`, which supersedes SPEC-1 §3,
  SPEC-2 §3.1/§3.4/§3.5 and SPEC-3 §1.1.
- Closed 13 open questions against these decisions; updated README status.

### Found

The three decisions interact more favourably than expected — each one closes problems raised
by the others.

**Self-hosting dissolves five separate problems at once.** It was chosen for reproducibility,
but it also makes the belief instrument uniform across every agent (the root cause of
`OQ-0002`), removes the ToS conflicts, removes the deprecation exposure, and turns capacity
from a hard rate-limit wall into a cost knob. Five P0/P1 questions closed on one decision.

**The capability control does double duty, and this is a real methodological point worth
making in the paper.** Ensemble-diversity measures are known to be near-collinear with member
accuracy — a diversity statistic can be largely a restatement of `(1 − mean accuracy)`.
Holding `ā` fixed by design breaks that collinearity *by construction*. So the control that
isolates the causal claim is the same control that makes the diversity measure interpretable.
Neither competing paper has it.

**The diversity ladder (`AMD-0001` §3) is both sharper and cheaper than the v1.0 design.**
Five levels — identical / stochastic / persona / architectural / combined — separate
"architectural diversity protects" from "any decorrelation protects", which no prior study
can distinguish because they all compare exactly two configurations. And three of the five
levels run on a single served model, so the marginal serving cost is near zero. If prompting
or sampling diversity turns out to protect as well as architectural diversity, that is a more
*useful* finding than the original hypothesis, and it is currently unknown.

**Dropping H4 cost less than expected.** It had no experimental factor behind it in the first
place (`OQ-0004`), was partly pre-empted by `2606.16710`'s threshold result, and its
conceptual claim was staked in `2605.17353`'s Future Work. Removing it converts a fourth
unfunded hypothesis into a clean Future Work paragraph.

### Decided
`DR-0005`, `DR-0006`, `DR-0007` — see the register.

### Open / Next
G1 checklist is `AMD-0001` §10. In priority order:
1. Read `arXiv:2604.26561` in full — `OQ-0039`. Its abstract may contain a published
   prediction that H1 fails in exactly our regime. This changes the framing either way and
   nothing should be frozen before it is read.
2. Belief-gradedness pre-check — `OQ-0038`. One day. A step-response would make bimodality
   trivially high for reasons unrelated to topology, i.e. it could *manufacture* an H2 result.
3. Fact-suite validation with a preregistered inclusion band — `OQ-0017`. Doubles as the
   isolated control arm and as the capability measurement for `AMD-0001` §4.
4. Token/timing pilot → rebuild the budget from measurements, not assumptions — `OQ-0007`.
5. Power analysis → N and replication count.

Still not researched: workshop deadlines, arXiv `cs.MA` endorsement, belief-calibration
literature, statistical standards. Lower priority now that the gate is held.

---

## 2026-08-07 — Session 005: Reading 2604.26561, and the dependent variable changes

**Participant(s):** Project lead; AI-assisted (Claude Opus 5, Claude Code)
**Phase / Gate:** G1 — Design freeze
**Goal:** Close `OQ-0038` and `OQ-0039` by reading `arXiv:2604.26561` in full — item 1 on the
G1 checklist.

### Done
- Read `2604.26561` in full from the arXiv HTML, extracted and parsed locally with MathML
  preserved. **Not** from a prose summary (SOP-020 §4.6).
- Wrote `docs/02-literature/notes/LIT-0001-sela-preserving-disagreement.md`.
- Closed `OQ-0038` (resolved → DV change) and `OQ-0039` (traced to source).
- Raised `OQ-0042` and `OQ-0043`.
- Revised `AMD-0001` §2 (H1 restated) and §8 (belief instrument).
- Extended the prior-art review with round 2c.

### Found

**`OQ-0039` resolves favourably.** The threatening sentence — heterogeneity *"does not reduce
convergence"* in accuracy-oriented tasks — is **a citation, not Sela's own result.** It traces
to **Fang et al., "A-HMAD" (Springer, Nov 2025)**, which we had never seen. Raised as
`OQ-0042`; it is now the most important paper to obtain.

Better still, Sela offers a *mechanism* for the contrast: *"architectural diversity disrupts
shared inductive bias, which drives artificial consensus only when no objective ground truth
constrains the outcome."* Fang's setting has ground truth and no adversary. Sela's has an
adversary-free setting with no ground truth. **Ours has ground truth *and* an adversary
pushing against it** — the cell neither ran. Sela's theory predicts diversity won't help
there; the cascade mechanism below predicts it will. Adjudicating between them is a genuine
contribution, and it is sharper than the framing we had this morning.

**`OQ-0038` resolves unfavourably for the metric and very favourably for the project.**
Confirmed verbatim from §7.4: 7–9B models respond to counter-arguments **binarily** — maintain
entirely or capitulate entirely, with *"the absence of a 'consider and reject' middle state"*
described as *"a robust characteristic of the 7–9B parameter range."* DR-0005 selected exactly
that range, so the graded credence would have been measuring probe noise.

**But the next paragraph is the most useful thing found in this entire review:**

> *"Any multi-agent architecture that exposes small-model agents to arguments from other agents
> risks inducing **capitulation cascades**, where the first agent to encounter a persuasive
> argument flips, creating a feedback loop. Architectural designs that preserve agent isolation
> during evaluation — as our system does — are necessary safeguards at this model scale."*

Sela names our phenomenon, identifies its mechanism, calls it a hazard — **and designs around
it rather than studying it.** That is the contribution restated in a competitor's words.

**Consequence: the dependent variable changes.** From a graded credence to a **discrete belief
state analysed by survival methods** — time-to-capitulation, hazard rate, recovery rate. This
is better on four counts, not a retreat: it matches the model class's actual behaviour; it fits
the epidemiological framing *better* than a continuous DV inside a compartmental metaphor; it
is cheaper, relieving `OQ-0007`; and it removes an artefact where a step response could have
made bimodality trivially high and **manufactured** an H2 confirmation.

**A third find reframes the analysis.** Huang et al. (2025) *prove multi-agent debate is a
martingale on belief in the correct answer* — no expected gain over independent voting
(`OQ-0043`). If that holds, the no-injection control arm has a **theoretical prediction** to be
checked against, which almost no simulation paper has. It also relocates H1: if the mean is a
martingale, the action is in **variance and tails** — cascades, capitulation, recovery — not
mean belief.

**Also recovered:** a validated 7–9B model pool running locally via Ollama on consumer
hardware (Qwen3-8B, Mistral-NeMo, Mistral-7B-Instruct-v0.3, Qwen2.5-Coder-7B, Dolphin3-8B,
DeepSeek-R1-8B, Gemma2-9B) — directly reusable under DR-0005, and using it makes our results
comparable to theirs. And Li et al. (arXiv:2509.05396) find weak models in heterogeneous debate
can *degrade* outcomes — a competing explanation for Fang's null that capability matching must
separate out.

### Decided
No new DRs. The DV change is carried in `AMD-0001` §8 and needs a DR once the pilot confirms
the discreteness in our own models — it should not be frozen on one paper's evidence.

### Open / Next
1. **Obtain Fang et al., "A-HMAD"** — `OQ-0042`. Springer, Nov 2025; not yet located.
2. Obtain Huang et al., "Debate or vote" — `OQ-0043`.
3. State-discreteness pre-check in our own models — converts `AMD-0001` §8 from borrowed
   evidence to measured evidence.
4. Rewrite `DRAFT-metric-definitions.md` for a discrete-state DV; D1–D7 need revisiting.
5. Then: fact-suite validation, token/timing pilot, power analysis.

---

## 2026-08-07 — Session 004: Reframe signed off, compute lost, A-HMAD threat dissolved

**Participant(s):** Project lead; AI-assisted (Claude Opus 5, Claude Code)
**Phase / Gate:** G1 — design freeze
**Goal:** Act on the project lead's decisions; begin Phase A (desk work).

### Done
- Initialised `git`; added the GitHub remote
  (`Abhijit89Kumar/Diversity-as-a-Defense-Against-Misinformation-in-LLM-Societies`).
  Committed locally. **Not pushed** — see Open/Next.
- Recorded `DR-0008` (reframe to multi-round cascade dynamics — project lead sign-off) and
  `DR-0009` (compute unfunded; sequence GPU-free work first, amends `DR-0005`).
- **A2 complete.** Obtained and read the A-HMAD paper in full from the open-access PDF.
  Wrote `LIT-0002`.
- Closed `OQ-0042`, `OQ-0044`, `OQ-0045`. Raised `OQ-0046`, `OQ-0047`, `OQ-0048`.

### Found

**The strongest published threat to H1 does not exist.** `OQ-0042` recorded A-HMAD as
*"Fang, Yizuo, et al."*, testing architectural heterogeneity, reporting a **null** in the
accuracy-oriented regime. The paper is **Zhou, Yan & Chen, Yanguang**, *J. King Saud Univ.
CIS* 37:330 (2025), DOI 10.1007/s44443-025-00353-3. Reading it:

- Its heterogeneity is **role/prompt on a single base model** (Llama-2 70B-chat), not
  architectural. Verbatim §3.3: *"Agents share the same base model architecture but are given
  different role instructions in their prompt"*, and *"In our experiments, we primarily use the
  same model class for a fair comparison."*
- Its DV is **task accuracy**, not convergence.
- Its result is **positive**: +4–6 pp over standard debate; the heterogeneity ablation is worth
  up to 3.5%.
- There is **no misinformation anywhere** in it (`misinform` = 0 hits in the full text).

So it cannot support the claim attributed to it in `OQ-0039` — it measures neither convergence
nor architectural diversity. Threat downgraded 4/5 → 1/5.

**Third mischaracterisation in this review.** First a fetch-tool summariser inverted
`2601.05606`'s setup; then a peer-reviewed related-work sentence mis-stated this paper's
finding; and the same citation carried the **wrong author names**. Whether that originated in
Sela's bibliography or in our transcription is `[UNVERIFIED]`. The standing rule (SOP-020 §4.6,
§4.7) has now paid for itself three times.

**It also handed us a confound we had not excluded.** Role/prompt heterogeneity alone is worth
up to 3.5% on the same base model. If our heterogeneous cohorts differ in persona or prompt as
well as in weights, H1 is unidentifiable. Prompts must be byte-identical across agents, with
the seeded persona the single deliberate exception (`OQ-0046`).

**Compute is gone.** The $280 Modal pool expired ~2 months ago. `DR-0005`'s technical
reasoning is untouched — the substrate is still right — but it is unfunded (`OQ-0048`).

**And the loss is smaller than it looks.** Modal's Starter plan carries **$30/month in
recurring free credits** (verified 2026-08-07 at <https://modal.com/pricing>) ≈ 37 L4-hours or
27 A10-hours per month. `EXP-000` is estimated at 4–6 GPU-hours ≈ $4–6 — `[UNVERIFIED]`,
assumptions in `OQ-0048`, to be replaced by measurement. **The experiment that closes six G1
items appears affordable today with no grant and no out-of-pocket spend.** G1 is not
compute-blocked.

### Decided
- `DR-0008` — reframe to cascade dynamics; T becomes a first-class IV; primary outcomes become
  tail/dynamic quantities rather than means.
- `DR-0009` — build the engine against a deterministic stub agent so the whole pipeline is
  testable with zero inference; defer `EXP-000` behind funding but scope it to the free credit.

### Open / Next
- **Push to GitHub is not done and needs a decision** — public vs private matters here, given
  `RK-0015` (an established lab announced our axes as their next step). A public repo timestamps
  the work but also advertises the direction.
- Continue Phase A: A3 (rewrite metric definitions for the discrete-state DV under the cascade
  reframe), A4 (communication-budget convention), A5 (positioning statement), A6 (G1 checklist).
- Obtain arXiv:2509.05396 (`OQ-0047`) — the weak-models-degrade-debate competing explanation.
- Then Phase B engineering, all of which is GPU-free.

---

## 2026-08-07 — Session 005: Phase A complete, Phase B analysis core, two validation experiments

**Participant(s):** Project lead; AI-assisted (Claude Opus 5, Claude Code)
**Phase / Gate:** G1 — design freeze
**Goal:** Execute the project lead's decisions; complete Phase A desk work; begin Phase B
engineering, all GPU-free per `DR-0009`.

### Done
- **Git live and public.** Two commits re-attributed to the personal account, remote pushed.
  Now at 10 commits.
- **Phase A complete.** `AMD-0002` (metrics and analysis plan) supersedes the pre-reframe
  draft; communication-budget convention fixed; positioning statement v1.0 FINAL;
  `G1-GATE-CHECKLIST.md` created with GPU dependency flagged per row.
- **Phase B analysis core built and tested.** `types.py`, `metrics.py`,
  `analysis/survival.py`, `analysis/synthetic.py`; 25 tests passing (22 fast, 3 Monte Carlo).
- **`EXP-A01`** — planted-effect validation. **`EXP-A02`** — power analysis.
- Design documents: `MODEL-POOL.md`, `CONSTRUCT-VALIDITY-BELIEF-METRIC.md`,
  `RELEASE-SCOPE-AND-DUAL-USE.md`, `fact-suite/` (31 candidates).
- `DR-0008`…`DR-0011`. G1 checklist: **10 of 18 rows closed.**

### Found

**The A-HMAD threat did not exist.** Recorded as *"Fang, Yizuo et al."*, architectural
heterogeneity, **null** result. It is **Zhou & Chen**, *role/prompt* heterogeneity on one base
model (Llama-2 70B-chat), a **positive** result, with **no misinformation anywhere**
(`LIT-0002`). It cannot support the claim attributed to it. Threat 4/5 → 1/5.

**The martingale citation was also wrong** — Choi, Zhu & Li (arXiv:2508.17536), not the
recorded authors. But the claim verifies, and it hands us `AMD-0002 §5`'s theoretical
prediction for the negative control (`LIT-0003`).

**That is four mis-citations traced in this review**, two of them from a peer-reviewed
bibliography. SOP-020 §4.6–4.7 has now paid for itself repeatedly.

**And the best framing result so far.** The martingale is scoped to *"homogeneous agents and
uniform belief updates"* (`LIT-0004`, Zhu et al., a Tier-A paper neither earlier sweep found).
Our design violates the first condition **by construction**. H1 is therefore no longer an
empirical hunch — it is a well-posed theoretical question with a proved null: *does
architectural heterogeneity break the martingale, and does it break toward truth under an
adversary?* (`OQ-0050`.)

**`EXP-A01` — the pipeline does not manufacture significance.** Bias ≤ 3% of a planted −1.2;
cluster-robust SE / empirical SD ∈ [0.94, 1.07]; false-positive rate on null data 0.060–0.067
against nominal 0.05. **And with naive standard errors the false-positive rate doubles to
0.120** under run-level frailty — the regime our design is actually in. A fifth of
"significant" findings at α = 0.05 would have been noise. `OQ-0006` measured, not asserted.

**`EXP-A02` — the proposed SESOI was unreachable.** HR 0.80 needs ~600 runs; 200 gives 40%
power. Revised to **HR 0.67**, justified against published effect sizes and achievable at
~140 runs. Three further results:
- **T is power-neutral.** T = 3 → 10 multiplies events 2.4× and moves power 0.92 → 0.97,
  because extra rounds add *correlated* agent-rounds. **So T is set by cascade science alone.**
- **Runs > N > T** for power per unit cost, because runs are the clustering unit. When compute
  shrinks, cut N and T before cutting runs.
- **N = 20 is adequate** (0.92 at 120 runs), closing `OQ-0032`.

**The model pool improved by being constrained.** Four Apache-2.0, ungated families —
Qwen2.5-7B, Mistral-7B-v0.3, OLMo-2-7B, Granite-3.3-8B. Llama and Gemma are excluded: both
gated, both carrying acceptable-use policies, and fetching the Llama 3.1 policy returns
**HTTP 401 — the terms governing use are themselves behind the gate.** Apache-2.0 imposes no
use restrictions, so `OQ-0040` does not arise for the pool we will run.

**A failing test surfaced a design decision, not a bug.** Seeded agents must be excluded from
state assortativity: they are pinned to CAPITULATED, so including them would make the
echo-chamber metric a function of seed placement and degree — which differ by topology, and
H2 *is* the topology comparison.

### Decided
- `DR-0008` reframe (project lead sign-off) · `DR-0009` compute unfunded, sequence GPU-free
  work · `DR-0010` develop in public · `DR-0011` release scope: ship the framework and
  benchmark, withhold tuned persuasion prompts.

### Open / Next
- **`EXP-000` is the whole remaining GPU dependency** — it satisfies five G1 rows at once
  (B6, C3, D1, D2, E1) for an estimated $4–6 within the free monthly credit.
- Next GPU-free work: the simulation engine against a deterministic stub agent; prompt
  templates (`OQ-0046`); the confound register (B7); A1's systematic channel coverage.
- Read in full: `2601.19921` and `2508.17536` — `OQ-0050`'s hook depends on their assumptions.

---
