---
id: MODEL-POOL
title: Candidate model pool — measured availability, not catalogue listings
status: DRAFT v0.2 — availability measured; capability pending EXP-000
version: 0.2
created: 2026-08-07
revised: 2026-08-09
supersedes: MODEL-POOL v0.1 (self-hosted Apache-2.0 pool — unservable, see §1)
closes: OQ-0055 (partially) · G1 checklist row C4
evidence: experiments/EXP-A04/provider_sweep.json
---

# Candidate model pool

**Everything here is measured, not catalogued.** `EXP-A03` established that NVIDIA's
`/v1/models` endpoint lists 100 models it will not all serve, and `EXP-A04` measured
availability, reliability and latency across 20 candidates on both providers, 3 trials each.

---

## 1. Why v0.1 was discarded

v0.1 selected Qwen2.5-7B, Mistral-7B-v0.3, OLMo-2-7B and Granite-3.3-8B — self-hosted,
Apache-2.0, ungated. That reasoning was sound and **the pool remains the right one if
institutional compute appears** (`OQ-0055`).

It is currently unusable. On NVIDIA, `mistral-7b-instruct-v0.3` and `granite-3.0-8b-instruct`
are catalogued but 404 on chat; Qwen and OLMo are absent. On GMI nothing below ~26B exists.

The reason is structural and worth stating: **the 7–9B open-weight band is
research-convenient but commercially uninteresting.** Hosted providers serve very small models
for cost or very large ones for capability. Nothing in between. That band runs on a single
GPU — which is exactly the argument to make when asking for institutional compute.

## 2. What actually works (`EXP-A04`, 3 trials each, 2026-08-09)

**Fully reliable (3/3) with a clean short answer:**

| Provider | Model | Lineage | p50 latency | Completion tokens |
|---|---|---|---|---|
| nvidia | `nvidia/nemotron-mini-4b-instruct` | NVIDIA | 313 ms | 1 |
| nvidia | `nvidia/nvidia-nemotron-nano-9b-v2` | NVIDIA | 364 ms | 3 |
| nvidia | `nvidia/llama-3.3-nemotron-super-49b-v1.5` | NVIDIA | 433 ms | 2 |
| nvidia | `meta/llama-3.1-8b-instruct` | Meta | 484 ms | 3 |
| gmi | `Qwen/Qwen3-Next-80B-A3B-Instruct` | Alibaba | 1,416 ms | 1 |
| gmi | `deepseek-ai/DeepSeek-V3.2` | DeepSeek | 2,286 ms | 1 |
| gmi | `MiniMaxAI/MiniMax-M3` | MiniMax | 2,558 ms | 16 |
| gmi | `moonshotai/Kimi-K2.5` | Moonshot | 2,691 ms | 2 |

**Reliable but emits a short reasoning trace** — usable; 13–16 completion tokens is a ~5×
overhead, not the ~100× that uncontrolled reasoning costs (`EXP-A03` §1.1):

| Provider | Model | Lineage | p50 | Tokens |
|---|---|---|---|---|
| nvidia | `openai/gpt-oss-20b` (`reasoning_effort: low`) | OpenAI | 338 ms | 13 |
| nvidia | `nvidia/nemotron-3-nano-30b-a3b` (`/no_think`) | NVIDIA | 434 ms | 16 |
| gmi | `zai-org/GLM-5.2-FP8` | Zhipu | 2,608 ms | 16 |
| gmi | `XiaomiMiMo/MiMo-V2.5` | Xiaomi | 4,241 ms | 16 |

**Excluded by measurement:**

| Model | Reason |
|---|---|
| `meta/llama-3.1-70b-instruct` | Reliable but **41.6 s** p50 — 86× the 8B model. Unusable at scale. |
| `openai/gpt-oss-120b`, `mistralai/mistral-nemotron`, `google/gemma-4-31b-it` | 0/3 — timeouts |
| `Qwen/Qwen3.5-27B`, `Qwen/Qwen3.6-35B-A3B` | 0/3 — HTTP 429, persistently overloaded |
| `minimaxai/minimax-m3` (NVIDIA), `google/gemma-4-26b-a4b-it` (GMI) | 1/3 and 2/3 — intermittent 429 |

## 3. The provider constraint that decides the pool

Reliable lineages, split by provider:

| Provider | Lineages available | Size band |
|---|---|---|
| **NVIDIA** | NVIDIA, Meta, OpenAI — and the NVIDIA entries are Llama-derived, so **~2 genuinely distinct** | 4–49 B |
| **GMI** | Alibaba, DeepSeek, MiniMax, Moonshot, Zhipu, Xiaomi — **6 distinct** | 27 B – 500 B+ |

**A cohort must not mix providers.** Provider would be confounded with lineage inside the
manipulation, and differing latency and failure profiles per member is precisely the
correlated-failure contamination `CONFOUND-REGISTER` X1 exists to prevent (`OQ-0055` option 3,
rejected).

**Therefore GMI is the only provider that can support D3 with four distinct lineages.**

## 4. Recommended pool

### 4.1 Primary — GMI, for the diversity ladder

| Slot | Model | Lineage | Notes |
|---|---|---|---|
| M1 | `Qwen/Qwen3-Next-80B-A3B-Instruct` | Alibaba | 80 B total / **3 B active** |
| M2 | `deepseek-ai/DeepSeek-V3.2` | DeepSeek | |
| M3 | `MiniMaxAI/MiniMax-M3` | MiniMax | |
| M4 | `moonshotai/Kimi-K2.5` | Moonshot | |
| Reserve | `zai-org/GLM-5.2-FP8`, `XiaomiMiMo/MiMo-V2.5` | Zhipu, Xiaomi | short reasoning trace |

**The D0/D1/D2 base model is not chosen here.** It must be whichever of M1–M4 has isolated
accuracy closest to the D3 cohort mean, and that is a measurement (`EXP-000`, D1). Choosing it
now would be exactly the capability-by-assertion this project criticises in prior work.

### 4.2 Secondary — NVIDIA, free, for the gradedness anchor

| Model | Lineage | Why |
|---|---|---|
| `meta/llama-3.1-8b-instruct` | Meta | 8 B — **inside** Sela's 7–9 B gradedness range |
| `nvidia/nvidia-nemotron-nano-9b-v2` | NVIDIA | 9 B — inside the range; also hybrid Transformer-Mamba |

`B6` asks whether agents revise binarily. Sela established that for **7–9 B**; the primary pool
is 27 B+. Running the gradedness sweep on **both** bands converts B6 from an assumption borrowed
from one paper into a test of whether gradedness is **size-dependent** — which extends Sela
rather than relying on him, and costs nothing because these endpoints are free.

## 5. Open problems with this pool — stated, not buried

1. **Outside the gradedness range.** The discrete-state DV rests on 7–9 B behaviour. If the
   27 B+ models are graded, `AMD-0002` needs substantial revision. `B6` is now the highest-value
   check in `EXP-000`, not a formality.
2. **"Size" is ambiguous for MoE.** `Qwen3-Next-80B-A3B` has 80 B total but **3 B active** per
   token. Whether gradedness tracks total or active parameters is unknown and unaddressed in the
   literature — a small, genuinely novel question this pool can answer almost for free.
3. **Ceiling risk is worse, not better.** `EXP-A03` measured `Qwen3-Next-80B` at **1.00** on a
   12-item sample. The stratified suite (`fact-suite` v0.2) is the mitigation, and its
   acquisition stratum now has to work at this capability level. **If it does not, the fact
   suite needs harder items again** — and that will be visible in `EXP-000` Part A.
4. **Cost.** GMI is paid. `EXP-000` is estimated at well under $1; the full matrix is
   plausibly $10–30 against a $9.90 balance, so the matrix substrate stays open (`DR-0012`).
5. **No revision pinning.** Neither provider exposes model revision SHAs. `SOP-040 §5` wants
   them. Mitigation: record every version string the API returns, run compactly, and re-run a
   canary set daily to detect drift (`RK-0005`).
6. **Licences unverified for the GMI models.** These are open-weight families but served under
   GMI's terms; the underlying licences have not been checked and neither has GMI's AUP for
   misinformation clauses (`OQ-0040`, `OQ-0053`).

## 6. Before this is frozen

- [ ] `EXP-000` D1 — isolated accuracy per model, with CIs
- [ ] D0/D1/D2 base model selected by measured `ā`, not by assertion
- [ ] `H(c)` computed and its **range** checked against the 0.15 criterion (`OQ-0051`)
- [ ] `B6` gradedness run on **both** size bands
- [ ] GMI licence and AUP check (`OQ-0053`)
- [ ] Canary drift-detection set defined
