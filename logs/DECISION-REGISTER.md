# Decision Register

Append-only. Never renumber, never delete. Supersede with a new record.
Template: `meta/templates/decision-record.md`. Rules: SOP-010 §1.2.

| ID | Date | Title | Status |
|---|---|---|---|
| DR-0001 | 2026-08-07 | Adopt a governed repository structure and SOP set | ACCEPTED |
| DR-0002 | 2026-08-07 | Treat the v1.0 documents as source of record, not working drafts | ACCEPTED |
| DR-0003 | 2026-08-07 | Insert a design-freeze gate (G1) before any engineering | ACCEPTED |
| DR-0004 | 2026-08-07 | Commit in advance to publishing null results as null | ACCEPTED |
| DR-0005 | 2026-08-07 | Self-host small open-weight models; abandon the free-tier premise | ACCEPTED |
| DR-0006 | 2026-08-07 | Lead with capability-matched diversity; demote H2 and H4 | ACCEPTED |
| DR-0007 | 2026-08-07 | Hold the G1 gate; let the delivery date move | ACCEPTED |
| DR-0008 | 2026-08-07 | Reframe the contribution to multi-round cascade dynamics | ACCEPTED |
| DR-0009 | 2026-08-07 | Compute unfunded — sequence GPU-free work first; amends DR-0005 | ACCEPTED |
| DR-0010 | 2026-08-07 | Develop in public from day one | ACCEPTED |
| DR-0011 | 2026-08-07 | Release scope: ship the framework, withhold tuned persuasion prompts | ACCEPTED |

---

## DR-0001 — Adopt a governed repository structure and SOP set

**Date:** 2026-08-07 · **Status:** ACCEPTED · **Decided by:** Project lead, AI-assisted session

**Context.** The project arrived as four specification documents with no repository,
no version control, no logging, and no defined method for making or recording
decisions. The stated intent is that this folder become the single knowledge source,
lab notebook, and codebase for an 8-week research project targeting a workshop
submission and an arXiv preprint.

**Options considered.**
1. *Start engineering immediately from SPEC-2.* Fastest to visible progress. Rejected:
   the specs contain at least seven P0-severity issues (see `OPEN-QUESTIONS.md`) that
   would each invalidate results after the compute was already spent.
2. *Lightweight structure — a README and a notes file.* Low overhead. Rejected: it
   provides no defence against the specific failure modes that kill first papers
   (unchecked novelty, post-hoc analysis, irreproducible runs).
3. *Full governed structure with SOPs, registers, and phase gates.* Chosen.

**Decision.** Adopt the structure in SOP-000 §4, the nine principles in SOP-000 §2, the
SOP set SOP-010…SOP-080, the identifier scheme in SOP-000 §5, and the phase gates in
SOP-000 §6.

**Consequences.**
- *Good:* decisions become traceable; the preregistration mechanism blocks post-hoc
  analysis; the reproducibility requirements make the release credible; the registers
  make it obvious what is unresolved.
- *Cost:* real overhead — roughly a day of setup and ongoing discipline per session.
  This is deliberate and is the point of P9.
- *Risk:* process can become theatre. Mitigation: every register entry must be actionable
  or be closed. If a register stops changing, it is being ignored, and that is itself a
  signal to raise at the next gate.

---

## DR-0002 — Treat the v1.0 documents as source of record

**Date:** 2026-08-07 · **Status:** ACCEPTED

**Context.** The four `.docx` files define the project. They also contain errors we
intend to correct. Editing them in place would erase the record of what was originally
intended, and would make it impossible to show a reviewer (or ourselves) how the design
evolved.

**Decision.** The originals are preserved verbatim in
`docs/01-specifications/source-docx/`, with faithful Markdown conversions alongside,
marked read-only. All corrections are **amendments** (`AMD-xxxx`) in `docs/03-design/`,
each backed by a decision record. The v1.0 specs are never edited.

