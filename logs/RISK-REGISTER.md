# Risk Register

Append-only. Rules: SOP-010 §1.4. Every risk needs a **trigger** — the observable event
that means the mitigation must be executed *now*. A risk without a trigger is a worry.

Scoring: Likelihood (L) and Impact (I) on 1–5. Severity = L × I.

| ID | Risk | L | I | Sev | Status |
|---|---|---|---|---|---|
| RK-0001 | Contribution is already published | 4 | 5 | 20 | ASSESSING |
| RK-0002 | Belief metric is not construct-valid across model families | 4 | 5 | 20 | OPEN |
| RK-0003 | Free-tier rate limits make the matrix infeasible | 3 | 4 | 12 | ASSESSING |
| RK-0004 | Budget overrun / cap exceeded | 4 | 3 | 12 | OPEN |
| RK-0005 | Provider deprecates a model mid-matrix | **5** | **5** | **25** | **MATERIALISED** |
| RK-0006 | Design is underpowered; results are inconclusive | 3 | 4 | 12 | OPEN |
| RK-0007 | 8-week timeline slips past the target workshop deadline | 4 | 3 | 12 | ASSESSING |
| RK-0008 | Analysis-pipeline bug produces a wrong published number | 2 | 5 | 10 | OPEN |
| RK-0009 | Ceiling/floor effects on the fact suite | 3 | 3 | 9 | OPEN |
| RK-0010 | Ethics/IRB gap on the annotation study | 2 | 4 | 8 | OPEN |
| RK-0011 | Dual-use criticism at review | 2 | 3 | 6 | OPEN |
| RK-0012 | Raw data loss | 2 | 5 | 10 | OPEN |
| RK-0013 | Collaboration breakdown / uneven contribution | 2 | 4 | 8 | OPEN |
| RK-0014 | arXiv endorsement not in place when needed | 2 | 3 | 6 | OPEN |
| RK-0015 | **Scooped by Becker et al. / GippLab on the heterogeneity axis** | 4 | 5 | 20 | OPEN |

---

### RK-0001 — Contribution is already published
**Trigger:** the prior-art sweep surfaces a Tier-A paper whose contribution overlaps
ours by more than "same area, different question."
**Mitigation:** re-position rather than abandon. The project has at least four separable
contributions — (a) the diversity-defence result, (b) a validated cross-model belief
measurement protocol, (c) an open benchmark and framework, (d) the topology×population
interaction. If (a) is taken, (b) and (c) are still publishable and are arguably the more
durable artefacts. Decide at G1, not later.
**Owner:** Lead / theorist. **Links:** OQ-0001.

### RK-0002 — Belief metric is not construct-valid across model families
**Trigger:** robustness testing shows belief estimates move more under paraphrase or
option-order than under the experimental manipulation; or per-model calibration curves
differ enough that a fixed threshold means different things per model.
**Mitigation:** fall back to a uniform, provider-independent measure (verbal
paraphrase-consistency across many templates) and report it as the primary DV, with any
logit measure as a secondary analysis on the subset where it is available. Report the
robustness numbers in the paper as a contribution rather than hiding them.
**Owner:** Lead / theorist. **Links:** OQ-0002, OQ-0009, SOP-030 §1.

### RK-0003 — Free-tier rate limits make the matrix infeasible
**Trigger:** measured throughput in the pilot implies the corrected call volume
(OQ-0007) exceeds a provider's daily cap, or sustained 429s.
**Mitigation, in order:** reduce probe frequency (probe at rounds 0/2/5 rather than every
round); reduce M paraphrase templates; reduce facts from 15 to a validated subset;
reduce topologies; self-host on Modal. Every reduction is recorded as a scope cut with a
DR and reported as a limitation — never as a method change.
**Owner:** Engineering lead. **Links:** OQ-0007, OQ-0013.

### RK-0004 — Budget overrun
**Trigger:** cumulative spend passes 60% of any cap before the corresponding phase is 60%
complete.
**Mitigation:** hard stop and re-plan. Known issues already: the annotation budget is
inconsistent between SPEC-3 and SPEC-4 and understated by ~3× before platform fees; the
70B condition is not costed; the $0.00 API line assumes free tiers that cannot serve the
70B arm. Rebuild the budget from the corrected call volume before G3 and log a running
spend ledger from day one.
**Owner:** Both. **Links:** OQ-0012, OQ-0014.

### RK-0005 — Model deprecation mid-matrix — **MATERIALISED 2026-08-07**
**L 5 · I 5 · Sev 25.** No longer a risk. It is a scheduled event.

`llama-3.1-8b-instant` — the primary homogeneous cohort model — and
`llama-3.3-70b-versatile` both **shut down on 2026-08-16**, nine days from today, per
<https://console.groq.com/docs/deprecations> (verified directly, 2026-08-07). The notice
states the deprecation *"applies to free and developer-tier usage"*. `qwen-2.5-32b` from the
heterogeneous cohort has been gone since 2025-04-14 and is three retirements out of date.

Historic churn on Groq's small-model free tier is roughly every 6–10 months; several models
were previously retired *into* `llama-3.1-8b-instant`, which is now retiring itself.
**Any 8-week study on hosted free tiers must assume at least one mid-flight retirement.**

**Immediate actions:** stop naming the deprecated models anywhere; choose replacements before
any pilot; treat any pilot data already collected on them as unreproducible after 08/16.
**Strategic action:** this is the strongest available argument for self-hosting open weights
(`docs/03-design/FEASIBILITY-ASSESSMENT.md` §7.2) — weights are permanent, logprobs are
uniform, and there is no ToS ambiguity.

