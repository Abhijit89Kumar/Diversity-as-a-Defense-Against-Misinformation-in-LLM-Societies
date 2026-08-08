---
id: SOP-040
title: Code & Reproducibility
status: ACTIVE
version: 1.0
created: 2026-08-07
---

# SOP-040 — Code & Reproducibility

Governs the codebase. Derives from SOP-000 P6.

The bar: **a stranger with the repository and API keys can reproduce every number in
the paper.** Not "could in principle" — has been tested.

---

## 1. Environment

- Python version pinned in `pyproject.toml` (`requires-python`).
- Dependencies pinned to exact versions in a lockfile (`uv.lock` or
  `requirements.lock`). Loose ranges belong in `pyproject.toml`; the lockfile is what
  reproduces.
- `.env.example` lists every environment variable by name. **Never commit real keys.**
  `.env` is gitignored. If a key is ever committed, it is rotated immediately — not
  "removed in a later commit"; git history is public.
- Record the platform (OS, CPU/GPU, CUDA, driver) in every experiment card. vLLM
  numerics are hardware-dependent.

## 2. Determinism — and its limits

Be precise about what is and is not reproducible, because LLM pipelines are not
bit-reproducible and claiming otherwise invites a reviewer to disprove it.

| Layer | Reproducible? | How we handle it |
|---|---|---|
| Graph generation | Yes | Seeded NetworkX; seed recorded |
| Agent→node assignment | Yes | Seeded permutation; seed recorded |
| Prompt construction | Yes | Templates versioned and hashed |
| Message sampling (T > 0) | No | Record every generated message verbatim; downstream analysis replays from logs, not from the API |
| Message sampling (T = 0) | Partially | Still not guaranteed across serving-stack versions |
| Provider model weights | **No** | Providers update silently. Record model ID **and** any version/fingerprint the API returns, plus the UTC timestamp of every call. |

**Consequence, and it is a load-bearing one:** the durable scientific artefact is the
**logged trajectory dataset**, not the ability to re-hit the APIs. Analysis must be a
pure function of the logged data. Design the pipeline so that re-running analysis
never requires re-running generation.

## 3. Repository hygiene

- `src/llm_society_sim/` — importable package. No experiment logic in scripts that
  cannot be imported and tested.
- Every module has a docstring stating which specification section it implements.
- Type hints throughout; `mypy` or `pyright` in CI.
- `ruff` for lint and format. One command: `make check`.
- **Tests are not optional for anything that touches a number in the paper.** At
  minimum: topology builders (degree distributions, connectivity), the memory
  operator (token budget respected, system prompt pinned, pruning order correct), the
  belief metric (known-input → known-output), metric computations (TRR/MP/BPI on
  hand-constructed trajectories with known answers), and the analysis functions
  (recover a planted effect from synthetic data).
- **Synthetic-data end-to-end test:** generate fake trajectories with a known,
  planted effect and confirm the analysis pipeline recovers it. This catches the class
  of bug where the pipeline reports significance because of an indexing error. Run it
  before G4.

## 4. Configuration

- All experiment parameters live in versioned config files under `configs/`, never as
  literals in code and never as ad-hoc CLI flags for confirmatory runs.
- Every run records the **hash of its resolved config** (after defaults and overrides
  are applied) in its output.
- Config schema validated (Pydantic) at load time. Fail loudly on unknown keys —
  silently-ignored typos in a config file have ended experiments.

## 5. Run identity

Every run emits a manifest containing at least:

```
run_id, config_hash, git_commit, git_dirty (bool),
topology_type, topology_seed, population_type, agent_assignment_seed,
fact_id, prompt_template_version, prompt_seed,
per-agent: {model_id, provider, provider_version_string, temperature},
started_at_utc, finished_at_utc,
api_calls: {n_success, n_retry, n_failed, total_prompt_tokens, total_completion_tokens},
cost_estimate_usd,
software_versions: {python, vllm, transformers, networkx, tiktoken, ...}
```

`git_dirty = true` on a confirmatory run invalidates that run. Commit before you launch.

## 6. Failure handling — a scientific issue, not just an engineering one

The v1.0 router design returns a placeholder string (`"[Agent Error: Latency drop]"`)
after three failed attempts. That string would then enter another agent's context as
if it were a message. Two consequences:

1. It silently corrupts the experiment — a failed call becomes a data point.
2. Failure rates almost certainly differ across providers, so the corruption is
   **correlated with the experimental condition**. That is a confound in the primary
   comparison.

**Required policy:** every API failure is recorded with agent, round, provider, error
class, and attempt count. The preregistration states the handling rule in advance —
retry to exhaustion, drop the run, or impute — and the paper reports failure rates
per provider. A run whose failure count exceeds the preregistered threshold is
excluded by rule, not by judgement after seeing its outcome.

## 7. Version control

- `git init` at the root; everything except secrets, large data, and caches is tracked.
- Small, described commits. Reference `DR-xxxx` / `EXP-xxx` in messages where relevant.
- Tag the phase gates: `g1-design-frozen`, `prereg-frozen`, `g3-matrix-launch`,
  `submission-v1`.
- Large artefacts (trajectory data, figures over a few MB) go to a release, Hugging
  Face dataset, or Zenodo — not into git history. See SOP-050.

## 8. Release readiness (G5)

- `README` with install, quickstart, and one command that reproduces a headline figure.
- LICENSE (MIT per SPEC-4).
- `CITATION.cff`.
- Archived DOI (Zenodo) for the exact commit cited in the paper.
- A clean-machine test: fresh clone, fresh venv, run the reproduction command. If it
  fails, the release is not ready.

---

## Changelog

| Version | Date | Change | DR |
|---|---|---|---|
| 1.0 | 2026-08-07 | Initial issue | DR-0001 |