**Consequences.** Slightly more indirection when reading the current design — mitigated
by keeping a single consolidated current-design document in `docs/03-design/` once
amendments accumulate. In exchange, design drift is fully visible and the eventual
paper can state honestly what was planned versus what was done.

---

## DR-0003 — Insert a design-freeze gate (G1) before any engineering

**Date:** 2026-08-07 · **Status:** ACCEPTED

**Context.** SPEC-4 Phase 1 begins with implementation in weeks 1–2. Auditing the specs
surfaced issues that are cheap to fix now and very expensive to fix after 405 runs have
been executed — chiefly: the belief probe measures a different model than the agent in
the heterogeneous condition (OQ-0002); the primary metrics have no definitions
(OQ-0003); H4 has no experiment behind it (OQ-0004); the call-volume estimate that the
entire budget rests on appears ~4× low (OQ-0007); and the novelty of the contribution
has not been checked against 2024–2026 literature (OQ-0001).

**Options considered.**
1. *Build in parallel with resolving these.* Tempting given an 8-week clock. Rejected
   for the metric and probe questions specifically, because they determine what the
   engine must produce. Partially adopted: infrastructure that is invariant to those
   answers (repo scaffolding, config schema, topology builders, logging, test harness)
   may proceed in parallel.
2. *Resolve everything first.* Chosen for design-critical items only.

**Decision.** No confirmatory compute is spent until G1 is passed: prior-art review
complete with a written positioning statement, every P0 question closed, and a
construct-validity argument for the belief metric written. Non-design-critical
engineering may proceed in parallel.

**Consequences.** Reduces available execution time. Accepted — SOP-000 P9: under time
pressure we cut scope, not method. If the schedule compresses, the response is fewer
facts, fewer topologies, or fewer conditions, reported as a limitation.

---

## DR-0004 — Commit in advance to publishing null results as null

**Date:** 2026-08-07 · **Status:** ACCEPTED

**Context.** SPEC-4 §6 Risk 3 states that "negative or neutral findings will be framed
as a discovery regarding model alignment convergence rather than failure, preserving
paper publishability." Read charitably this is a sensible observation that a null result
is still interesting. Read as written, it is a plan to change the story after seeing the
data, which is the mechanism behind a large fraction of irreproducible results and is
something reviewers actively look for.

**Decision.** We commit now, before the data exists:
- If H1 is not supported, the paper's results section states that H1 is not supported,
  with the effect size and its confidence interval.
- A null result on H1 may be *interpreted* in the discussion as evidence about alignment
  convergence between model families. That interpretation is labelled as post-hoc.
- The preregistration is frozen and hashed before confirmatory data collection, so the
  distinction between planned and post-hoc is checkable rather than a matter of memory.
- Claims of "no effect" use equivalence testing against a preregistered smallest effect
  size of interest, not `p > α` (SOP-060 §4).

**Consequences.** Removes the option of a convenient rewrite. In exchange, the framework,
the metric-validation work, and the benchmark remain publishable contributions
regardless of which way H1 falls — which is the actual reason this project is safe to
run on an 8-week clock. Supersedes the operational reading of SPEC-4 §6 Risk 3.

---

## DR-0005 — Self-host small open-weight models; abandon the free-tier premise

**Date:** 2026-08-07 · **Status:** ACCEPTED · **Decided by:** Project lead (choice delegated), AI-assisted session
**Closes:** OQ-0041 · **Partially closes:** OQ-0002, OQ-0013, OQ-0018 · **Affects:** SPEC-2 entirely, SPEC-3 §1.1, SPEC-4 §4

**Context.** `docs/03-design/FEASIBILITY-ASSESSMENT.md` (all figures verified 2026-08-07)
established that the free-tier substrate fails on five independent axes simultaneously:

- `llama-3.1-8b-instant` and `llama-3.3-70b-versatile` shut down **2026-08-16**;
  `qwen-2.5-32b` gone since 2025-04-14; Cerebras serves no Llama-class model.
