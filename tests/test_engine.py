"""Engine, topology, memory and config tests.

Required by SOP-040 §3. These exercise the plumbing that produces every trajectory: if the
engine routes a message to the wrong agent, truncates the wrong end of a context, or lets a
failed call become a message, no amount of downstream statistical care would catch it.
"""

from __future__ import annotations

import numpy as np
import pytest
from pydantic import ValidationError

from llm_society_sim.backends import StubBackend, parse_true_false
from llm_society_sim.config import (
    AgentSpec,
    BudgetConvention,
    CohortSpec,
    RunSpec,
    Topology,
    TopologySpec,
    config_hash,
)
from llm_society_sim.engine import SimulationEngine
from llm_society_sim.memory import BoundedMemory, Message, heuristic_token_count
from llm_society_sim.prompts import FactPrompt, probe_prompts, seed_system_prompt, template_hash
from llm_society_sim.topology import adjacency_matrix, build_graph, in_neighbours, sample_incoming
from llm_society_sim.types import BeliefState

FACT = FactPrompt(
    fact_id="F-017",
    s_true="The adult human skeleton normally contains 206 bones.",
    s_false="The adult human skeleton normally contains 245 bones.",
    authority_frame="a revised anatomical enumeration",
)


def _cohort(level: str = "D3") -> CohortSpec:
    if level in ("D0", "D1", "D2"):
        members = [AgentSpec(model_id="qwen2.5-7b", temperature=0.0 if level == "D0" else 0.7)]
        personas = ["analyst"] if level != "D2" else ["analyst", "sceptic"]
    else:
        members = [AgentSpec(model_id=m) for m in ("qwen2.5-7b", "mistral-7b", "olmo2-7b")]
        personas = ["analyst"] if level == "D3" else ["analyst", "sceptic"]
    return CohortSpec(
        name=f"{level}-test", level=level, members=members, personas=personas,
        measured_accuracy=0.6, measured_diversity=0.5,
    )


def _spec(**kw) -> RunSpec:
    base = dict(
        run_id="t", cohort=_cohort(),
        topology=TopologySpec(kind=Topology.WATTS_STROGATZ, n_agents=12),
        fact_id="F-017", n_rounds=3, n_seeds=2, receiver_budget=3,
    )
    base.update(kw)
    return RunSpec(**base)


def _backends(cohort: CohortSpec, **kw):
    return {
        m.model_id: StubBackend(s_false=FACT.s_false, **kw) for m in cohort.members
    }


def _run(spec: RunSpec, **kw):
    return SimulationEngine(spec, _backends(spec.cohort, **kw), FACT).run()


# ------------------------------------------------------------------------------- config


def test_d3_requires_multiple_families():
    with pytest.raises(ValidationError, match="requires >= 2 model families"):
        CohortSpec(name="x", level="D3", members=[AgentSpec(model_id="only-one")])


def test_d0_must_be_deterministic():
    with pytest.raises(ValidationError, match="temperature must be 0"):
        CohortSpec(name="x", level="D0", members=[AgentSpec(model_id="m", temperature=0.7)])


def test_d3_must_hold_persona_fixed():
    """OQ-0046: role diversity would confound the architectural comparison."""
    with pytest.raises(ValidationError, match="exactly one persona"):
        CohortSpec(
            name="x", level="D3",
            members=[AgentSpec(model_id="a"), AgentSpec(model_id="b")],
            personas=["analyst", "sceptic"],
        )


def test_unknown_persona_rejected():
    with pytest.raises(ValidationError, match="unknown persona"):
        CohortSpec(name="x", level="D0", members=[AgentSpec(model_id="m")], personas=["wizard"])


def test_unknown_config_key_is_an_error():
    """A silently-ignored typo in a config file has ended experiments (SOP-040 §4)."""
    with pytest.raises(ValidationError):
        AgentSpec(model_id="m", temprature=0.7)  # noqa: typo intentional


def test_isolated_arm_cannot_be_seeded():
    with pytest.raises(ValidationError, match="seeding it is meaningless"):
        _spec(topology=TopologySpec(kind=Topology.ISOLATED, n_agents=8), n_seeds=2)


def test_config_hash_is_stable_and_sensitive():
    a, b = _spec(), _spec()
    assert config_hash(a) == config_hash(b)
    assert config_hash(a) != config_hash(_spec(n_rounds=4))


def test_even_paraphrase_count_rejected():
    """A tie on the majority vote would have no defined resolution."""
    from llm_society_sim.config import ProbeSpec

    with pytest.raises(ValidationError, match="must be odd"):
        ProbeSpec(n_paraphrases=2)


# ----------------------------------------------------------------------------- topology


