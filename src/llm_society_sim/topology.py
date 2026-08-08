"""Communication graphs and the message-budget convention.

Implements AMD-0002 §7 and the topology factor in AMD-0001.

> **Ownership note.** This module is proposed as the co-researcher's to own and extend
> (briefing §8.2). What is here is the minimum the engine needs to run end-to-end. Two
> substantial pieces are deliberately left unimplemented and marked below: **density
> matching** across topologies (OQ-0028) and the **classical contagion baseline** (OQ-0024).
> Both are self-contained, need no GPU, and are the interesting part.
"""

from __future__ import annotations

import networkx as nx
import numpy as np

from .config import BudgetConvention, Topology, TopologySpec

__all__ = [
    "build_graph",
    "adjacency_matrix",
    "in_neighbours",
    "sample_incoming",
    "graph_summary",
]


def build_graph(spec: TopologySpec, seed: int) -> nx.DiGraph:
    """Build the communication graph.

    Edge direction is **information flow**: an edge j -> i means i receives from j. Every
    undirected construction is symmetrised, so an undirected tie is mutual communication.

    The seed is explicit rather than module-global: topology realisation is one of four
    independent randomisations (SOP-030 §4), and SPEC-2 v1.0 hard-coded `seed=42`, which
    meant topology variance was never sampled at all — a real problem for a hypothesis
    entirely about topology.
    """
    n = spec.n_agents

    if spec.kind is Topology.ISOLATED:
        g = nx.DiGraph()
        g.add_nodes_from(range(n))

    elif spec.kind is Topology.COMPLETE:
        g = nx.complete_graph(n, create_using=nx.DiGraph)

    elif spec.kind is Topology.ERDOS_RENYI:
        # Undirected then symmetrised: a tie means mutual communication, which keeps the
        # comparison with Watts-Strogatz (inherently undirected) like-for-like.
        u = nx.erdos_renyi_graph(n, spec.er_p, seed=seed)
        g = u.to_directed()

    elif spec.kind is Topology.WATTS_STROGATZ:
        u = nx.watts_strogatz_graph(n, spec.ws_k, spec.ws_p, seed=seed)
        g = u.to_directed()

    else:  # pragma: no cover - StrEnum is exhaustive
        raise ValueError(f"unknown topology: {spec.kind}")

    g.graph["kind"] = str(spec.kind)
    g.graph["seed"] = seed
    g.remove_edges_from(nx.selfloop_edges(g))
    return g


def adjacency_matrix(g: nx.DiGraph, n: int) -> np.ndarray:
    """Dense (n, n) adjacency where `a[i, j] != 0` means i receives from j.

    NetworkX's convention is `a[u, v] != 0` for edge u -> v (u sends to v), so this is its
    transpose. Getting that backwards would silently invert every topology result, so it is
    done once, here, and tested.
    """
    a = nx.to_numpy_array(g, nodelist=range(n), dtype=float)
    return a.T


def in_neighbours(g: nx.DiGraph, node: int) -> list[int]:
    """Agents that `node` can receive from, in deterministic order."""
    return sorted(g.predecessors(node))


def sample_incoming(
    g: nx.DiGraph,
    node: int,
    convention: BudgetConvention,
    receiver_budget: int,
    rng: np.random.Generator,
) -> list[int]:
    """Which neighbours' messages this agent actually reads this round (AMD-0002 §7).

    `PER_RECEIVER` (primary) — at most `receiver_budget` messages, sampled uniformly without
    replacement when in-degree exceeds it. This holds *exposure volume* constant so topology
    varies **who** you hear from rather than **how much**, which is the only way to separate
    structure from volume. It also stops the bounded-memory operator truncating
    complete-graph agents far harder than sparse-graph ones, which would make "topology
    effect" partly "truncation effect".

    The honest cost, which belongs in the paper rather than in a reviewer's question: under
    this convention a complete graph becomes "hear k uniformly-sampled peers per round", not
    "hear everyone".

    `PER_EDGE` (sensitivity) — read every in-neighbour. Message volume then scales with
    degree, and Niu et al. show the sign of the topology effect can flip between the two.
    """
    nbrs = in_neighbours(g, node)
    if convention is BudgetConvention.PER_EDGE or len(nbrs) <= receiver_budget:
        return nbrs
    idx = rng.choice(len(nbrs), size=receiver_budget, replace=False)
    return [nbrs[i] for i in sorted(idx)]


def graph_summary(g: nx.DiGraph) -> dict[str, float]:
    """Structural descriptives, logged per run so topology claims are checkable.

    Reported in the paper alongside the topology label — "Watts-Strogatz" is a recipe, not a
    measurement, and two realisations from the same recipe can differ materially at N=20.
    """
    n = g.number_of_nodes()
    m = g.number_of_edges()
    in_deg = np.array([d for _, d in g.in_degree()], dtype=float)
    undirected = g.to_undirected()

    summary: dict[str, float] = {
        "n_nodes": float(n),
        "n_edges": float(m),
        "density": float(nx.density(g)) if n > 1 else 0.0,
        "mean_in_degree": float(in_deg.mean()) if n else 0.0,
        "min_in_degree": float(in_deg.min()) if n else 0.0,
        "max_in_degree": float(in_deg.max()) if n else 0.0,
        "clustering": float(nx.average_clustering(undirected)) if m else 0.0,
    }
    if m and nx.is_connected(undirected):
        summary["avg_shortest_path"] = float(nx.average_shortest_path_length(undirected))
        summary["n_components"] = 1.0
    else:
        summary["avg_shortest_path"] = float("nan")
        summary["n_components"] = float(nx.number_connected_components(undirected)) if n else 0.0
    return summary


# ---------------------------------------------------------------------------------------
# NOT IMPLEMENTED — owned by the co-researcher (briefing §8.2). Both are self-contained,
# GPU-free, and are the parts with real research content.
#
# 1. density_matched_spec(kind, target_density, n) -> TopologySpec        [OQ-0028]
#    Choose generator parameters so that complete / ER / WS realisations share an edge count.
#    Li et al. (arXiv:2410.13909) held density at 0.08 ± 0.002 across three topologies for
#    exactly this reason; our current spec does not, so any comparison involving the complete
#    graph is confounded with connectivity. Note the ER-vs-WS contrast — which is what H2
#    actually claims — is already density-matched, so the problem is confined to the complete
#    graph and one honest option is to treat it as a labelled reference condition instead.
#
# 2. Classical contagion baselines on the same graphs                     [OQ-0024]
#    SIR / SIS, a Granovetter threshold model, and a bounded-confidence (Deffuant or
#    Hegselmann-Krause) model, run on identical graphs with identical seeding, so the paper
#    can show *where* LLM dynamics diverge from classical contagion rather than asserting
#    that they do. This is very likely its own results section and it directly substantiates
#    the central claim about why LLM societies need studying separately.
# ---------------------------------------------------------------------------------------