- Corrected call volume (~160,000) exceeds combined free-tier **token**/day caps by ~3x.
- Cerebras's ToS prohibits "benchmarking or competitive analysis of the Service".
- Groq's operative API terms are not publicly retrievable — unknown, not permissive.
- Closed APIs cannot supply logprobs uniformly, which is the root cause of OQ-0002.

**Options considered.**
1. *Stay hosted, swap to replacement models.* Cheapest in cash. Rejected: token caps still
   leave the design ~3x short; churn recurs every 6–10 months so a mid-flight retirement must
   be assumed again; Groq's terms remain unread; and gathering enough capacity requires
   sharding agents across providers, which **aliases model identity with provider** — a fatal
   confound for a belief-dynamics dependent variable.
2. *Pay for a Groq Developer plan.* Removes daily caps. Rejected as primary: the Aug-16
   deprecation explicitly applies to developer tier, so it fixes neither model permanence,
   nor the unread terms, nor the missing logprobs.
3. *Hybrid — self-host core arms, one permitted hosted API for diversity.* Attractive because
   it keeps a genuinely different model family in the mix. Rejected as default: reintroduces
   non-reproducibility and a provider confound **in exactly the arm H1 depends on**. Retained
   as a possible robustness check, never a primary condition.
4. *Self-host small open weights on Modal.* Chosen.

**Decision.** All agent models are open-weight, self-hosted on Modal with vLLM, in the
**3–9B class**. No confirmatory condition depends on a hosted commercial API.

Rationale, in order of weight:
- **Weights are permanent.** A deprecation cannot invalidate a run. This is a reproducibility
  argument (SOP-040 §2), not a convenience one.
- **Logprobs are uniform across every agent**, so the belief instrument is identical in every
  condition. Dissolves OQ-0002 at the root rather than working around it.
- **No ToS ambiguity.** Open weights under their own licences; no benchmarking clause, no
  human review of prompts, no training on our data.
- **No rate limits** — capacity becomes a cost question with a knob, not a hard wall.
- **The 3–9B class is right for the science, not a compromise.** The capability-matched design
  (DR-0006) needs many cohorts spanning a diversity range, affordable only with small models.
  Precedent: `2605.17353` ran N=200 agents on 3–4B backbones.

**Consequences.**
- *Good:* reproducible; uniform instrument; no legal grey area; no deprecation exposure; run
  count becomes a budget decision instead of a rate-limit lottery.
- *Cost:* the "$0.00 text generation" line in SPEC-4 §4 is void. The $280 Modal pool becomes
  the real compute budget. Adds vLLM/Modal serving orchestration.
- *Cost:* frontier-scale models leave the study. Claims are scoped to small open-weight models
  and Limitations must say so. This is an honest narrowing to the same scope as the closest
  comparable work.
- *Risk:* serving cost is dominated by warm wall-clock across sequential rounds, not tokens,
  and is unquantified. **Trigger:** the timing pilot must produce a measured cost-per-run
  before any matrix launch (G3).
- *Reversibility:* cheap — nothing prevents adding a hosted-API robustness arm later.

**Follow-ups.**
- [ ] Supersede SPEC-2 §3.4 (`router.py`) and §3.5 (`modal_prober.py`) via AMD-0001.
- [ ] Cost the serving plan; rebuild the budget from measured pilot figures.
- [ ] Verify current availability and licence terms of each candidate model `[UNVERIFIED]`.

---

## DR-0006 — Lead with capability-matched diversity; demote H2 and H4

**Date:** 2026-08-07 · **Status:** ACCEPTED · **Decided by:** Project lead
**Closes:** part of OQ-0001 · **Affects:** SPEC-1 §3 (all four hypotheses), SPEC-3 §1.1

**Context.** The prior-art review established that the generic framing is published several
times over, the topology axis is thoroughly occupied, and H4 is partly pre-empted. It also
established something more useful: **two 2026 papers publish contradictory directional results
on model heterogeneity, and neither controls for capability.**

- `2606.03032` §5.4: cross-series agents retain more critical facts than same-series
  (.598 vs .357) — but their same-series arm contains GPT-3.5-turbo, so it is
  capability-degraded, not matched.
