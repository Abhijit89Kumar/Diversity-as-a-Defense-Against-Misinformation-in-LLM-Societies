"""Configuration schemas.

Implements SOP-040 §4: all experiment parameters live in versioned config files, never as
literals in code and never as ad-hoc CLI flags for confirmatory runs. Unknown keys are a hard
error -- a silently-ignored typo in a config file has ended experiments.

Design of record: AMD-0001 (design) and AMD-0002 (metrics, communication-budget convention).
"""

from __future__ import annotations

import hashlib
import json
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

__all__ = [
    "Topology",
    "BudgetConvention",
    "AgentSpec",
    "CohortSpec",
    "TopologySpec",
    "MemorySpec",
    "ProbeSpec",
    "RunSpec",
    "config_hash",
]


class _Strict(BaseModel):
    """Base: reject unknown keys, freeze after construction."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class Topology(StrEnum):
    COMPLETE = "complete"
    ERDOS_RENYI = "erdos_renyi"
    WATTS_STROGATZ = "watts_strogatz"
    ISOLATED = "isolated"  # the no-communication control arm (AMD-0001 §6)


class BudgetConvention(StrEnum):
    """How much each agent hears per round (AMD-0002 §7).

    This is not a detail. Niu et al. (arXiv:2607.21912) prove the *sign* of the topology
    effect depends on it: under fixed per-edge exposure adding edges raises infection risk,
    while under a fixed sender budget the first-order threshold is independent of density.
    A topology comparison that does not fix and state a convention is arguable as an artefact.
    """

    PER_RECEIVER = "per_receiver"  # primary: every agent receives at most k messages
    PER_EDGE = "per_edge"  # sensitivity: every agent sends to every out-neighbour


class AgentSpec(_Strict):
    """One model in the pool.

    `revision` is required for confirmatory runs: "Qwen2.5-7B-Instruct" is not a reproducible
    identifier if the repository is updated (SOP-040 §5).
    """

    model_id: str
    revision: str | None = None
    backend: Literal["stub", "vllm", "openai_compatible"] = "stub"
    temperature: float = Field(0.0, ge=0.0, le=2.0)
    max_tokens: int = Field(160, gt=0)


class CohortSpec(_Strict):
    """A population composition — one rung of the diversity ladder (AMD-0001 §3)."""

    name: str
    level: Literal["D0", "D1", "D2", "D3", "D4"]
    members: list[AgentSpec] = Field(min_length=1)
    personas: list[str] = Field(default_factory=lambda: ["analyst"])
    measured_accuracy: float | None = Field(
        None, ge=0.0, le=1.0,
        description="Mean isolated accuracy ā(c). Required before confirmatory runs — it is "
                    "the capability control (AMD-0001 §4). None until EXP-000 measures it.",
    )
    measured_diversity: float | None = Field(
        None, description="H(c), error-decorrelation (AMD-0001 §5). None until measured.",
    )

    @model_validator(mode="after")
    def _check_ladder_consistency(self) -> CohortSpec:
        # Validate persona names against the template registry. Imported lazily to keep the
        # config module free of a prompt dependency at import time.
        from .prompts import PERSONAS

        unknown = set(self.personas) - set(PERSONAS)
        if unknown:
            raise ValueError(
                f"unknown persona(s) {sorted(unknown)}; known: {sorted(PERSONAS)}. "
                "Personas must exist in the versioned template registry so the prompt hash "
                "covers everything an agent actually sees (SOP-040 §5)."
            )
        if len(set(self.personas)) != len(self.personas):
            raise ValueError("duplicate personas would inflate apparent persona diversity")

        families = {m.model_id for m in self.members}
        if self.level in ("D0", "D1", "D2") and len(families) != 1:
            raise ValueError(
                f"{self.level} must use a single model; got {len(families)}. "
                "D0-D2 isolate stochastic and persona decorrelation from architectural."
            )
        if self.level in ("D3", "D4") and len(families) < 2:
            raise ValueError(f"{self.level} requires >= 2 model families; got {len(families)}.")
        if self.level == "D0" and any(m.temperature > 0 for m in self.members):
            raise ValueError("D0 is the deterministic baseline; temperature must be 0.")
        if self.level == "D1" and not any(m.temperature > 0 for m in self.members):
            raise ValueError("D1's only source of decorrelation is sampling; temperature must be > 0.")
        if self.level in ("D0", "D1", "D3") and len(self.personas) != 1:
            raise ValueError(
                f"{self.level} must use exactly one persona. Prompts are byte-identical across "
                "agents except the seed persona (OQ-0046) -- role diversity is worth up to 3.5% "
                "on its own (Zhou & Chen 2025) and would confound the architectural comparison."
            )
        if self.level in ("D2", "D4") and len(self.personas) < 2:
            raise ValueError(f"{self.level} manipulates persona diversity; needs >= 2 personas.")
        return self


class TopologySpec(_Strict):
    kind: Topology
    n_agents: int = Field(20, ge=2)
    er_p: float = Field(0.2, ge=0.0, le=1.0, description="Erdős–Rényi edge probability")
    ws_k: int = Field(4, ge=2, description="Watts–Strogatz ring degree (must be even)")
    ws_p: float = Field(0.1, ge=0.0, le=1.0, description="Watts–Strogatz rewiring probability")

    @model_validator(mode="after")
    def _check(self) -> TopologySpec:
        if self.kind is Topology.WATTS_STROGATZ:
            if self.ws_k % 2:
                raise ValueError("ws_k must be even for a Watts–Strogatz ring lattice")
            if self.ws_k >= self.n_agents:
                raise ValueError("ws_k must be < n_agents")
        return self


class MemorySpec(_Strict):
    """Bounded context operator M_φ."""

    token_budget: int = Field(2000, gt=0)
    keep_system_prompt: bool = True
    strategy: Literal["recency"] = "recency"


class ProbeSpec(_Strict):
    """Belief measurement (AMD-0002 §1.1).

    Both the true and the false claim are probed separately -- they are not logical negations,
    and distinguishing "abandoned the truth" from "adopted the falsehood" is the point.
    """

    n_paraphrases: int = Field(3, ge=1, description="M. Odd values avoid ties on the majority.")
    probe_rounds: list[int] | None = Field(
        None, description="Rounds to probe at; None means every round. Reducing cadence is a "
                          "legitimate cost saving ONLY if fixed a priori (SOP-030 §1.5).",
    )
    randomise_option_order: bool = True

    @model_validator(mode="after")
    def _warn_even(self) -> ProbeSpec:
        if self.n_paraphrases % 2 == 0:
            raise ValueError(
                "n_paraphrases must be odd so the majority vote cannot tie; "
                f"got {self.n_paraphrases}."
            )
        return self


class RunSpec(_Strict):
    """Everything needed to reproduce one simulation run."""

    run_id: str
    cohort: CohortSpec
    topology: TopologySpec
    memory: MemorySpec = MemorySpec()
    probe: ProbeSpec = ProbeSpec()

    fact_id: str
    n_rounds: int = Field(5, ge=1)
    n_seeds: int = Field(2, ge=0)
    budget_convention: BudgetConvention = BudgetConvention.PER_RECEIVER
    receiver_budget: int = Field(
        4, ge=1,
        description="k in the per-receiver convention. Should equal the minimum in-degree "
                    "across the topology set so no configuration needs up-sampling.",
    )

    # Four independent randomisations, seeded separately so each can be held fixed or
    # resampled per replication without entangling the others (SOP-030 §4).
    seed_topology: int = 0
    seed_assignment: int = 0
    seed_message_budget: int = 0
    seed_sampling: int = 0

    prompt_template_version: str = "v0.1"

    @model_validator(mode="after")
    def _check(self) -> RunSpec:
        if self.n_seeds >= self.topology.n_agents:
            raise ValueError("at least one non-seeded agent is required for any outcome")
        if self.topology.kind is Topology.ISOLATED and self.n_seeds:
            raise ValueError(
                "the isolated control arm exchanges no messages, so seeding it is meaningless"
            )
        return self

    @property
    def seeding_density(self) -> float:
        """σ — renamed from ρ, which collides with the spectral radius in prior work (OQ-0035)."""
        return self.n_seeds / self.topology.n_agents


def config_hash(spec: RunSpec) -> str:
    """SHA-256 of the fully-resolved config.

    Recorded with every run (SOP-040 §5) so a result can always be traced to the exact
    configuration that produced it, after defaults and overrides are applied.
    """
    payload = json.dumps(spec.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
