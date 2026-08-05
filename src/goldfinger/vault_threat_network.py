"""Vault security network — graph penetration and network hardening.

The vault-defense extension. The layered-score model in
:mod:`goldfinger.vault_security` assesses *strength ratings*; this module
treats the vault as an **undirected weighted graph** of defensive zones and
the *paths* the intruder could take to reach the gold. Each edge carries an
"intrusion effort" (time/risk to traverse). The model answers two questions
with real graph algorithms:

1. **Penetration** — what is the minimum-effort path from the outer perimeter
   to the gold chamber, and which edges are critical (removing/raising them
   most frustrates the intruder)?
2. **Hardening** — given a finite budget of hardening units, where should each
   unit go to *maximise* the minimum effort the intruder must pay
   (shortest-path network hardening)?

This is the classic shortest-path *interdiction / improvement* problem in
small scale: a greedy marginal-gain allocation that raises the intruder's
required effort edge by edge.

All algorithms are deterministic (plain Dijkstra, no heap-ordering ambiguity)
and infrastructure-free.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any, TypedDict

__all__ = [
    "REFERENCE_GRAPH",
    "REFERENCE_HARDENING",
    "REFERENCE_TARGET",
    "VAULT_NODE_ORDER",
    "edge_criticality",
    "harden_network",
    "minimum_effort_path",
    "path_effort",
]

#: Canonical ordering of defensive zones (also the deterministic tie-break
#: order for criticality and hardening).
VAULT_NODE_ORDER: tuple[str, ...] = (
    "perimeter",
    "compound",
    "fence",
    "yard",
    "guardpost",
    "secret_tunnel",
    "vault_exterior",
    "vault_door",
    "lock_room",
    "gold_chamber",
)

#: Undirected zone graph with intrusion-effort costs per edge. The gold
#: chamber is reachable two ways: the guarded spine (expensive) and the
#: secret tunnel (cheap) — the tunnel is the vault's weak point.
REFERENCE_GRAPH: dict[str, dict[str, float]] = {
    "perimeter": {"compound": 2.0},
    "compound": {"perimeter": 2.0, "fence": 1.5, "yard": 3.5},
    "fence": {"compound": 1.5, "yard": 1.2, "guardpost": 4.0},
    "yard": {"compound": 3.5, "fence": 1.2, "guardpost": 2.0},
    "guardpost": {"fence": 4.0, "yard": 2.0, "vault_exterior": 3.0, "secret_tunnel": 6.0},
    "secret_tunnel": {"guardpost": 6.0, "gold_chamber": 2.5},
    "vault_exterior": {"guardpost": 3.0, "vault_door": 4.0},
    "vault_door": {"vault_exterior": 4.0, "lock_room": 5.0},
    "lock_room": {"vault_door": 5.0, "gold_chamber": 6.0},
    "gold_chamber": {"lock_room": 6.0, "secret_tunnel": 2.5},
}

#: The reference intrusion problem: from the outer perimeter to the gold.
REFERENCE_TARGET: tuple[str, str] = ("perimeter", "gold_chamber")


class _HardeningIntel(TypedDict):
    """Typed shape of the reference hardening posture."""

    budget: int
    gain_per_unit: float


#: Reference hardening posture — the defensive budget and the effort each unit
#: buys. Single source of truth for the mission adapter, the manuscript token
#: map, and the figures, so the three cannot report different postures.
REFERENCE_HARDENING: _HardeningIntel = {
    "budget": 10,
    "gain_per_unit": 0.5,
}


def _require_node(graph: Mapping[str, Mapping[str, float]], node: str) -> None:
    if node not in graph:
        raise KeyError(f"unknown vault zone {node!r}")


def _require_edge_cost(cost: float, label: str) -> float:
    if isinstance(cost, bool) or not isinstance(cost, (int, float)):
        raise TypeError(f"{label} must be a number")
    if cost < 0:
        raise ValueError(f"{label} must be non-negative")
    return float(cost)


def _node_key(node: str) -> tuple[int, str]:
    """Deterministic sort key: canonical order first, then lexicographic."""
    known = node in VAULT_NODE_ORDER
    return (VAULT_NODE_ORDER.index(node) if known else len(VAULT_NODE_ORDER), node)


def _ordered_nodes(graph: Mapping[str, Mapping[str, float]]) -> list[str]:
    """Graph nodes in deterministic traversal order."""
    return sorted(graph.keys(), key=_node_key)


def _neighbors_in_order(graph: Mapping[str, Mapping[str, float]], node: str) -> list[str]:
    return sorted(graph[node].keys(), key=_node_key)


def minimum_effort_path(
    graph: Mapping[str, Mapping[str, float]],
    source: str,
    target: str,
) -> tuple[float, tuple[str, ...]]:
    """Dijkstra shortest-path intrusion effort from ``source`` to ``target``.

    Returns ``(min_effort, path)``. Raises ``ValueError`` if ``target`` is
    unreachable from ``source``.
    """
    _require_node(graph, source)
    _require_node(graph, target)
    nodes = _ordered_nodes(graph)
    dist: dict[str, float] = {n: math.inf for n in nodes}
    prev: dict[str, str | None] = {n: None for n in nodes}
    dist[source] = 0.0
    settled: set[str] = set()
    for _ in range(len(nodes)):
        # Pick the unsettled node with the smallest tentative distance,
        # tie-broken by canonical order (deterministic).
        candidates = [n for n in nodes if n not in settled and dist[n] < math.inf]
        if not candidates:
            break
        u = min(candidates, key=lambda n: (dist[n], _node_key(n)))
        settled.add(u)
        for v in _neighbors_in_order(graph, u):
            cost = _require_edge_cost(graph[u][v], f"graph[{u!r}][{v!r}]")
            tentative = dist[u] + cost
            if tentative < dist[v]:
                dist[v] = tentative
                prev[v] = u
    if dist[target] == math.inf:
        raise ValueError(f"target zone {target!r} is unreachable from {source!r}")
    path: list[str] = []
    cur: str | None = target
    while cur is not None:
        path.append(cur)
        cur = prev[cur]
    path.reverse()
    return float(dist[target]), tuple(path)


def path_effort(graph: Mapping[str, Mapping[str, float]], path: tuple[str, ...]) -> float:
    """Sum of intrusion-effort costs along a (valid) path."""
    if not path:
        raise ValueError("path must not be empty")
    total = 0.0
    for a, b in zip(path, path[1:], strict=False):
        if b not in graph[a]:
            raise ValueError(f"no edge from {a!r} to {b!r} in the graph")
        total += _require_edge_cost(graph[a][b], f"graph[{a!r}][{b!r}]")
    return float(total)


def edge_criticality(
    graph: Mapping[str, Mapping[str, float]],
    source: str,
    target: str,
) -> tuple[tuple[tuple[str, str], float], ...]:
    """Rank edges by how much removing each raises the minimum intrusion effort.

    Returns ``((edge_a, edge_b), min_effort_with_edge_removed)`` sorted
    descending by the resulting effort. Edges whose removal leaves the target
    unreachable report ``math.inf`` (the most critical).
    """
    base_effort, path = minimum_effort_path(graph, source, target)
    critical: list[tuple[tuple[str, str], float]] = []
    for a, b in zip(path, path[1:], strict=False):
        cut = {node: dict(neighbors) for node, neighbors in graph.items()}
        cut[a].pop(b, None)
        cut[b].pop(a, None)
        try:
            effort, _ = minimum_effort_path(cut, source, target)
        except ValueError:
            effort = math.inf
        if effort > base_effort:
            critical.append(((a, b), effort))
    critical.sort(key=lambda item: item[1], reverse=True)
    return tuple(critical)


def harden_network(
    graph: Mapping[str, Mapping[str, float]],
    source: str,
    target: str,
    budget: int,
    gain_per_unit: float = 0.5,
) -> dict[str, Any]:
    """Greedily allocate ``budget`` hardening units to maximise the minimum
    intrusion effort.

    Each unit raises one edge's cost by ``gain_per_unit``; at every step the
    edge whose raise most increases the current shortest-path effort is chosen
    (ties broken by canonical node order). Returns a report dict with the
    allocation, the raised graph (as plain nested dicts), and the final minimum
    effort before/after.
    """
    if isinstance(budget, bool) or not isinstance(budget, int):
        raise TypeError("budget must be an int")
    if budget < 0:
        raise ValueError("budget must be non-negative")
    if (
        isinstance(gain_per_unit, bool)
        or not isinstance(gain_per_unit, (int, float))
        or gain_per_unit <= 0
    ):
        raise ValueError("gain_per_unit must be a positive number")

    raised: dict[str, dict[str, float]] = {node: dict(graph[node]) for node in graph}
    before, _ = minimum_effort_path(raised, source, target)
    allocation: dict[tuple[str, str], int] = {}
    for _ in range(budget):
        best: tuple[str, str] | None = None
        best_effort = -1.0
        for a, b in _ordered_edges(raised):
            trial = {n: dict(raised[n]) for n in raised}
            trial[a][b] = _require_edge_cost(raised[a][b], "cost") + gain_per_unit
            trial[b][a] = _require_edge_cost(raised[b][a], "cost") + gain_per_unit
            # Raising an edge cost never changes the topology, so ``target``
            # stays reachable and ``minimum_effort_path`` cannot raise here —
            # the reachability invariant was established by ``before`` above.
            effort, _ = minimum_effort_path(trial, source, target)
            if effort > best_effort:
                best_effort = effort
                best = (a, b)
        if best is None:
            break  # edgeless graph (e.g. source == target): nothing to harden
        a, b = best
        raised[a][b] = _require_edge_cost(raised[a][b], "cost") + gain_per_unit
        raised[b][a] = _require_edge_cost(raised[b][a], "cost") + gain_per_unit
        allocation[best] = allocation.get(best, 0) + 1

    after, _ = minimum_effort_path(raised, source, target)
    return {
        "budget": budget,
        "gain_per_unit": gain_per_unit,
        "min_effort_before": before,
        "min_effort_after": after,
        "effort_raised": after - before,
        "allocation": {f"{a}->{b}": units for (a, b), units in allocation.items()},
        "graph": raised,
    }


def _ordered_edges(graph: Mapping[str, Mapping[str, float]]) -> list[tuple[str, str]]:
    """All undirected edges in deterministic canonical order."""
    seen: set[tuple[str, str]] = set()
    edges: list[tuple[str, str]] = []
    for a in _ordered_nodes(graph):
        key_a = _node_key(a)
        for b in sorted(graph[a].keys(), key=_node_key):
            key = (a, b) if (key_a, _node_key(b)) <= (_node_key(b), key_a) else (b, a)
            if key not in seen:
                seen.add(key)
                edges.append(key)
    return edges