- `2601.05606`: "the accuracy of the emergent consensus is ultimately determined by the
  capability of the prevailing model class"; "peripheral diversity does not reliably
  compensate for central incompetence" — also capability-confounded.
- `2604.26561` runs a scale-matched (7–9B) heterogeneity design with p < 0.001, but on
  value-laden policy deliberation with no ground truth, and asserts heterogeneity "does not
  reduce convergence" in accuracy-oriented settings (OQ-0039).

**Options considered.**
1. *Keep all four hypotheses, cut scale instead.* Rejected: H2 is the weakest axis, H4 is
   partly pre-empted, and four hypotheses on a compressed timeline risks none being convincing.
2. *Lead with the measurement protocol and benchmark.* Genuinely safer against scooping, since
   an instrument stays useful regardless. Retained as the **fallback position** if H1 is
   pre-empted before submission (RK-0001, RK-0015).
3. *Lead with capability-matched diversity.* Chosen.

**Decision.** The primary contribution is the **causal isolation of diversity from capability**
under adversarial misinformation injection.

- **H1 is promoted to the sole confirmatory hypothesis**, restated over a *measured, continuous*
  diversity quantity at *matched aggregate capability*.
- **H3 is retained but converted from a regression to a manipulation** (OQ-0011) — hold argument
  content fixed, vary stated certainty. Confirmatory, secondary.
- **H2 is demoted to exploratory.** Topology becomes a factor to report and control, not a
  headline claim. Its bimodality framing is dropped unless the pilot shows N is adequate
  (OQ-0032) and the directional conflict with `2512.18094` is resolved (OQ-0033).
- **H4 is dropped from this paper**, moved to Future Work. It has no experimental factor
  (OQ-0004), is partly pre-empted by `2606.16710`'s threshold result, and is conceptually
  staked by `2605.17353`'s Future Work. A density sweep would now cost more than it buys.

**Consequences.**
- *Good:* the paper answers a live, documented disagreement rather than asking a first-look
  question. Neither competing group can retrofit a capability control cheaply. The
  heterogeneity x adversary cell is genuinely empty.
- *Good:* one confirmatory hypothesis makes the multiple-comparison family small and the power
  analysis tractable.
- *Cost:* the title's promise narrows. "Diversity as a Defense" must not be oversold beyond
  small open-weight models on a factual-claim suite.
- *Risk:* OQ-0039 may contain a published prediction that H1 fails in exactly our regime.
  **This is acceptable and arguably good** — under DR-0004 a null becomes a *confirmation* of
  an existing prediction with a cleaner design, which is publishable. But `2604.26561` must be
  read in full before the preregistration is written.

**Follow-ups.**
- [ ] Read `2604.26561` in full; resolve OQ-0039.
- [ ] Restate H1 formally over measured diversity at matched capability (AMD-0001).
- [ ] Pre-commit the direction of the H1 prediction (OQ-0029).

---

## DR-0007 — Hold the G1 gate; let the delivery date move

**Date:** 2026-08-07 · **Status:** ACCEPTED · **Decided by:** Project lead
**Affects:** SPEC-4 §2 (8-week roadmap)

**Context.** SPEC-4's 8-week plan from 2026-08-07 ends ~2026-10-02. The design freeze is not
done: ten P0 open questions are live, the belief instrument is unresolved, the substrate has
just changed (DR-0005), and the hypothesis set has just changed (DR-0006). Launching a
confirmatory matrix on that basis would spend the entire compute budget on a design with known
holes.

**Decision.** G1 is held until its evidence requirements are met. The delivery date is
re-derived afterwards, not before. Per SOP-000 P9, schedule pressure changes **scope**, never
method: if time compresses we drop conditions and report it as a limitation.

The **arXiv preprint is the deadline-independent artefact** and the primary portfolio
deliverable. Workshop submission is opportunistic against whatever window is open when the work
is genuinely ready.

