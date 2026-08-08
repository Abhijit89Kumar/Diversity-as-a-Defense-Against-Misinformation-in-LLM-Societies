"""Command-line entry point.

Console output is deliberately ASCII-only: Windows consoles default to cp1252, and a
public repository should not crash on its own demo command.

    python -m llm_society_sim.cli demo          # stub run, no GPU, no keys
    python -m llm_society_sim.cli ladder        # inspect the configured cohorts
    python -m llm_society_sim.cli sweep --runs 30

`demo` and `sweep` use the deterministic stub backend and therefore need **no GPU and no API
key** (`DR-0009`). They exercise the whole pipeline - engine, metrics, survival analysis - so
that anyone cloning the repository can verify it works before compute exists.

**Stub output is not evidence about language models.** It is a property of the threshold rule
in `backends.StubBackend`. Real results require `EXP-000` and the confirmatory matrix.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

from . import metrics
from .analysis.survival import capitulation_data, fit_discrete_hazard, truth_acquisition_data
from .backends import StubBackend
from .config import AgentSpec, CohortSpec, RunSpec, Topology, TopologySpec
from .engine import SimulationEngine
from .prompts import FactPrompt

REPO = Path(__file__).resolve().parents[2]


# ------------------------------------------------------------------------------- helpers


def load_facts(path: Path | None = None) -> list[FactPrompt]:
    path = path or REPO / "docs" / "03-design" / "fact-suite" / "candidates.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    return [
        FactPrompt(
            fact_id=i["id"], s_true=i["s_true"], s_false=i["s_false"],
            authority_frame=i["authority_frame"],
        )
        for i in data["items"]
    ]


def load_cohorts(path: Path | None = None) -> list[CohortSpec]:
    path = path or REPO / "configs" / "ladder.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    return [CohortSpec(**c) for c in data["cohorts"]]


def _stub_cohort(level: str, h: float) -> CohortSpec:
    """A stub-backed cohort standing in for a real one, for demo/sweep only."""
    if level in ("D0", "D1", "D2"):
        members = [AgentSpec(model_id="stub-a", temperature=0.0 if level == "D0" else 0.7)]
        personas = ["analyst", "sceptic"] if level == "D2" else ["analyst"]
    else:
        members = [AgentSpec(model_id=f"stub-{c}", temperature=0.7) for c in "abcd"]
        personas = ["analyst", "sceptic"] if level == "D4" else ["analyst"]
    return CohortSpec(
        name=f"{level}-stub", level=level, members=members, personas=personas,
        measured_accuracy=0.62, measured_diversity=h,
    )


def _run_one(cohort: CohortSpec, fact: FactPrompt, *, run_id: str, seed: int, topology: Topology):
    spec = RunSpec(
        run_id=run_id, cohort=cohort,
        topology=TopologySpec(kind=topology, n_agents=20),
        fact_id=fact.fact_id, n_rounds=5, n_seeds=2, receiver_budget=4,
        seed_topology=seed, seed_assignment=seed,
        seed_message_budget=seed, seed_sampling=seed,
    )
    # Stub protectiveness scales with the cohort's nominal diversity, purely so the demo has
    # something to recover. This is scaffolding, not a hypothesis.
    threshold = 0.30 + 0.30 * (cohort.measured_diversity or 0.0)
    backends = {
        m.model_id: StubBackend(s_false=fact.s_false, threshold=threshold, base_accuracy=0.65)
        for m in cohort.members
    }
    return SimulationEngine(spec, backends, fact).run()


# ------------------------------------------------------------------------------ commands


def cmd_ladder(args: argparse.Namespace) -> int:
    print(f"{'cohort':<20}{'level':<7}{'models':<8}{'personas':<10}{'a_bar':<8}{'H(c)':<8}")
    print("-" * 61)
    for c in load_cohorts(args.config):
        acc = "-" if c.measured_accuracy is None else f"{c.measured_accuracy:.3f}"
        div = "-" if c.measured_diversity is None else f"{c.measured_diversity:.3f}"
        print(f"{c.name:<20}{c.level:<7}{len(c.members):<8}{len(c.personas):<10}{acc:<8}{div:<8}")
    print(
        "\na_bar and H(c) are unmeasured until EXP-000. Confirmatory runs must refuse to start\n"
        "without them - a cohort whose capability is asserted rather than measured is the\n"
        "exact flaw this project criticises in prior work."
    )
    return 0


def cmd_demo(args: argparse.Namespace) -> int:
    fact = load_facts()[16]  # F-017, the 206-bones item
    cohort = _stub_cohort("D3", 0.8)
    res = _run_one(cohort, fact, run_id="demo", seed=7, topology=Topology.WATTS_STROGATZ)
    t = res.trajectory

    print(f"fact   : {fact.fact_id} - {fact.s_true}")
    print(f"inject : {fact.s_false}")
    print(f"cohort : {cohort.name}  |  topology: watts_strogatz  |  N=20, T=5, seeds=2\n")

    f = metrics.state_fractions(t)
    print(f"{'round':<8}{'holds':>9}{'capitulated':>14}{'destabilised':>15}")
    for r in range(t.states.shape[1]):
        print(f"{r:<8}{f['trr'][r]:>9.2f}{f['mp'][r]:>14.2f}{f['ds'][r]:>15.2f}")

    s = metrics.run_level_summary(t)
    print(
        f"\ncascade size {s['cascade_size']:.2f} | onset {s['cascade_onset']:.0f} | "
        f"peak velocity {s['peak_velocity']:.2f} | assortativity {s['state_assortativity']:.3f}"
    )
    print(
        f"calls {res.manifest['calls']['n']} | probes {res.manifest['probes']['n']} | "
        f"failures {res.failure_count} | unparseable "
        f"{100 * res.manifest['probes']['unparseable_rate']:.1f}%"
    )
    print(f"config {res.manifest['config_hash'][:12]} | templates {res.manifest['prompt_template_hash'][:12]}")
    print("\nStub backend - this is plumbing, not evidence about language models.")
    return 0


def cmd_sweep(args: argparse.Namespace) -> int:
    facts = load_facts()
    ladder = [("D0", 0.0), ("D1", 0.35), ("D3", 0.8)]
    trajectories = []
    for i in range(args.runs):
        level, h = ladder[i % len(ladder)]
        fact = facts[i % len(facts)]
        res = _run_one(
            _stub_cohort(level, h), fact,
            run_id=f"sweep-{i:04d}", seed=i, topology=Topology.WATTS_STROGATZ,
        )
        trajectories.append(res.trajectory)

    cap = capitulation_data(trajectories)
    tru = truth_acquisition_data(trajectories)
    print(f"runs {len(trajectories)}")
    print(f"  capitulation risk set : {len(cap):>5} agent-rounds, {int(cap.event.sum()):>4} events")
    print(f"  truth-acquisition set : {len(tru):>5} agent-rounds, {int(tru.event.sum()):>4} events")

    for level, _ in ladder:
        sizes = [metrics.cascade_size(t) for t in trajectories if t.condition == level]
        print(f"  mean cascade size {level}: {np.mean(sizes):.3f}  (n={len(sizes)})")

    if cap["event"].sum() > 10 and cap["h_cohort"].nunique() > 1:
        fit = fit_discrete_hazard(cap, ["h_cohort"])
        hr, lo, hi = fit.hazard_ratio("h_cohort")
        print(f"\nH1 estimate (stub data): HR {hr:.3f}  95% CI [{lo:.3f}, {hi:.3f}]")
        print("A protective effect is planted in the stub by construction, so recovering it")
        print("demonstrates the pipeline works - it says nothing about real models.")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="llm-society-sim", description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("ladder", help="show the configured diversity ladder")
    p.add_argument("--config", type=Path, default=None)
    p.set_defaults(func=cmd_ladder)

    p = sub.add_parser("demo", help="one stub run, end to end")
    p.set_defaults(func=cmd_demo)

    p = sub.add_parser("sweep", help="many stub runs, then fit the primary model")
    p.add_argument("--runs", type=int, default=30)
    p.set_defaults(func=cmd_sweep)

    args = ap.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
