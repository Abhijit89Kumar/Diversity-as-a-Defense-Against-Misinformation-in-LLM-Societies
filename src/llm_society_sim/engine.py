"""Simulation orchestrator.

Implements the run protocol in AMD-0001 and the measurement in AMD-0002 §1.

Per round:
    1. **Probe** every agent on the true claim and the false claim separately, M paraphrases
       each, majority vote -> discrete state.
    2. **Generate** one broadcast message per agent (skipped after the final probe).
    3. **Route** messages, subject to the communication-budget convention (AMD-0002 §7).

Round 0 is probed *before* any messages are exchanged, so `states[:, 0]` is the pre-interaction
baseline. That column is what defines the risk sets in `analysis/survival.py`: agents starting
in HOLDS enter the capitulation risk set, agents starting elsewhere enter the truth-acquisition
risk set.

Everything needed to reproduce a run is emitted in the manifest (SOP-040 §5). Analysis reads
the logged trajectory, never the API (SOP-040 §2).
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Mapping, Sequence

import numpy as np

from . import prompts as pt
from .backends import Backend, Generation, ProbeAnswer
from .config import BudgetConvention, RunSpec, Topology, config_hash
from .memory import BoundedMemory, Message
from .prompts import FactPrompt
from .topology import adjacency_matrix, build_graph, graph_summary, sample_incoming
from .types import BeliefState, RunTrajectory, states_from_endorsements

__all__ = ["RunResult", "SimulationEngine"]


@dataclass(slots=True)
class RunResult:
    """One completed run: the trajectory plus everything needed to audit it."""

    trajectory: RunTrajectory
    manifest: dict
    messages: list[Message] = field(default_factory=list)
    call_log: list[dict] = field(default_factory=list)
    probe_log: list[dict] = field(default_factory=list)

    @property
    def failure_count(self) -> int:
        return sum(1 for c in self.call_log if c.get("error"))


class SimulationEngine:
    """Runs one simulation.

    Args:
        spec: Fully-resolved run configuration.
        backends: Backend per ``model_id``. One backend may serve many agents; backends are
            stateless across agents, so all agent state lives here.
        fact: The claim pair under discussion.
    """

    def __init__(self, spec: RunSpec, backends: Mapping[str, Backend], fact: FactPrompt) -> None:
        self.spec = spec
        self.fact = fact
        self.backends = dict(backends)

        missing = {m.model_id for m in spec.cohort.members} - set(self.backends)
        if missing:
            raise KeyError(f"no backend supplied for: {sorted(missing)}")

        self.n = spec.topology.n_agents
        self.graph = build_graph(spec.topology, seed=spec.seed_topology)

        # Agents are assigned to nodes by a seeded permutation, so which model sits at which
        # graph position is randomised independently of the topology realisation (SOP-030 §4).
        rng_assign = np.random.default_rng(spec.seed_assignment)
        order = rng_assign.permutation(self.n)
        members = spec.cohort.members
        personas = spec.cohort.personas
        self.agent_model = [members[int(order[i]) % len(members)] for i in range(self.n)]
        self.agent_persona = [personas[int(order[i]) % len(personas)] for i in range(self.n)]

        # Seeds are the *lowest-numbered* nodes after permutation, i.e. an arbitrary but
        # reproducible subset. Seed placement relative to graph structure is a covariate
        # (distance-to-nearest-seed), not something to optimise.
        self.seed_agents = frozenset(range(spec.n_seeds))

        self._rng_budget = np.random.default_rng(spec.seed_message_budget)

        # Memory uses each backend's own tokenizer; a shared tokenizer would make the context
        # budget mean different amounts of text per family (memory.py).
        self.memory = {
            m.model_id: BoundedMemory(
                spec.memory.token_budget, counter=self.backends[m.model_id].token_counter()
            )
            for m in members
        }

    # ------------------------------------------------------------------ system prompts

    def _system_prompt(self, agent: int) -> str:
        if agent in self.seed_agents:
            return pt.seed_system_prompt(self.fact, certainty="high")
        return pt.neutral_system_prompt(self.agent_persona[agent])

    # ------------------------------------------------------------------ seeds

    def _agent_seed(self, agent: int) -> int:
        """Stable per-agent sampling identity for this run.

        Deliberately **does not vary with round or paraphrase index**. A deterministic
        backend must be a pure function of its context, because that is what a real model at
        temperature 0 is. Folding the round into the seed made belief drift even when no
        messages were delivered — which two engine tests caught.
        """
        return self.spec.seed_sampling * 1_000_003 + agent

    def _call_seed(self, agent: int, round_index: int, temperature: float) -> int:
        """Sampling seed for a generation call.

        Varies by round only when temperature > 0, so stochastic decorrelation (the D1 rung of
        the ladder) is modelled while a temperature-0 cohort stays reproducible.
        """
        base = self._agent_seed(agent)
        return base + (7919 * round_index if temperature > 0 else 0)

    # ------------------------------------------------------------------ probing

    def _probe_claim(
        self, agent: int, claim: str, history: Sequence[Message], round_index: int, which: str
    ) -> tuple[bool | None, float]:
        """Probe one claim with M paraphrases; return (majority, agreement).

        `agreement` is the share of parseable probes matching the majority — the instrument
        reliability statistic required by `CONSTRUCT-VALIDITY-BELIEF-METRIC.md` §2.1. It is
        reported separately from belief gradedness, which is a different thing entirely.
        """
        spec = self.spec
        backend = self.backends[self.agent_model[agent].model_id]
        system = self._system_prompt(agent)

        swap = spec.probe.randomise_option_order and (agent + round_index) % 2 == 1
        questions = pt.probe_prompts(claim, spec.probe.n_paraphrases, swap_order=swap)

        answers: list[bool] = []
        for k, q in enumerate(questions):
            res: ProbeAnswer = backend.probe(
                system=system,
                history=history,
                question=q,
                seed=self._agent_seed(agent),
            )
            self.probe_log.append(
                {
                    "run_id": spec.run_id, "agent": agent, "round": round_index,
                    "claim": which, "paraphrase": k, "swap_order": swap,
                    "answer": res.answer, "raw": res.raw, "error": res.error,
                }
            )
            if res.ok:
                answers.append(bool(res.answer))

        if not answers:
            return None, float("nan")
        n_true = sum(answers)
        majority = n_true * 2 > len(answers)
        agreement = (n_true if majority else len(answers) - n_true) / len(answers)
        return majority, agreement

    def _probe_round(self, round_index: int, contexts: Mapping[int, list[Message]]) -> np.ndarray:
        """Probe every agent, returning the (n,) state column for this round."""
        b = np.zeros(self.n, dtype=bool)
        m = np.zeros(self.n, dtype=bool)
        for agent in range(self.n):
            history = contexts.get(agent, [])
            bt, _ = self._probe_claim(agent, self.fact.s_true, history, round_index, "s_true")
            mt, _ = self._probe_claim(agent, self.fact.s_false, history, round_index, "s_false")
            # An unparseable probe is not evidence of endorsement. Treating None as False for
            # both yields DESTABILISED, which is the honest "we could not read this agent"
            # state -- and the incoherence/unparseable rate is logged so it cannot hide.
            b[agent] = bool(bt) if bt is not None else False
            m[agent] = bool(mt) if mt is not None else False
        return states_from_endorsements(b, m)

    # ------------------------------------------------------------------ messaging

    def _generate_round(
        self, round_index: int, contexts: Mapping[int, list[Message]]
    ) -> list[Message]:
        """One broadcast message per agent. Failures are logged and produce no message."""
        spec = self.spec
        out: list[Message] = []
        turn = pt.discussion_turn_prompt(self.fact, round_index)

        for agent in range(self.n):
            cfg = self.agent_model[agent]
            backend = self.backends[cfg.model_id]
            system = self._system_prompt(agent)
            history, trunc = self.memory[cfg.model_id].prune(system, contexts.get(agent, []))

            res: Generation = backend.generate(
                system=system, turn=turn, history=history,
                max_tokens=cfg.max_tokens, temperature=cfg.temperature,
                seed=self._call_seed(agent, round_index, cfg.temperature),
            )
            self.call_log.append(
                {
                    "run_id": spec.run_id, "agent": agent, "round": round_index,
                    "model_id": cfg.model_id, "backend": backend.name,
                    "prompt_tokens": res.prompt_tokens, "completion_tokens": res.completion_tokens,
                    "finish_reason": res.finish_reason, "error": res.error,
                    "context_kept": trunc["kept"], "context_dropped": trunc["dropped"],
                }
            )
            if res.ok:
                out.append(
                    Message(
                        sender=agent, round=round_index, content=res.text,
                        stance=res.meta.get("stance"),
                    )
                )
            # SOP-040 §6: a failed call contributes NO message. It never becomes a
            # placeholder string in a neighbour's context -- failure rates differ by model,
            # so that corruption would correlate with the experimental condition.
        return out

    def _route(self, messages: Sequence[Message]) -> dict[int, list[Message]]:
        """Deliver messages, honouring the communication-budget convention (AMD-0002 §7)."""
        by_sender = {msg.sender: msg for msg in messages}
        delivered: dict[int, list[Message]] = defaultdict(list)
        if self.spec.topology.kind is Topology.ISOLATED:
            return delivered

        for agent in range(self.n):
            senders = sample_incoming(
                self.graph, agent,
                self.spec.budget_convention, self.spec.receiver_budget, self._rng_budget,
            )
            for s in senders:
                if s in by_sender:
                    delivered[agent].append(by_sender[s])
        return delivered

    # ------------------------------------------------------------------ run

    def run(self) -> RunResult:
        spec = self.spec
        self.call_log: list[dict] = []
        self.probe_log: list[dict] = []
        all_messages: list[Message] = []

        contexts: dict[int, list[Message]] = defaultdict(list)
        columns: list[np.ndarray] = []

        # t = 0: baseline, before any communication.
        columns.append(self._probe_round(0, contexts))

        for t in range(1, spec.n_rounds + 1):
            produced = self._generate_round(t, contexts)
            all_messages.extend(produced)
            for agent, msgs in self._route(produced).items():
                contexts[agent].extend(msgs)
            columns.append(self._probe_round(t, contexts))

        states = np.column_stack(columns).astype(np.int8)

        # Seeded agents are pinned: they hold the injected claim by construction (SPEC-3
        # §3.1). They are excluded from every outcome denominator downstream.
        for s in self.seed_agents:
            states[s, :] = BeliefState.CAPITULATED

        trajectory = RunTrajectory(
            run_id=spec.run_id,
            states=states,
            seed_agents=self.seed_agents,
            h_cohort=spec.cohort.measured_diversity if spec.cohort.measured_diversity is not None else float("nan"),
            a_bar=spec.cohort.measured_accuracy if spec.cohort.measured_accuracy is not None else float("nan"),
            condition=spec.cohort.level,
            adjacency=adjacency_matrix(self.graph, self.n),
            failure_count=sum(1 for c in self.call_log if c.get("error")),
        )

        unparseable = sum(1 for p in self.probe_log if p["answer"] is None)
        manifest = {
            "run_id": spec.run_id,
            "config_hash": config_hash(spec),
            "prompt_template_version": pt.TEMPLATE_VERSION,
            "prompt_template_hash": pt.template_hash(),
            "fact_id": spec.fact_id,
            "cohort": {
                "name": spec.cohort.name, "level": spec.cohort.level,
                "measured_accuracy": spec.cohort.measured_accuracy,
                "measured_diversity": spec.cohort.measured_diversity,
                "members": [m.model_dump(mode="json") for m in spec.cohort.members],
                "personas": list(spec.cohort.personas),
            },
            "topology": {**spec.topology.model_dump(mode="json"), **graph_summary(self.graph)},
            "budget_convention": str(spec.budget_convention),
            "receiver_budget": spec.receiver_budget,
            "n_rounds": spec.n_rounds,
            "n_seeds": spec.n_seeds,
            "seeding_density_sigma": spec.seeding_density,
            "seeds": {
                "topology": spec.seed_topology, "assignment": spec.seed_assignment,
                "message_budget": spec.seed_message_budget, "sampling": spec.seed_sampling,
            },
            "agent_assignment": [
                {"agent": i, "model_id": self.agent_model[i].model_id,
                 "persona": self.agent_persona[i], "seeded": i in self.seed_agents}
                for i in range(self.n)
            ],
            "calls": {
                "n": len(self.call_log),
                "n_failed": sum(1 for c in self.call_log if c.get("error")),
                "prompt_tokens": sum(c["prompt_tokens"] for c in self.call_log),
                "completion_tokens": sum(c["completion_tokens"] for c in self.call_log),
            },
            "probes": {
                "n": len(self.probe_log),
                "n_unparseable": unparseable,
                "unparseable_rate": unparseable / len(self.probe_log) if self.probe_log else 0.0,
            },
        }

        return RunResult(
            trajectory=trajectory, manifest=manifest,
            messages=all_messages, call_log=self.call_log, probe_log=self.probe_log,
        )