**Consequences.**
- *Good:* removes the incentive to launch early with an unresolved dependent variable — the
  single most expensive mistake available.
- *Cost:* no committed submission date. Mitigated by treating the preprint as the deliverable.
- *Risk:* RK-0015 — Becker et al. announced our axes as their next step in June 2026, so delay
  carries real scoop exposure. **Mitigation:** the two-stage option stays available and is
  revisited at G2 — if the pilot produces a clean result, a short preprint staking the
  measurement protocol and a pilot-scale finding can go out while the full matrix runs.
  **Trigger:** any new arXiv listing from that group, or any paper crossing both the
  heterogeneity and misinformation axes.
- *Risk:* an open-ended schedule can drift. **Mitigation:** G1 carries a written evidence
  checklist; progress against it is reviewed in every research-log entry.

---

## DR-0008 — Reframe the contribution to multi-round cascade dynamics

**Date:** 2026-08-07 · **Status:** ACCEPTED · **Decided by:** Project lead (explicit sign-off)
**Closes:** OQ-0044 · **Affects:** H1 framing, the paper's central question, AMD-0001 §2

**Context.** Nilayam, Ramanna, Tumbade & Nayak (ServiceNow), *"Heterogeneous LLM Debate Under
Adversarial Peers: Honest Gains, Replacement Costs, and Resilience"* (arXiv:2606.19826,
18 June 2026) concludes: *"Heterogeneity is therefore not only an attack surface but, when an
adversary is already present, also a defense."* That is H1's headline, in an accuracy-oriented
setting, with an adversary, seven weeks before this decision.

But they measure **exactly one revision step (R0→R1)**, and say why:
*"later rounds compound direct peer influence with path dependence."*

Sela (`2604.26561`) independently flags capitulation cascades and designs around them.
**Two independent groups identified multi-round cascade behaviour as the complication they
were avoiding.** The unexploited problem is the dynamics, not the one-step effect.

Separately, Huang et al. (`OQ-0043`) reportedly prove debate is a **martingale on belief in the
correct answer** — no expected gain over independent voting. If that holds, the mean is
uninformative by construction and the entire signal lives in the variance and the tails.

**Options considered.**
1. **Reframe to cascade dynamics.** Keep the design; restate the question as whether the
   published single-step protection survives multi-round propagation at matched capability.
2. Pivot to the measurement/benchmark contribution as primary (the DR-0006 fallback).
3. Contest the capability confound head-on as the primary contribution.

**Decision.** Adopt **1, composed with 3** — they are one paper. The central question becomes:

> Single-step heterogeneity benefits under adversarial peers are published. **Do they survive
> multi-round cascade dynamics, and do they survive capability matching?**

Consequences for the design, to be carried into AMD-0001 and the preregistration:
- **T is a first-class independent variable**, not a fixed constant. The R0→R1 step is the
  published baseline we replicate; rounds 2…T are the contribution.
- **The primary outcomes are tail and dynamic quantities**, not means: capitulation-cascade
  incidence, time-to-capitulation, cascade size distribution, recovery rate, and the
  probability of irreversible collapse. If the mean is a martingale, reporting the mean as the
  headline would be reporting a theorem.
- The no-injection arm inherits a **theoretical prediction** (flat expected belief) rather than
  a merely descriptive one — a genuine advantage over comparable simulation papers.
- Capability matching remains the control that distinguishes this from all four published
  heterogeneity results.

**Consequences.**
- *Good:* the question is sharper, is not pre-empted, and is one two independent groups have
  implicitly posed. Being second on the one-step result is now an asset — it is the baseline
  we build on and cite.
- *Cost:* T must extend far enough for cascades to develop, which raises per-run cost at the
  moment compute is unfunded (DR-0009). Expect to trade cells for rounds.
- *Risk:* if cascades do not occur at reachable T, the contribution weakens. Mitigation: the
  pilot measures cascade onset before the matrix is designed; if onset is late, that is itself
  a reportable finding about the stability of these systems.
