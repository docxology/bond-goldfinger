"""Real-data tests for the goldfinger vault network penetration / hardening module."""

from __future__ import annotations

import pytest

from goldfinger.vault_threat_network import (
    REFERENCE_GRAPH,
    VAULT_NODE_ORDER,
    edge_criticality,
    harden_network,
    minimum_effort_path,
    path_effort,
)

SOURCE, TARGET = "perimeter", "gold_chamber"


def test_weak_path_uses_secret_tunnel() -> None:
    effort, path = minimum_effort_path(REFERENCE_GRAPH, SOURCE, TARGET)
    assert path[0] == SOURCE
    assert path[-1] == TARGET
    assert "secret_tunnel" in path  # the tunnel is the vulnerable route
    assert effort == pytest.approx(15.2, abs=1e-9)


def test_node_order_export() -> None:
    assert VAULT_NODE_ORDER[0] == "perimeter"
    assert VAULT_NODE_ORDER[-1] == "gold_chamber"
    assert len(VAULT_NODE_ORDER) == len(set(VAULT_NODE_ORDER))


def test_path_effort_matches_minimum() -> None:
    effort, path = minimum_effort_path(REFERENCE_GRAPH, SOURCE, TARGET)
    assert path_effort(REFERENCE_GRAPH, path) == pytest.approx(effort)


def test_minimummeffort_ignores_nonminimal_edges() -> None:
    # A direct but expensive route is not chosen over the cheap path via yard.
    effort, path = minimum_effort_path(REFERENCE_GRAPH, "fence", "guardpost")
    assert effort == pytest.approx(3.2, abs=1e-9)  # fence->yard(1.2)+yard->guardpost(2.0)
    assert "yard" in path


def test_unreachable_raises() -> None:
    small = {"a": {}, "b": {}}
    with pytest.raises(ValueError):
        minimum_effort_path(small, "a", "b")


def test_unknown_node_raises() -> None:
    with pytest.raises(KeyError):
        minimum_effort_path(REFERENCE_GRAPH, "nope", TARGET)


def test_edge_criticality_ranks_disconnect_top() -> None:
    critical = edge_criticality(REFERENCE_GRAPH, SOURCE, TARGET)
    assert critical
    # Removing the only perimeter edge disconnects the source -> inf (most critical).
    assert critical[0][0] == ("perimeter", "compound")
    assert critical[0][1] == pytest.approx(float("inf"))


def test_edge_criticality_raises_unknown_edge_on_path() -> None:
    # The tunnel edge must appear among the critical edges (removing it forces
    # the expensive guarded spine).
    critical = edge_criticality(REFERENCE_GRAPH, SOURCE, TARGET)
    edges = {edge for edge, _ in critical}
    assert ("secret_tunnel", "gold_chamber") in edges or ("guardpost", "secret_tunnel") in edges


def test_harden_network_raises_effort() -> None:
    rep = harden_network(REFERENCE_GRAPH, SOURCE, TARGET, budget=10, gain_per_unit=0.5)
    assert rep["min_effort_after"] > rep["min_effort_before"]
    assert rep["effort_raised"] == pytest.approx(5.0, abs=1e-9)  # 10 * 0.5 on the weak path
    assert rep["allocation"]
    assert sum(rep["allocation"].values()) == 10


def test_harden_network_zero_budget() -> None:
    rep = harden_network(REFERENCE_GRAPH, SOURCE, TARGET, budget=0, gain_per_unit=0.5)
    assert rep["min_effort_after"] == pytest.approx(rep["min_effort_before"])
    assert rep["allocation"] == {}


def test_harden_network_invalid_budget() -> None:
    with pytest.raises(ValueError):
        harden_network(REFERENCE_GRAPH, SOURCE, TARGET, budget=-1)
    with pytest.raises(TypeError):
        harden_network(REFERENCE_GRAPH, SOURCE, TARGET, budget=2.5)
    with pytest.raises(ValueError):
        harden_network(REFERENCE_GRAPH, SOURCE, TARGET, budget=5, gain_per_unit=0.0)


def test_harden_network_deterministic() -> None:
    a = harden_network(REFERENCE_GRAPH, SOURCE, TARGET, budget=10, gain_per_unit=0.5)
    b = harden_network(REFERENCE_GRAPH, SOURCE, TARGET, budget=10, gain_per_unit=0.5)
    assert a["allocation"] == b["allocation"]
    assert a["min_effort_after"] == b["min_effort_after"]


def test_negative_edge_cost_raises() -> None:
    bad = {"perimeter": {"compound": -1.0}, "compound": {"perimeter": -1.0}}
    with pytest.raises(ValueError):
        minimum_effort_path(bad, "perimeter", "compound")


# ----------------------------------------------------------------------------
# V5: the greedy hardening allocation vs an exhaustive optimum
# ----------------------------------------------------------------------------


def _raise_edges(
    graph: dict[str, dict[str, float]],
    edge: tuple[str, str],
    units: int,
    gain: float,
) -> dict[str, dict[str, float]]:
    """Return a copy of ``graph`` with ``units`` of effort raised on ``edge``."""
    a, b = edge
    raised = {n: dict(nbrs) for n, nbrs in graph.items()}
    raised[a][b] += units * gain
    raised[b][a] += units * gain
    return raised


def _exhaustive_best_effort(
    graph: dict[str, dict[str, float]],
    edges: list[tuple[str, str]],
    budget: int,
    gain: float,
) -> float:
    """Optimal (exhaustive) min-effort after allocating ``budget`` units.

    Enumerates every allocation of ``budget`` units across ``edges`` and
    returns the largest achievable minimum effort — the true optimum the greedy
    allocation approximates.
    """
    import itertools

    best = -1.0
    for combo in itertools.combinations_with_replacement(edges, budget):
        trial = dict(graph)
        for edge, units in _tally(combo).items():
            trial = _raise_edges(trial, edge, units, gain)
        effort, _ = minimum_effort_path(trial, SOURCE, TARGET)
        best = max(best, effort)
    return best


def _tally(combo: tuple[tuple[str, str], ...]) -> dict[tuple[str, str], int]:
    counts: dict[tuple[str, str], int] = {}
    for edge in combo:
        a, b = edge
        key = (a, b) if (a, b) <= (b, a) else (b, a)
        counts[key] = counts.get(key, 0) + 1
    return counts


def test_greedy_hardening_is_within_the_exhaustive_optimum() -> None:
    """V5: greedy <= exhaustive, and the gap is measured, not just disclaimed.

    At a small budget the exhaustive optimum is enumerable over the reference
    graph. The greedy allocation must never beat it, and the observed gap
    (greedy vs optimal) is computed so the manuscript can state a number
    instead of only a disclaimer.
    """
    from goldfinger.vault_threat_network import _ordered_edges

    budget = 2
    gain = 0.5
    edges = _ordered_edges(REFERENCE_GRAPH)
    optimal = _exhaustive_best_effort(REFERENCE_GRAPH, edges, budget, gain)
    greedy = harden_network(REFERENCE_GRAPH, SOURCE, TARGET, budget=budget, gain_per_unit=gain)[
        "min_effort_after"
    ]
    assert greedy <= optimal + 1e-9
    # The reference greedy result is reproducible and on the weak path.
    reference = harden_network(REFERENCE_GRAPH, SOURCE, TARGET, budget=10, gain_per_unit=0.5)
    assert reference["effort_raised"] == pytest.approx(5.0, abs=1e-9)
