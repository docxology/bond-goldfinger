"""Gates on the reference intel itself: the YAML mirror and cross-model steel.

Two claims used to be made in prose and enforced nowhere:

1. ``manuscript/config.yaml``'s ``grand_slam:`` block "mirrors" the module
   ``REFERENCE_*`` constants. Nothing read the block, so the two could drift
   silently — and a reader who trusted the YAML would read wrong intel.
2. The two laser models describe "the same" reference steel plate. They did
   not: one used ``c = 500 J/(kg K)`` with ``dT = 1500 K``, the other
   ``c = 460 J/(kg K)`` with a 1200 K rise.

Both are now enforced here, key for key and value for value. Each assertion
fails if either side is edited alone; ``test_the_mirror_gate_can_actually_fail``
and ``test_the_steel_agreement_gate_can_actually_fail`` are the positive
controls that demonstrate it rather than assert it.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

from goldfinger.laser_physics import REFERENCE_PHYSICS
from goldfinger.laser_thermal import REFERENCE_BEAM
from goldfinger.manuscript_variables import load_mission_config
from goldfinger.market_attack import REFERENCE_MODEL
from goldfinger.reserve_attack import REFERENCE_ATTACK
from goldfinger.vault_security import REFERENCE_RATINGS
from goldfinger.vault_threat_network import (
    REFERENCE_GRAPH,
    REFERENCE_HARDENING,
    REFERENCE_TARGET,
)

_PKG_ROOT = Path(__file__).resolve().parents[1]


def _grand_slam() -> dict[str, Any]:
    block = load_mission_config(_PKG_ROOT).get("grand_slam")
    assert isinstance(block, dict), "manuscript/config.yaml must carry a grand_slam: mapping"
    return block


def _undirected_edges(graph: dict[str, dict[str, float]]) -> dict[frozenset[str], float]:
    """Collapse the adjacency map to one entry per undirected edge."""
    edges: dict[frozenset[str], float] = {}
    for node, neighbours in graph.items():
        for other, cost in neighbours.items():
            key = frozenset({node, other})
            if key in edges:
                assert edges[key] == cost, f"asymmetric edge cost for {sorted(key)}"
            edges[key] = cost
    return edges


def _mirror_edges(raw: dict[str, float]) -> dict[frozenset[str], float]:
    """Parse the YAML ``a-b: cost`` edge table into undirected edge keys."""
    edges: dict[frozenset[str], float] = {}
    for label, cost in raw.items():
        left, _, right = label.partition("-")
        assert right, f"edge key {label!r} must be 'zone_a-zone_b'"
        edges[frozenset({left, right})] = cost
    return edges


# --------------------------------------------------------------------------
# The config.yaml mirror is real and enforced
# --------------------------------------------------------------------------


def test_mirror_declares_exactly_the_reference_constants_it_claims() -> None:
    """A new REFERENCE_* constant cannot be added without mirroring it."""
    assert set(_grand_slam()) == {
        "market",
        "vault",
        "laser",
        "reserve_attack",
        "laser_beam",
        "vault_network",
    }


@pytest.mark.parametrize(
    ("block", "constant"),
    [
        ("market", REFERENCE_MODEL),
        ("vault", REFERENCE_RATINGS),
        ("laser", REFERENCE_PHYSICS),
        ("reserve_attack", REFERENCE_ATTACK),
        ("laser_beam", REFERENCE_BEAM),
    ],
)
def test_flat_mirror_blocks_equal_their_module_constant(
    block: str, constant: dict[str, float]
) -> None:
    mirrored = _grand_slam()[block]
    assert set(mirrored) == set(constant), f"grand_slam.{block} key set drifted"
    for key, value in constant.items():
        assert mirrored[key] == value, (
            f"grand_slam.{block}.{key} is {mirrored[key]}, code says {value}"
        )


def test_vault_network_mirror_equals_the_graph_and_posture() -> None:
    mirrored = _grand_slam()["vault_network"]
    assert set(mirrored) == {"source", "target", "budget", "gain_per_unit", "edges"}
    assert (mirrored["source"], mirrored["target"]) == REFERENCE_TARGET
    assert mirrored["budget"] == REFERENCE_HARDENING["budget"]
    assert mirrored["gain_per_unit"] == REFERENCE_HARDENING["gain_per_unit"]
    assert _mirror_edges(mirrored["edges"]) == _undirected_edges(REFERENCE_GRAPH)


def test_the_mirror_gate_can_actually_fail() -> None:
    """Positive control: a one-value edit to the YAML side is caught.

    Loads the committed YAML, perturbs a single number in memory, and shows the
    same comparison the gate performs now fails.
    """
    perturbed = yaml.safe_load(
        (_PKG_ROOT / "manuscript" / "config.yaml").read_text(encoding="utf-8")
    )
    perturbed["grand_slam"]["market"]["reference_price"] = 9999.0
    assert perturbed["grand_slam"]["market"] != dict(REFERENCE_MODEL)
    perturbed["grand_slam"]["vault_network"]["edges"]["secret_tunnel-gold_chamber"] = 99.0
    assert _mirror_edges(perturbed["grand_slam"]["vault_network"]["edges"]) != _undirected_edges(
        REFERENCE_GRAPH
    )


def test_every_yaml_file_under_manuscript_parses() -> None:
    """Any YAML shipped in ``manuscript/`` must actually load.

    ``config.yaml.example`` used to sit here advertised as a "reference copy of
    the configurable surface" while raising ``ScannerError`` on load. It was
    deleted; this gate stops the class from coming back.
    """
    candidates = sorted(
        path
        for path in (_PKG_ROOT / "manuscript").iterdir()
        if path.suffix in {".yaml", ".yml"} or path.name.endswith((".yaml.example", ".yml.example"))
    )
    assert candidates, "expected at least manuscript/config.yaml"
    for path in candidates:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert isinstance(loaded, dict), f"{path.name} must load as a YAML mapping"


# --------------------------------------------------------------------------
# The two laser models describe one plate
# --------------------------------------------------------------------------


def test_the_two_laser_models_use_the_same_steel() -> None:
    """Scalar burn-through and thermal engagement share the reference plate."""
    assert REFERENCE_PHYSICS["density"] == REFERENCE_BEAM["density"]
    assert REFERENCE_PHYSICS["specific_heat"] == REFERENCE_BEAM["specific_heat"]
    assert REFERENCE_PHYSICS["absorptivity"] == REFERENCE_BEAM["absorptivity"]
    assert REFERENCE_PHYSICS["power"] == REFERENCE_BEAM["power"]


def test_the_scalar_temperature_rise_is_the_thermal_models_melt_span() -> None:
    """``delta_temperature`` is exactly ``melt_temp - ambient``, not a free number."""
    span = REFERENCE_BEAM["melt_temp"] - REFERENCE_BEAM["ambient"]
    assert REFERENCE_PHYSICS["delta_temperature"] == span


def test_the_steel_agreement_gate_can_actually_fail() -> None:
    """Positive control: the pre-remediation constants would be rejected."""
    historical_physics = dict(REFERENCE_PHYSICS)
    historical_physics["specific_heat"] = 500.0
    historical_physics["delta_temperature"] = 1500.0
    assert historical_physics["specific_heat"] != REFERENCE_BEAM["specific_heat"]
    assert (
        historical_physics["delta_temperature"]
        != REFERENCE_BEAM["melt_temp"] - REFERENCE_BEAM["ambient"]
    )