- *Reversibility:* cheap. No engineering is committed to the old framing.

**Note.** This does not invalidate prior work in this repository. The substrate decision,
the discrete-state DV, the capability-matching protocol and the diversity ladder are all
unaffected. Only the framing of the question changed, and it changed toward something sharper.

---

## DR-0009 — Compute is unfunded; sequence GPU-free work first

**Date:** 2026-08-07 · **Status:** ACCEPTED · **Decided by:** Project lead
**Amends:** DR-0005 (does not supersede it) · **Raises:** OQ-0048

**Context.** DR-0005 committed to self-hosting small open weights on Modal, funded by a $280
credit pool. The project lead has reported that **those credits expired roughly two months
ago.** Grants and an institutional contact are being pursued; nothing is confirmed.

DR-0005's technical reasoning is unaffected — free-tier hosting still fails on model
deprecation, token caps, ToS, and logprob availability (`FEASIBILITY-ASSESSMENT.md`). The
substrate is still correct. It is simply not funded.

**Options considered.**
1. *Revert to free-tier hosting.* Rejected: every reason in DR-0005 still holds, and the
   primary model was deprecated on 2026-08-16 regardless.
2. *Halt until compute is secured.* Rejected: most of the critical path to G1 does not need a
   GPU, and halting would waste the window while grants are pursued.
3. **Sequence GPU-free work first and hold GPU work behind funding.** Chosen.

**Decision.**
- All Phase-A desk work and all Phase-B engineering proceed now. Both are GPU-free.
- The engine is built against a **deterministic stub agent** so the full pipeline — topology,
  memory operator, scheduling, logging, metrics, analysis — is exercised and tested end to end
  with no inference at all. The planted-effect synthetic-data test (SOP-040 §3, SOP-060 §8) is
  the highest-value guard in the project and needs zero compute.
