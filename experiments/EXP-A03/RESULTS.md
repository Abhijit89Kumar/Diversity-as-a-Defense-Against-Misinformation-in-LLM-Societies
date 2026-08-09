---
id: EXP-A03
title: Provider availability and fact-suite ceiling check
status: COMPLETE
type: PILOT-PRECURSOR
preregistered: no — exploratory, run to decide the substrate
opened: 2026-08-09
closed: 2026-08-09
---

# EXP-A03 — Provider availability and fact-suite ceiling

Run to answer two questions before committing to a substrate (`DR-0012`): **what do the
available providers actually serve**, and **does the fact suite work at the sizes they serve?**

Cost: a few hundred API calls, effectively free. It changed two design decisions.

---

## 1. Provider availability

### NVIDIA API Catalog

`/v1/models` returns **100 model ids. It is a catalogue, not an availability list.**
Of 13 UI-badged "free endpoint" models tested:

| Outcome | n | Examples |
|---|---|---|
| Responded | 6 | `meta/llama-3.1-8b-instruct` (1.1 s), `nvidia/nemotron-mini-4b-instruct` (233 ms) |
| HTTP 410 "reached its…" | 2 | `qwen/qwen3-next-80b-a3b-instruct`, `mistralai/mixtral-8x7b-instruct-v0.1` |
| Timed out | 5 | **all five failed again on retry at a 180 s timeout — none is a cold start.** `gemma-4-31b-it` answered once in 82 s then timed out; `llama-3.3-70b-instruct` likewise (80 s, then timeout) |

Latency spanned **233 ms to 56 s** on the same tier. `gemma-4-31b-it` answered once in 82 s and
timed out on the retry.

**Three of the six that work are reasoning models** — `nemotron-nano-9b-v2`, `gpt-oss-20b`,
`nemotron-3-nano-30b` — emitting chain-of-thought into `reasoning_content` and leaving
`content` empty. At a 24-token probe budget they return **no answer at all**.

### 1.1 Reasoning can be suppressed, and that changes the cost picture entirely

An initial reading of this was that a reasoning model costs ~100× the tokens of a direct
answerer per probe, making them unusable across ~144,000 probes. **Testing the controls shows
that is wrong.**

| Model | Control | Latency | Completion tokens | Answer |
|---|---|---|---|---|
| `nemotron-nano-9b-v2` | none (budget 400) | 4,362 ms | 251 | TRUE |
| `nemotron-nano-9b-v2` | **`/no_think` system prefix** | **245 ms** | **3** | TRUE |
| `nemotron-nano-9b-v2` | `chat_template_kwargs {thinking: false}` | 6,477 ms | 380 | TRUE (ignored) |
| `gpt-oss-20b` | none (budget 400) | 589 ms | 56 | TRUE |
| `gpt-oss-20b` | **`reasoning_effort: "low"`** | **550 ms** | **16** | TRUE |
| `nemotron-3-nano-30b` | none (budget 400) | 732 ms | 40 | TRUE |

`/no_think` takes Nemotron from **251 completion tokens to 3** — identical to a model that
never reasons. `reasoning_effort: low` takes gpt-oss from 56 to 16. Note that
`chat_template_kwargs {"thinking": false}` was **silently ignored**: it neither errored nor
suppressed anything, which is the kind of failure that would quietly inflate a budget by an
order of magnitude if assumed to work.

**Reasoning models are therefore fully usable**, and the pool is wider than the raw
availability numbers suggest. Both controls are implemented in `NvidiaBackend`
(`reasoning_control="no_think" | "effort_low"`) and verified live end-to-end.

**None of the four models in `MODEL-POOL.md` are usable.** `mistral-7b-instruct-v0.3` and
`granite-3.0-8b-instruct` are catalogued but 404 on chat; Qwen and OLMo are absent.

### GMI Cloud

Base URL `https://api.gmi-serving.com/v1`. **Cloudflare rejects the default Python
user-agent with `403 code 1010`** — a browser UA header is required. Worth knowing; it
looks like an auth failure and is not.

80 models, but the size band is entirely different: closed frontier APIs plus **large open
MoE**. No model below ~26B. No Llama, Mistral, OLMo, Granite or Phi.

Direct-answer models that worked:

| Model | Lineage | Latency |
|---|---|---|
| `google/gemma-4-26b-a4b-it` | Google | 1.25 s |
| `google/gemma-4-31b-it` | Google | 1.31 s |
| `Qwen/Qwen3-Next-80B-A3B-Instruct` | Alibaba | 1.50 s |
| `MiniMaxAI/MiniMax-M3` | MiniMax | 1.95 s |
| `moonshotai/Kimi-K2.5` | Moonshot | 3.12 s |

**Four distinct pretraining lineages** — materially better than NVIDIA, where almost
everything available is Llama- or Nemotron-derived. Failures: Qwen3.5-27B/35B `429`
(overloaded), GLM `404`, DeepSeek-V4-Flash and MiMo emit reasoning traces, ByteDance `502`,
Tencent `400`.

---

## 2. The fact-suite ceiling — the decisive result

12 items spanning the difficulty range, probed on `s_true`, greedy decoding, one sample each.

| Model | Accuracy on `s_true` | Inclusion band [0.25, 0.85] |
|---|---|---|
| `llama-3.1-8b-instruct` (8B) | **0.92** | **CEILING** |
| `gemma-4-26b-a4b-it` (26B) | 0.83 | in band, barely |
| `Qwen3-Next-80B-A3B` (80B) | **1.00** | **CEILING** |

Only two items were missed by anyone: F-007 (penny from a skyscraper) and **F-028
(bat-and-ball)**, both by the 26B model. The 80B model got everything right.

### Why this matters, and the nuance the band got wrong

`RK-0009` (ceiling effects) has **materialised**. But the consequence is not uniform, and the
inclusion band conflated two different needs:

| Outcome | Needs | Effect of ceiling |
|---|---|---|
| **Capitulation hazard** (primary) | Agents that *start* holding the truth | **Helped** — ceiling maximises this risk set |
| **Truth-acquisition hazard** (AMD-0002 §2.3) | Agents that start *not* holding the truth | **Destroyed** — an empty risk set makes it unestimable |

`fact-suite/README.md` §2 imposed a single band `0.25 ≤ ā ≤ 0.85` on every item to serve both.
**That was the error.** No single difficulty serves both outcomes, and demanding one meant the
suite would have been rejected wholesale at validation.

### The fix: stratify the suite by intended outcome

Two strata, each validated against its own criterion:

- **Retention stratum** — high isolated accuracy (≈ 0.75–0.95). Agents begin in `HOLDS`;
  these items carry the capitulation hazard and the cascade outcomes.
- **Acquisition stratum** — mid-to-low isolated accuracy (≈ 0.25–0.60). A meaningful share of
  agents begin wrong; these items carry the truth-acquisition hazard and make topology results
  identifiable (`OQ-0027`).

This is better design, not a workaround: it makes item difficulty an explicit, reported factor
rather than a nuisance the band was trying to average away. Stratum is entered as a factor;
outcomes are reported per stratum.

**And the suite needs harder items.** The current 31 are largely well-known misconceptions that
instruction-tuned models are explicitly trained to correct. The one item that reliably
discriminated was **reasoning**, not recall — which points at where the acquisition stratum
should come from.

---

## 3. Caveats

- **n = 12 items, one greedy sample each.** Indicative, not the full validation. `EXP-000`
  Part A uses 31 items × 3 paraphrases × 2 orders with repetitions.
- Per-item accuracy over many stochastic samples may be lower than a single greedy sample
  suggests. But 0.92 and 1.00 sit far enough above 0.85 that the direction is not in doubt.
- Only `s_true` was probed. `s_false` endorsement is untested and could differ.

## 4. Consequences

1. `OQ-0054` — split the fact suite into retention and acquisition strata, and add harder
   items. **Blocks `EXP-000`**, since the inclusion rule must be fixed before validation data
   is seen (G1 row C2 precedes C3).
2. `MODEL-POOL.md` needs rewriting; none of its four models is servable on either provider.
3. The `NvidiaBackend` must probe availability rather than trust the catalogue — already
   implemented as `probe_availability()`.
4. `OQ-0038`'s gradedness finding is specific to **7–9B**. GMI's models are 26–80B, outside
   that range, so `B6` becomes more important, not less — and running it on both an 8B and a
   26B+ model turns it into a test of whether gradedness is size-dependent, which extends
   Sela rather than merely borrowing from it.

## 5. Reproduce

```bash
python scripts/provider_check.py     # to be extracted from the scratchpad probes
```

Requires `NVIDIA_API_KEY` and `GMI_API_KEY` in `.env` (gitignored). Provider availability
changed *during* testing, so results are timestamped rather than expected to replicate exactly.
