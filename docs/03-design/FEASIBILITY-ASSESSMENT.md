---
id: FEASIBILITY-2026-08
title: Feasibility Assessment — capacity, models, terms, compute, annotation
status: DRAFT — v1.0 plan does not survive
version: 0.1
created: 2026-08-07
closes: OQ-0013, OQ-0014 (partially), OQ-0018, OQ-0020
---

# Feasibility Assessment

All figures below were fetched from primary sources on **2026-08-07** and carry their URL.
Anything not verified is marked `[UNVERIFIED]` and must not be treated as fact (SOP-010 §2).

> **Verdict: the v1.0 execution plan is not feasible as written.** Not marginally — the
> primary model disappears in nine days, the free-tier token budget is short by roughly 3×,
> one provider's terms prohibit the kind of comparison a paper implies, and the compute
> plan specifies hardware that physically cannot host the model assigned to it.
>
> All of this is fixable. None of it is fixable *after* the matrix has been launched.

---

## 1. Summary

| Component | Verdict | Reason |
|---|---|---|
| Primary model (`llama-3.1-8b-instant`) | **DEAD 2026-08-16** | Groq deprecation, 9 days away |
| `llama-3.3-70b-versatile` on Groq | **DEAD 2026-08-16** | Same announcement |
| `qwen-2.5-32b` | **DEAD since 2025-04-14** | 3 retirements out of date |
| Free-tier call capacity | **INFEASIBLE** | Token/day caps bind ~3× short |
| Cerebras as a benchmarked provider | **PROHIBITED BY ToS** | Explicit anti-benchmarking clause |
| Groq ToS position | **UNKNOWN** | Operative agreement not publicly retrievable |
| Modal L4 for 70B | **PHYSICALLY IMPOSSIBLE** | 24 GB card, ~141 GB model |
| Modal 70B on correct hardware | **PLAUSIBLE, UNMEASURED** | Cost dominated by warm-time, not tokens |
| MTurk | **CLOSED TO NEW REQUESTERS** | Since 2026-07-30 |
| Prolific | **FEASIBLE** | But budget line is wrong by 1.5–4.5× |

---

## 2. Model availability — the nine-day problem

Source: <https://console.groq.com/docs/deprecations>, fetched 2026-08-07. Verbatim:

> *"August 16, 2026: llama-3.1-8b-instant and llama-3.3-70b-versatile — In line with our
> commitment to bringing you cutting-edge models, on June 17, 2026, we emailed users to
> announce the deprecation of `llama-3.1-8b-instant` and `llama-3.3-70b-versatile`. We
> recommend migrating to `openai/gpt-oss-20b` (for Llama 3.1 8B Instant) and
> `openai/gpt-oss-120b` or `qwen/qwen3.6-27b` (for Llama 3.3 70B Versatile)…
> **This deprecation applies to free and developer-tier usage**; enterprise customers with
> a committed-spend contract are not affected."*

| Model in the specs | Shutdown | Status |
|---|---|---|
| `llama-3.1-8b-instant` (SPEC-2 §3.1, homogeneous cohort) | **08/16/26** | 9 days |
| `llama-3.3-70b-versatile` | **08/16/26** | 9 days |
| `qwen-2.5-32b` (SPEC-2 §3.1, heterogeneous cohort) | 04/14/25 | Gone ~16 months. Chain: → `qwen-qwq-32b` (07/14/25) → `qwen/qwen3-32b` (07/17/26) → `openai/gpt-oss-120b`. Current nearest: `qwen/qwen3.6-27b` |
| `llama3-8b-8192` (Cerebras equivalent in cohort) | 08/30/25 on Groq | Gone |

**Consequence.** An 8-week run starting today loses its primary homogeneous model in week 2.
Any pilot data collected on `llama-3.1-8b-instant` becomes unreproducible after 08/16 —
which collides directly with SOP-040 §2, where the logged trajectory dataset is the durable
artefact but the *generating model* must still be nameable and, ideally, re-runnable.

**Note the pattern.** Several models were previously retired *into* `llama-3.1-8b-instant`,
which is now itself retiring. Groq's small-model free tier has churned roughly every 6–10
months. **Any 8-week study on this substrate must assume at least one mid-flight retirement
and design for it** — or self-host, where weights are permanent.

This is the strongest available argument for self-hosting open weights rather than
depending on hosted free tiers, and it is a scientific argument, not just a logistical one:
`RK-0005` was rated likelihood 3; it should be **5**, because the event is already scheduled.

---

## 3. Free-tier capacity — token caps, not request caps