- `EXP-000` is deferred until compute exists, but is **scoped to fit Modal's recurring free
  $30/month Starter credit** (verified 2026-08-07 at <https://modal.com/pricing>), estimated at
  4–6 GPU-hours ≈ $4–6 (`OQ-0048`, assumptions shown, to be replaced by measurement).
- Model choice is deferred but constrained to the 7–9B open-weight class, which an L4 or A10
  can serve.

**Consequences.**
- *Good:* G1 is not compute-blocked. The stub-agent discipline is better engineering than we
  would have chosen under abundance — it forces a clean separation between the simulation
  engine and the inference backend, which is exactly what makes the released package reusable.
- *Cost:* `EXP-000` slips, so the power analysis and the final N slip with it. Consistent with
  DR-0007 — the gate is held, the date moves.
- *Risk:* if no compute materialises, the project caps out at a design-and-framework
  contribution. That remains publishable (DR-0006 fallback) but is a weaker paper.
  **Trigger:** no funded compute by the time Phase B is complete → re-plan scope explicitly.
- *Reversibility:* fully reversible the moment compute is funded.

**A note on scale, recorded so it is not forgotten under funding pressure.** Published
comparators run N=4 (`2606.03032`), N=7 (`2601.05606`), and 3–6 agents (`2506.00509`).
A well-controlled study at N=20 with capability matching would be larger and better controlled
than most of them. **Scarce compute is a reason to cut cells, not to cut rigour** (SOP-000 P9).

---

## DR-0010 — Develop in public from day one

**Date:** 2026-08-07 · **Status:** ACCEPTED · **Decided by:** Project lead
**Affects:** OQ-0022 (dual-use release policy), RK-0015 (scoop risk), SOP-070 §6, SOP-080 §4

**Context.** The repository is pushed to a **public** GitHub repo from the foundation stage,
well before the preprint. The alternative considered was private-until-preprint, on the
grounds that `RK-0015` records an established lab (GippLab) publicly naming both of this
project's axes as their next step, and a second group (ServiceNow) publishing the single-step
result seven weeks ago. A public repository advertises the direction — including the
cascade-dynamics reframe — to better-resourced groups.

**Decision.** Public, from now. The project lead's stated rationale: *"I am here to learn and
contribute, not to compete."*

**Consequences.**
- *Good:* a public, timestamped, append-only record of decisions and negative findings is
  itself a credible artefact — arguably more informative about research capability than the
  eventual paper, because it shows the reasoning and the corrections. It makes the
  reproducibility commitments in SOP-040 checkable by anyone. And it removes any temptation to
  quietly revise history, which is the whole point of the append-only registers.
- *Cost:* no protection against being scooped beyond the commit timestamp. Accepted
  deliberately.
- *Risk — brought forward, not created:* the dual-use question in `OQ-0022` and SOP-080 §4 was
  scoped as a *release-time* decision. Public-from-day-one moves it earlier: it becomes live
  **when the first agent-facing code lands**, not at submission. Nothing currently in the
  repository is operational — specifications, governance, and literature notes only — so there
  is no issue today. But before `src/` contains a working injection harness, the release-scope
  decision in `OQ-0022` must be made rather than deferred.
- *Mitigation already in place:* the fact suite is deliberately absurd, verifiable falsehoods
  about physics and arithmetic, not socially charged disinformation (SOP-080 §4). Keep it that
  way; it is what makes public development unproblematic here.

**Follow-up.** Raise the priority of `OQ-0022` from P2 to P1 and re-scope its trigger from
"before release" to "before the first agent-facing code is committed".

---

## DR-0011 — Release scope: ship the framework, withhold tuned persuasion prompts

**Date:** 2026-08-07 · **Status:** ACCEPTED
**Closes:** OQ-0022 · **Satisfies:** G1 checklist row E6 · **Affects:** SOP-080 §4, all released artefacts

**Context.** `DR-0010` made the repository public from the foundation stage, which moved the
dual-use decision from release time to **before the first agent-facing code is committed**.
That code is imminent, so the position is settled now rather than deferred.

The artefact genuinely is dual-use: it includes an injection harness that instructs an agent
to argue persuasively for a false claim, a corpus of paired true/false claims with authority
framing, and measurements of which structures spread falsehood fastest.

**Options considered.**
1. *Withhold everything until publication.* Rejected — contradicts DR-0010 and provides no
   real protection, since the underlying capability is one sentence in a system prompt.
2. *Release everything, including any prompt-efficacy findings.* Rejected — see the
   distinction in the decision below.
3. **Release the framework, benchmark, harness and data; withhold optimised persuasion
   prompts and any search procedure that produces them.** Chosen.

**Decision.** Full scope table in `docs/03-design/RELEASE-SCOPE-AND-DUAL-USE.md` §4. The
operative line:

> *"High stated certainty increases belief shift by X, holding content fixed"* is a
> **finding**. *"Here are the twenty prompts that most reliably flip an 8B agent, in order"*
> is a **capability uplift**.

The first informs defences. The second transfers with no adaptation and does nothing for a
defender that the aggregate finding does not already do. We publish the first and not the
second.

Two binding constraints follow:
- H3's certainty manipulation uses a **small, fixed, hand-written, versioned** template set.
  No search, no optimisation loop, no efficacy ranking of individual prompt strings.
- The fact suite stays **scientifically inert** — physics, chemistry, biology, arithmetic.
  Extending to socially charged misinformation is Future Work *with an ethics review*, not a
  scope increase. And no real organisation, person or journal is named in any injected string
  (correcting SPEC-3 v1.0, which attributed fabricated claims to real scientific bodies).

**Consequences.**
- *Good:* a specific, argued withholding reads far better at review than a generic assurance,
  and it constrains the code in a direction that also keeps the design clean.
- *Cost:* forecloses a genuinely interesting line of work (adversarial prompt optimisation
  against agent populations). Accepted.
- *Risk:* scope creep back toward the withheld item under reviewer pressure. Mitigation: the
  review triggers in `RELEASE-SCOPE-AND-DUAL-USE.md` §7, and the answer to a reviewer request
  is no, with that document as the reason.
