---
id: MODEL-POOL
title: Candidate model pool — licence, gating and availability
status: DRAFT — pending capability measurement (EXP-000)
version: 0.1
created: 2026-08-07
closes: G1 checklist row C4 · advances OQ-0040
---

# Candidate model pool

Metadata below queried from the Hugging Face API on **2026-08-07**. Parameter counts are
`safetensors.total`.

---

## 1. Survey

| Model | Licence | Gated | Params |
|---|---|---|---|
| `Qwen/Qwen2.5-7B-Instruct` | **apache-2.0** | no | 7.6 B |
| `Qwen/Qwen3-8B` | **apache-2.0** | no | 8.2 B |
| `mistralai/Mistral-7B-Instruct-v0.3` | **apache-2.0** | no | 7.2 B |
| `allenai/OLMo-2-1124-7B-Instruct` | **apache-2.0** | no | 7.3 B |
| `ibm-granite/granite-3.3-8b-instruct` | **apache-2.0** | no | 8.2 B |
| `microsoft/Phi-4-mini-instruct` | **mit** | no | 3.8 B |
| `HuggingFaceTB/SmolLM3-3B` | **apache-2.0** | no | 3.1 B |
| `mistralai/Ministral-8B-Instruct-2410` | other | no | 8.0 B |
| `tiiuae/Falcon3-7B-Instruct` | other | no | 7.5 B |
| `google/gemma-2-9b-it` | gemma | **manual** | 9.2 B |
| `meta-llama/Llama-3.1-8B-Instruct` | llama3.1 | **manual** | 8.0 B |

## 2. Recommended pool — four families, Apache-2.0, ungated

| Slot | Model | Lineage | Params |
|---|---|---|---|
| M1 | `Qwen/Qwen2.5-7B-Instruct` | Alibaba | 7.6 B |
| M2 | `mistralai/Mistral-7B-Instruct-v0.3` | Mistral | 7.2 B |
| M3 | `allenai/OLMo-2-1124-7B-Instruct` | AI2 | 7.3 B |
| M4 | `ibm-granite/granite-3.3-8b-instruct` | IBM | 8.2 B |

Reserve: `Qwen/Qwen3-8B` (same lineage as M1, useful for a within-family contrast that
isolates *architectural* diversity from *lineage* diversity).

**Parameter band 7.2–8.2 B** — tight, though parameter count is not capability and the
matching that matters is on measured isolated accuracy (AMD-0001 §4).

## 3. Why Llama and Gemma are excluded — and why that is an improvement

Both are **`manual` gated** and carry **custom licences with acceptable-use policies**.
Three consequences, in increasing order of importance:

1. **Reproducibility friction.** A gated model means anyone re-running this work must
   individually request and be granted access. For a public artefact under `DR-0010` whose
   whole point is that others can check it, that is a real cost.
2. **We could not read the terms.** Attempting to retrieve the Llama 3.1 acceptable-use
   policy returned `HTTP 401 — Access to model … is restricted`. The policy governing use is
   itself behind the gate. Accepting terms we have not read, for a study whose method is
   generating false factual claims, is not defensible.
3. **`OQ-0040`, applied to weights rather than APIs.** Both policies contain prohibited-use
   provisions. This study instructs models to argue persuasively for falsehoods — squarely
   the kind of activity such clauses are written about. **Apache-2.0 and MIT impose no
   use restrictions at all**, so choosing them removes the question entirely rather than
   requiring us to argue our way through it.

This is not a compromise forced by circumstance. For *this* study it is the better pool.

## 4. A specific asset: OLMo-2 is fully open

`allenai/OLMo-2` releases training **data** as well as weights. For a project whose central
construct is *why models fail differently*, having one member whose pretraining corpus is
inspectable is unusual and valuable — it converts "these models are diverse" from an
assertion about provenance into something partially checkable.

Worth stating in the paper as a reason for the pool's composition rather than leaving it as
a coincidence.

## 5. What this does not settle

- **Capability matching is unresolved until measured.** Parameter count is not capability.
  `EXP-000` measures isolated accuracy per model on the validated fact suite; cohorts are
  then constructed at matched `ā` (AMD-0001 §4). It is entirely possible that these four
  differ enough in accuracy that exact matching is impossible, in which case the bracketing
  strategy in AMD-0001 §4.3 applies.
- **Capability *spread* matters as well as the mean** (`OQ-0047`). Report both.
- **Chat templates differ across families.** Each model's own template must be applied, but
  the *content* placed inside it must be byte-identical across agents (`OQ-0046`) — otherwise
  architectural diversity is confounded with prompt diversity, which Zhou & Chen show is
  worth up to 3.5% on its own (`LIT-0002`).
- **Download size.** Four models at ~15 GB each in bf16 is ~60 GB of weights to cache. Not a
  blocker but worth planning for on a metered connection.

## 6. Before this is frozen

- [ ] Confirm each model's chat template and stop tokens
- [ ] Confirm vLLM support for each at the pinned version
- [ ] `EXP-000` measures isolated accuracy per model per candidate fact
- [ ] Cohorts constructed at matched `ā`, with spread reported
- [ ] Record exact revision SHAs, not just model names — "Qwen2.5-7B-Instruct" is not a
      reproducible identifier if the repo is updated (SOP-040 §5)
