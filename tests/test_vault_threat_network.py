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