**Trigger (residual):** any provider version string changing between runs, or a model ID
returning errors.
**Mitigation:** record provider version strings on every call (SOP-040 §5); run the matrix
in a compact window rather than spread over weeks; keep a small "canary" set of prompts
re-run daily whose outputs are checked for drift; if a change is detected, treat pre- and
post-change runs as separate strata and report it.
**Owner:** Engineering lead. **Links:** OQ-0018.

### RK-0006 — Underpowered design
**Trigger:** the pilot's between-run variance implies power < 0.80 for the smallest
effect of interest at the planned replication count.
**Mitigation:** increase replications on the primary contrast at the cost of secondary
cells; or preregister the study as exploratory and report estimates with intervals rather
than significance claims. Both are honest; running an underpowered confirmatory test and
reporting p-values is not.
**Owner:** Lead / theorist. **Links:** OQ-0019, SOP-030 §4.

### RK-0007 — Timeline slips past the workshop deadline
**Trigger:** any phase gate missed by more than 5 days.
**Mitigation:** the arXiv preprint is the deadline-independent artefact and is the primary
portfolio asset; workshop submission is opportunistic. Cut scope per SOP-000 P9. Confirm
the actual deadline calendar at G1 so slippage is measured against something real.
**Owner:** Both. **Links:** OQ-0023.

### RK-0008 — Analysis bug produces a wrong published number
**Trigger:** any discrepancy between two independent computations of the same quantity.
**Mitigation:** planted-effect synthetic-data test of the full analysis pipeline before it
touches real data (SOP-040 §3, SOP-060 §8); negative controls run before hypothesis tests
(SOP-060 §1); every paper number generated programmatically, never typed. If an error is
found post-publication, correct in public (SOP-080 §1).
**Owner:** Both. **Links:** —

### RK-0009 — Ceiling/floor on the fact suite
**Trigger:** `G_empty` baseline shows a fact where models are >95% or <5% correct in
isolation.
**Mitigation:** preregistered inclusion band; exclude out-of-band items *before* the
matrix runs, by rule. Over-recruit facts now (curate 25–30, keep the 15 that survive
validation) rather than discovering the problem after execution.
**Owner:** Lead / theorist. **Links:** OQ-0017.

### RK-0010 — Ethics/IRB gap
**Trigger:** any step toward launching the annotation study before a determination is
recorded.
**Mitigation:** obtain the determination first; it cannot be obtained retroactively. If no
institutional route exists, document a self-administered ethics protocol (consent, fair
pay, debrief, de-identification) and state it in the paper.
**Owner:** Lead / theorist. **Links:** OQ-0021, SOP-080 §2.

### RK-0011 — Dual-use criticism at review
**Trigger:** —(anticipatory).
**Mitigation:** write the broader-impact and release-scope decision before submission, not
in response to a reviewer. Keep the fact suite scientifically absurd rather than socially
charged. **Links:** OQ-0022, SOP-080 §4.

### RK-0012 — Raw data loss
**Trigger:** any single-copy state of raw data lasting more than 24 hours.
**Mitigation:** second-location backup before analysis begins; checksums recorded; backup
location and date logged. **Links:** SOP-050 §4.

### RK-0013 — Collaboration breakdown
**Trigger:** a task matrix item with no progress for two consecutive weeks, or an
unraised disagreement about authorship.
**Mitigation:** author order and CRediT roles agreed in a DR before results exist
(SOP-070 §7); weekly written check-in in the research log; either party may block a gate
on an integrity concern without penalty. **Links:** SOP-080 §5.

### RK-0015 — Scooped on the heterogeneity axis
**Raised:** 2026-08-07 · **L 4 · I 5 · Sev 20**

Becker, Wahle, Ruas & Gipp (arXiv:2606.16710, 15 Jun 2026, Göttingen/GippLab) published the
closest prior work eight weeks ago. Their stated Future Work is *"larger agent networks"* and
their Limitations name *"additional model families… and more complex agent architectures"* —
i.e. an established lab has publicly announced **both of this project's remaining axes** as
their next step. They have more compute, more people, and a two-month head start.

**Trigger:** any new arXiv listing from that group, or any paper crossing both the
heterogeneity and misinformation-propagation axes.

**Mitigations, in priority order:**
1. **Do not race them on their axis.** Compete on what they cannot cheaply copy: the
   *measured continuous* diversity–resilience relationship across many cohorts (they compare
   two backbones), the belief-trajectory instrument, N=20 topological structure, and the
   truth-diffusion counterpart metric. Beating them to "we also mixed model families" is not
   winnable and not interesting.
2. **Post the preprint early**, even at reduced scope. An arXiv timestamp is the only
   protection available, and it is free.
3. **Set a Google Scholar / arXiv alert** on that author group and on the topic, checked
   weekly, logged in the research log.
4. **Frame as complementary, not competing.** Cite them prominently. If they publish first,
   a well-executed independent study at different scale with a different instrument is still
   publishable — and a paper that *contradicts* a recent result is more interesting than one
   that confirms it.

**Owner:** Lead / theorist. **Links:** OQ-0001, OQ-0030, RK-0001.

### RK-0014 — arXiv endorsement missing
**Trigger:** 3 weeks before intended posting with no confirmed endorsement path for a
first-time submitter in the target category.
**Mitigation:** verify endorsement requirements early; identify a potential endorser
(supervisor, collaborator, co-author with posting history) well in advance.
**Links:** OQ-0023, SOP-070 §6.
