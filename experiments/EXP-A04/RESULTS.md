---
id: EXP-A04
title: Measured provider availability and reliability sweep
status: COMPLETE
type: DESIGN
preregistered: no — measurement to inform the pool decision
opened: 2026-08-09
closed: 2026-08-09
---

# EXP-A04 — Provider availability sweep

Evidence for `MODEL-POOL.md` v0.2 and `OQ-0055`. 20 candidate models, both providers,
**3 trials each**, sequential (parallel workers against a shared rate-limited endpoint would
produce 429s and corrupt the latency measurement this exists to collect).

Raw output: `provider_sweep.json`. Reproduce: `python scripts/provider_sweep.py --out experiments/EXP-A04`.

## Headline

**9 of 20 fully reliable with a clean short answer. 6 distinct lineages.**

Reliability is not binary — it is the thing that had to be measured. Three models returned
1/3 or 2/3, which is worse than a clean failure because it would surface mid-matrix as
missing data correlated with nothing in particular.

| Failure mode | Models |
|---|---|
| 0/3 timeouts | `gpt-oss-120b`, `mistral-nemotron`, `gemma-4-31b-it` |
| 0/3 HTTP 429 | `Qwen3.5-27B`, `Qwen3.6-35B-A3B` |
| Intermittent (1/3, 2/3) | `minimax-m3` (NVIDIA), `gemma-4-26b-a4b-it` (GMI) |
| Reliable but unusable | `llama-3.1-70b-instruct` — **41.6 s** p50, 86× the 8B model |

## The result that decides the pool

Reliable lineages split cleanly by provider:

- **NVIDIA** — NVIDIA, Meta, OpenAI. But the NVIDIA entries are Llama-derived, so **~2
  genuinely distinct lineages**. Fast (313–484 ms) and free.
- **GMI** — Alibaba, DeepSeek, MiniMax, Moonshot, Zhipu, Xiaomi. **6 distinct lineages.**
  Slower (1.4–4.2 s) and paid.

Since a cohort must not mix providers (`CONFOUND-REGISTER` X1 — provider would be confounded
with lineage inside the manipulation), **only GMI can support D3 at four distinct lineages.**

That is the whole pool decision, and it was not predictable from documentation.

## Secondary findings

- **`gemma-4-26b-a4b-it` was reliable in `EXP-A03` and intermittent here**, one day apart.
  Hosted availability is not a fixed property. `RK-0005` applies continuously, not just at
  deprecation events, and the canary-drift check in `MODEL-POOL.md` §5.5 is not optional.
- **Reasoning suppression holds up.** `nemotron-nano-9b-v2` under `/no_think` returned 3
  completion tokens across all trials; `gpt-oss-20b` under `reasoning_effort: low` returned 13.
  Both are usable overheads.
- **Answer consistency was perfect** across trials for every reliable model at temperature 0 —
  no model gave different answers on repeat calls. Encouraging for probe reliability (V1), but
  this is one item; the real test is `EXP-000`.

## Caveats

- One probe item (`F-017`, 206 bones). Availability and latency generalise; **answer behaviour
  does not** — that is what `EXP-000` Part A measures.
- 3 trials gives a coarse reliability estimate. A model at 2/3 here could be 0.5 or 0.9 in
  truth; the point is only to separate "reliable" from "not".
- Latency was measured from one location at one time of day.
- **No capability measured.** Nothing here says which models are *better*, only which respond.
  Capability matching (`AMD-0001 §4`) depends entirely on `EXP-000` D1.