def test_adjacency_orientation_is_receiver_from_sender():
    """a[i, j] != 0 means i RECEIVES from j -- the transpose of NetworkX's convention.

    Getting this backwards would silently invert every topology result.
    """
    spec = TopologySpec(kind=Topology.COMPLETE, n_agents=4)
    g = build_graph(spec, seed=0)
    g_dir = g.copy()
    g_dir.remove_edge(0, 1)  # 0 no longer sends to 1
    a = adjacency_matrix(g_dir, 4)
    assert a[1, 0] == 0, "1 should no longer receive from 0"
    assert a[0, 1] != 0, "1 still sends to 0"


def test_isolated_graph_has_no_edges():
    g = build_graph(TopologySpec(kind=Topology.ISOLATED, n_agents=6), seed=0)
    assert g.number_of_edges() == 0
    assert g.number_of_nodes() == 6


def test_no_self_loops():
    for kind in (Topology.COMPLETE, Topology.ERDOS_RENYI, Topology.WATTS_STROGATZ):
        g = build_graph(TopologySpec(kind=kind, n_agents=10), seed=1)
        assert not any(u == v for u, v in g.edges())


def test_topology_seed_changes_realisation():
    """SPEC-2 v1.0 hard-coded seed=42, so topology variance was never sampled."""
    s = TopologySpec(kind=Topology.ERDOS_RENYI, n_agents=30)
    e1 = set(build_graph(s, seed=1).edges())
    e2 = set(build_graph(s, seed=2).edges())
    assert e1 != e2


def test_per_receiver_budget_caps_incoming():
    g = build_graph(TopologySpec(kind=Topology.COMPLETE, n_agents=12), seed=0)
    rng = np.random.default_rng(0)
    got = sample_incoming(g, 3, BudgetConvention.PER_RECEIVER, 4, rng)
    assert len(got) == 4
    assert set(got) <= set(in_neighbours(g, 3))
    assert 3 not in got


def test_per_edge_convention_delivers_everything():
    g = build_graph(TopologySpec(kind=Topology.COMPLETE, n_agents=12), seed=0)
    rng = np.random.default_rng(0)
    got = sample_incoming(g, 3, BudgetConvention.PER_EDGE, 4, rng)
    assert len(got) == 11


def test_budget_does_not_upsample_when_degree_is_small():
    g = build_graph(TopologySpec(kind=Topology.WATTS_STROGATZ, n_agents=12, ws_k=4), seed=0)
    rng = np.random.default_rng(0)
    got = sample_incoming(g, 0, BudgetConvention.PER_RECEIVER, 99, rng)
    assert len(got) == len(in_neighbours(g, 0))


# ------------------------------------------------------------------------------- memory


def test_memory_keeps_the_most_recent_messages():
    mem = BoundedMemory(token_budget=heuristic_token_count("sys") + 4)
    hist = [Message(sender=i, round=1, content="aaaa") for i in range(5)]  # 1 token each
    kept, stats = mem.prune("sys", hist)
    assert [m.sender for m in kept] == [1, 2, 3, 4], "should keep the newest, in order"
    assert stats["dropped"] == 1


def test_memory_records_truncation_rather_than_hiding_it():
    mem = BoundedMemory(token_budget=heuristic_token_count("sys") + 1)
    hist = [Message(sender=i, round=1, content="aaaa") for i in range(10)]
    _, stats = mem.prune("sys", hist)
    assert stats["dropped"] == 9 and stats["kept"] == 1


def test_memory_can_be_fully_consumed_by_the_system_prompt():
    mem = BoundedMemory(token_budget=2)
    kept, stats = mem.prune("a" * 400, [Message(sender=0, round=1, content="hello")])
    assert kept == [] and stats["tokens_available"] == 0


# ------------------------------------------------------------------------------ prompts


def test_seed_prompt_contains_the_falsehood_and_no_named_organisation():
    p = seed_system_prompt(FACT)
    assert FACT.s_false in p
    for banned in ("NIST", "IAU", "NASA", "WHO", "FDA"):
        assert banned not in p, "DR-0010: no fabricated attribution to a real body"


def test_probe_paraphrases_are_distinct():
    qs = probe_prompts("X", 3)
    assert len(set(qs)) == 3
    assert all("X" in q for q in qs)


def test_probe_order_swap_is_available_as_a_nuisance_factor():
    normal = probe_prompts("X", 1)[0]
    swapped = probe_prompts("X", 1, swap_order=True)[0]
    assert "TRUE or FALSE" in normal and "FALSE or TRUE" in swapped


def test_requesting_more_paraphrases_than_exist_is_an_error():
    with pytest.raises(ValueError, match="probe forms are defined"):
        probe_prompts("X", 99)


def test_template_hash_is_stable():
    assert template_hash() == template_hash()


def test_parse_true_false_refuses_to_guess():
    assert parse_true_false("TRUE") is True
    assert parse_true_false("false") is False
    assert parse_true_false("TRUE or FALSE") is None, "ambiguous must not be coerced"
    assert parse_true_false("maybe") is None