Source: <https://console.groq.com/docs/rate-limits>, fetched 2026-08-07.

| Model | RPM | RPD | TPM | **TPD** |
|---|---|---|---|---|
| `llama-3.1-8b-instant` | 30 | 14.4K | 6K | **500K** |
| `llama-3.3-70b-versatile` | 30 | 1K | 12K | **100K** |
| `openai/gpt-oss-120b` | 30 | 1K | 8K | **200K** |
| `openai/gpt-oss-20b` | 30 | 1K | 8K | **200K** |
| `qwen/qwen3.6-27b` | 30 | 1K | 8K | **200K** |

> `[UNVERIFIED]` — which tier. The page renders a tabbed widget ("Free Plan Limits" /
> "Developer Plan Limits") and its preamble reads *"the limits shown below are the base
> limits for the Developer plan."* A static fetch captures only one table. A human must open
> the page in a browser and confirm which tab these are. **If these are Developer-tier
> numbers, the free tier is lower still and the conclusion below only strengthens.**

**The RPD figure is a trap.** 500,000 TPD ÷ 14,400 RPD = **34.7 tokens per request.** No
multi-turn agent message is 35 tokens. The token cap binds long before the request cap, on
every model, on every provider.

**Cerebras** (<https://inference-docs.cerebras.ai/support/rate-limits>): free tier is
`gpt-oss-120b`, `zai-glm-4.7`, `gemma-4-31b` — **5 RPM / 30K TPM / 1M TPD**, and **no
RPD column at all**. Critically: **no Llama-class model remains on the Cerebras free tier**,
so the planned "Cerebras Llama-3-8B" cohort member does not exist.

**Google AI Studio** (<https://ai.google.dev/gemini-api/docs/rate-limits>, last updated
2026-07-21): the per-model free-tier table has been **removed**. The page now says limits
*"can be viewed in Google AI Studio"* behind authentication, and warns *"Specified rate
limits are not guaranteed."* `gemini-2.5-flash` **is** still free-tier per the pricing page
(<https://ai.google.dev/gemini-api/docs/pricing>, last updated 2026-08-05), but **no quota
is publicly stated**. Third-party blogs quote RPD anywhere from 250 to 1,500 — the spread is
itself evidence that no reliable public figure exists.
→ **Action: a human must sign in to <https://aistudio.google.com/rate-limit> and record the
actual quota.** Until then Gemini cannot enter any capacity plan.

**OpenRouter** (<https://openrouter.ai/docs/api-reference/limits>): `:free` models are
20 RPM and **50 requests/day**, rising to 1,000 RPD only after purchasing ≥10 credits. At
50 RPD, 160,000 calls takes 3,200 days. Not a fallback.

### Arithmetic

Corrected call volume (`OQ-0007`): ~40,500 agent messages + ~121,500 belief probes ≈
**160,000 calls**. Window = 56 days → **2,857 calls/day sustained**, with zero allowance for
retries, backoff, or outages.

> ⚠ **The token figures below rest on assumptions, not measurements** — ~800 tokens per
> multi-turn agent message, ~200 per probe, ≈ 56.7M tokens total. Per SOP-010 §2 these must
> not enter any document as facts. **They must be replaced with measured `usage` fields from
> a pilot before any plan depends on them.**

| Route | Daily ceiling | Days for 160K calls |
|---|---|---|
| Groq post-08/16, 3 models × 1K RPD | 3,000 requests | 53 days on requests — but 600K TPD ≈ **95 days on tokens** |
| Cerebras, 1M TPD | ~2,825 calls | **~57 days** |
| OpenRouter (+$10) | 1,000 | 160 days |
| Google | unquantifiable | — |

**And multi-turn makes it worse than this.** An agent message does not cost one message of
tokens — it costs the *entire conversation history re-sent as input on every turn*. Over
5 rounds, cumulative input scales roughly quadratically. Any estimate built from call counts
is wrong by an order of magnitude in the unsafe direction.

**Verdict: INFEASIBLE.** No single provider carries this. The multi-provider combination is
marginally arithmetically possible but **should be rejected on design grounds, not
logistics** — sharding agents across providers aliases model identity with provider, which
is fatal for a study whose dependent variable is belief dynamics.

---

## 4. Terms of service

| Provider | Benchmarking / publication | Evidence |
|---|---|---|
| **Cerebras** | **PROHIBITED** | <https://www.cerebras.ai/terms-of-service> — users may not *"Use or display the Service in competition with us, to develop competing products or services, **for benchmarking or competitive analysis of the Service**, or otherwise to our detriment or disadvantage."* (Effective 2024-08-27) |
| **Google** | Permitted | <https://ai.google.dev/gemini-api/terms> (updated 2026-03-23) — no benchmarking clause. But: *"Google uses the content you submit… to provide, improve, and develop Google products"* and *"human reviewers may read, annotate, and process your API input and output."* |
| **Groq** | **UNKNOWN** | <https://groq.com/terms-of-use/> governs the website, not the API, and is silent. The operative Groq Services Agreement and per-model terms require an authenticated session. **Silence is not permission.** |
| **OpenRouter** | Permitted, but | <https://openrouter.ai/terms> (updated 2026-07-29) §8: *"OpenRouter allows Red Teaming only for legitimate research purposes and requires users interested in Red Teaming to first submit a written request."* |

**Two live issues.**

1. **Cerebras.** Reporting Cerebras throughput, latency, or any cross-provider performance
   comparison is *on its face* "benchmarking or competitive analysis of the Service." Two
   escapes: use it purely as a model substrate and publish **nothing** about
   Cerebras-the-service — model behaviour only, never provider performance — or obtain
   written permission. The former is probably defensible since we measure belief dynamics,
   not inference speed, but it must be a deliberate documented decision, not an accident.
2. **OpenRouter's red-teaming clause.** A study that deliberately injects misinformation to
   measure propagation could be characterised as adversarial testing. If OpenRouter is used,
   submit the written request in advance. It is cheap and the clause explicitly contemplates
   legitimate research.

**Not yet checked, and potentially larger than rate limits:** each provider's separate
**acceptable-use / prohibited-use policy**, read specifically for clauses on *generating or
amplifying misinformation*. This study's entire method is instructing models to argue for
falsehoods. Raised as `OQ-0040`.

---

## 5. Compute — the 70B condition

Source: <https://modal.com/pricing>, fetched 2026-08-07. Per-second rates, converted:

| GPU | $/sec | $/hr | VRAM |
|---|---|---|---|
| Nvidia T4 | 0.000164 | **0.59** | 16 GB |
| Nvidia L4 | 0.000222 | **0.80** | 24 GB |
| Nvidia A10 | 0.000306 | **1.10** | 24 GB |
| Nvidia L40S | 0.000542 | **1.95** | 48 GB |
| Nvidia A100 40GB | 0.000583 | **2.10** | 40 GB |
| Nvidia A100 80GB | 0.000694 | **2.50** | 80 GB |
| Nvidia H100 | 0.001097 | **3.95** | 80 GB |
| Nvidia H200 | 0.001261 | **4.54** | 141 GB |

Starter plan: $0/month + compute, **$30/month free credits**.

**SPEC-2 §3.5 specifies L4 at "~$0.80/hr". The price is exactly right — and the hardware is
impossible.** Llama-3.1-70B in bf16 is ≈141 GB of weights before KV cache. An L4 has 24 GB.
The spec's entire compute model is built on a card that cannot load the model assigned to it.

Minimum viable configurations:

| Config | $/hr | Note |
|---|---|---|
| 2 × A100 80GB (160 GB) | **5.00** | bf16, tensor-parallel |
| 2 × H100 (160 GB) | **7.90** | bf16, faster |
| 1 × H200 (141 GB) | **4.54** | Marginal — no KV headroom at bf16 |
| 1 × A100 80GB, 4-bit AWQ (~40 GB) | **2.50** | **Changes model behaviour** — unacceptable for a belief study without an explicit equivalence check |

**Cost is dominated by warm wall-clock, not tokens.** The protocol is synchronous: all 20
agents must complete round *t* before round *t+1*. That is 135 runs × 5 rounds = **675
sequential batch steps**, each needing the model resident. Loading ~141 GB on every cold
start is minutes; keeping the container warm costs continuously whether or not it is
computing.

Order-of-magnitude, `[UNVERIFIED]` and requiring a pilot: at 2 × A100 80GB, if the condition
completes in 20 warm hours the cost is ~$100; at 60 hours it is ~$300 and the $280 pool is
gone. **The variance here is larger than the budget.** A one-run timing pilot resolves it.

Worth noting the quantisation trap explicitly: AWQ/GPTQ halves cost and *changes what the
model believes*. For a study whose DV is belief, quantising the scale-matched arm and not
the others would confound the primary comparison. If quantisation is used, it must be used
uniformly and an equivalence check reported.

---

## 6. Human annotation

**MTurk is closed to new requesters as of 2026-07-30** — one week ago. Amazon moved it to
the AWS "Services in Maintenance" list; existing accounts continue, new requesters and
workers cannot register.
Sources: [TechCrunch](https://techcrunch.com/2026/07/05/amazon-will-stop-accepting-new-customers-for-mechanical-turk/),
[The Register](https://www.theregister.com/off-prem/2026/07/03/amazons-mechanical-turk-to-stop-accepting-new-customers-and-not-even-ai-can-save-it/5266274),
[SiliconANGLE](https://siliconangle.com/2026/07/05/amazons-mechanical-turk-service-now-life-support-stops-accepting-new-users/).

> An aside that matters for the validation study's *validity*, not just its logistics:
> reporting on the closure cites a 2023 analysis finding **33–46% of MTurk workers were
> using LLMs to complete tasks.** A human-validation benchmark whose annotators are secretly
> using LLMs does not validate anything. Whichever platform is used, attention checks and an
> LLM-use screen are mandatory, and the exclusion rule must be preregistered (SOP-050 §6).

**Prolific** — minimum **£6 / $8 per hour**, recommended **£9 / $12 per hour**; platform fee
**33.3% of participant rewards for academic/non-profit** (42.8% corporate).
Sources: [pricing](https://researcher-help.prolific.com/en/articles/445239-what-is-your-pricing),
[how much to pay](https://researcher-help.prolific.com/en/articles/445266-how-much-should-i-pay-participants).

Recomputing the study — 150 items × 3 annotators = **450 judgements**:

| Scenario | Annotator time | Rewards | +33.3% fee | **Total** |
|---|---|---|---|---|
| 45 s/item at $8/hr (minimum) | 5.6 h | $45 | $15 | **$60** |
| 45 s/item at $12/hr (recommended) | 5.6 h | $68 | $23 | **$90** |
| SPEC-3's $0.30/judgement | — | $135 | $45 | **$180** |

Compliance: $0.30/judgement clears the $8/hr floor provided each judgement takes ≤135 s.
Reading one agent response and rating accept/reject/uncertain plausibly takes 30–60 s, so
SPEC-3's rate is compliant and in fact generous.

**But SPEC-4's budget line of $40 is wrong under every scenario**, and it corresponds to a
single-annotator study from which Fleiss' κ — SPEC-3's stated validation statistic — cannot
be computed at all (`OQ-0012`). With $80 reserved for workshop registration, **the $120 cash
cap is exceeded in every scenario**, by $20 at best and $140 at worst.

---

## 7. What this changes

Ordered by how much wasted work each prevents.

1. **Stop naming `llama-3.1-8b-instant` anywhere.** Choose a replacement now. This is a
   9-day clock and it touches the config, the pilot, and both homogeneous cohorts.
2. **Decide hosted-vs-self-hosted, and prefer self-hosted open weights.** Free-tier capacity
   does not fit, model churn is scheduled, one provider's ToS prohibits comparison, and
   another's terms are unreadable. Self-hosting on Modal costs money but buys permanent
   weights, uniform logprob access (which also resolves `OQ-0002`), no ToS ambiguity, and
   reproducibility. The $280 pool is the real budget; the "free API" premise is the thing to
   abandon, not the science.
3. **Cut the probe budget.** 121,500 probes are **76%** of the call volume. Probing at
   rounds {0, 2, 5} instead of every round cuts it ~40%. Legitimate **only if fixed a priori
   and recorded in a DR** — probe cadence is a free parameter on the dependent variable
   (SOP-030 §1.5).
4. **Measure tokens per call in a pilot** and redo every number in §3 and §5. Nothing here
   should be trusted as a planning figure until it is measured.
5. **Rebuild the budget** from corrected volumes. Current cash line is short; the $0.00
   API line is fiction.
6. **Read the providers' acceptable-use policies** for misinformation clauses (`OQ-0040`).
7. **Human must capture Google's actual quota** from the authenticated AI Studio page.
8. **Human must read Groq's operative API terms** from the authenticated console.

---

## 8. Still unverified

- Google Gemini free-tier RPM/RPD/TPM — not public.
- Which Groq tab the §3 table belongs to.
- Groq's operative API terms (benchmarking, publication, bulk scripted use).
- Whether Cerebras's 2024-dated ToS has been superseded by an inference-specific agreement.
- All token-per-call figures — assumptions, not measurements.
- Provider acceptable-use policies re: misinformation generation.
- Whether free tiers permit sustained automated bulk usage at all.
- Workshop deadlines, arXiv `cs.MA` endorsement requirements for a first-time submitter,
  and the belief-measurement and statistics literature — the round-2 sweep was interrupted
  before reaching these. Carried as open work.