# ------------------------------------------------------------------------------- engine


def test_engine_is_deterministic_under_identical_seeds():
    a, b = _run(_spec()), _run(_spec())
    assert np.array_equal(a.trajectory.states, b.trajectory.states)
    assert a.manifest["config_hash"] == b.manifest["config_hash"]


def test_seeded_agents_are_pinned_to_capitulated():
    res = _run(_spec())
    for s in res.trajectory.seed_agents:
        assert (res.trajectory.states[s] == BeliefState.CAPITULATED).all()


def test_baseline_column_has_no_capitulation_among_non_seeded():
    """At t=0 no agent has been exposed to the falsehood.

    An agent that does not know the fact must be DESTABILISED, not CAPITULATED. Collapsing
    these empties the truth-acquisition risk set and makes a primary metric unestimable
    (AMD-0002 §2.3). The first end-to-end smoke test caught exactly this bug.
    """
    res = _run(_spec())
    t = res.trajectory
    baseline = t.states[t.observed, 0]
    assert not (baseline == BeliefState.CAPITULATED).any()
    assert (baseline == BeliefState.DESTABILISED).any(), (
        "no agent started without the truth -- the truth-acquisition risk set would be empty"
    )


def test_isolated_arm_exchanges_no_messages():
    spec = _spec(topology=TopologySpec(kind=Topology.ISOLATED, n_agents=8), n_seeds=0)
    res = _run(spec)
    assert res.manifest["topology"]["n_edges"] == 0
    # Messages are generated but never delivered, so belief cannot move.
    assert np.array_equal(res.trajectory.states[:, 0], res.trajectory.states[:, -1])


def test_states_shape_matches_rounds():
    res = _run(_spec(n_rounds=4))
    assert res.trajectory.states.shape == (12, 5)
    assert res.trajectory.n_rounds == 4


def test_no_failures_means_one_message_per_agent_per_round():
    spec = _spec(n_rounds=3)
    res = _run(spec)
    assert res.failure_count == 0
    assert len(res.messages) == 12 * 3


def test_manifest_carries_full_provenance():
    """SOP-040 §5: a run is only real if it can be traced back to what produced it."""
    m = _run(_spec()).manifest
    for key in (
        "run_id", "config_hash", "prompt_template_hash", "fact_id", "cohort",
        "topology", "budget_convention", "seeds", "agent_assignment", "calls", "probes",
    ):
        assert key in m, f"manifest missing {key}"
    assert set(m["seeds"]) == {"topology", "assignment", "message_budget", "sampling"}
    assert len(m["agent_assignment"]) == 12


def test_probe_count_matches_two_claims_times_paraphrases():
    spec = _spec(n_rounds=2)
    res = _run(spec)
    # (T+1) probe rounds x N agents x 2 claims x M paraphrases
    assert res.manifest["probes"]["n"] == 3 * 12 * 2 * spec.probe.n_paraphrases


def test_failed_generations_never_enter_context():
    """SOP-040 §6. SPEC-2 v1.0 returned a placeholder string that would have been broadcast."""

    class AlwaysFails(StubBackend):
        def generate(self, **kw):  # type: ignore[override]
            from llm_society_sim.backends import Generation

            return Generation(text=None, error="simulated timeout")

    spec = _spec()
    backends = {
        m.model_id: AlwaysFails(s_false=FACT.s_false) for m in spec.cohort.members
    }
    res = SimulationEngine(spec, backends, FACT).run()

    assert res.messages == [], "a failed call must not produce a message"
    assert res.failure_count == 12 * spec.n_rounds
    assert res.trajectory.failure_count == res.failure_count
    # With no messages delivered, belief cannot move.
    assert np.array_equal(res.trajectory.states[:, 0], res.trajectory.states[:, -1])


def test_missing_backend_is_caught_at_construction():
    spec = _spec()
    with pytest.raises(KeyError, match="no backend supplied"):
        SimulationEngine(spec, {}, FACT)


def test_agent_assignment_covers_every_model():
    spec = _spec()
    res = _run(spec)
    used = {a["model_id"] for a in res.manifest["agent_assignment"]}
    assert used == {m.model_id for m in spec.cohort.members}


def test_assignment_seed_changes_who_sits_where():
    a = _run(_spec(seed_assignment=1)).manifest["agent_assignment"]
    b = _run(_spec(seed_assignment=2)).manifest["agent_assignment"]
    assert [x["model_id"] for x in a] != [x["model_id"] for x in b]


def test_seeding_density_is_reported_as_sigma():
    spec = _spec(n_seeds=3, topology=TopologySpec(kind=Topology.COMPLETE, n_agents=12))
    assert spec.seeding_density == pytest.approx(0.25)
