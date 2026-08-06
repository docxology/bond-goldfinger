"""goldfinger — special-agent mission software (film: Goldfinger, 1964).

Mission codename: **GRAND SLAM**.

The package models the operational concepts behind the mission across three
domains, each with a pure (no-I/O), deterministic, infrastructure-free core:

* :mod:`goldfinger.market_attack` — Operation Grand Slam gold-market cornering
  model (supply shock → price dynamics) via constant-elasticity inverse demand
  and tatonnement adjustment.
* :mod:`goldfinger.reserve_attack` — the macroeconomic extension: a
  first-generation speculative attack on a gold peg (Flood–Garber) that turns
  gold accumulation into a monetary-system weapon.
* :mod:`goldfinger.vault_security` — Fort Knox-style layered defense
  assessment (defense-in-depth scoring and sequential penetration probability).
* :mod:`goldfinger.vault_threat_network` — the network-defense extension:
  shortest-path vault penetration and greedy network hardening over a zone graph.
* :mod:`goldfinger.laser_physics` — laser threat physics (burn-through time vs
  material and power) via an energy-balance thermal model.
* :mod:`goldfinger.laser_thermal` — the spatio-temporal extension: Gaussian
  beam focusing, Carslaw–Jaeger heat conduction, and the effective burn range.

The mission adapter (:mod:`goldfinger.mission`) implements the frozen BOND-API
``MissionProvider`` protocol and is the only module that imports bond-api; the
six concept modules above are importable without it.
"""

from __future__ import annotations

from goldfinger.laser_physics import (
    burn_through_time,
    laser_threat_severity,
    max_burn_thickness,
    power_for_burn_through,
)
from goldfinger.laser_thermal import (
    REFERENCE_BEAM,
    BurnRangeResult,
    effective_burn_range,
    melt_time_at_distance,
    power_density,
    rayleigh_range,
    spot_radius_at_distance,
    surface_melt_time,
    thermal_surface_temperature,
)
from goldfinger.market_attack import (
    CONVERGENCE_TOLERANCE,
    CornerResult,
    convergence_residual,
    corner_valuation,
    effective_supply,
    has_converged,
    price_gain,
    shocked_equilibrium_price,
    simulate_corner,
)
from goldfinger.reserve_attack import (
    REFERENCE_ATTACK,
    attack_time,
    domestic_credit,
    floating_depreciation,
    reserve_floor_time,
    reserve_level,
    shadow_rate,
    simulate_reserve_crisis,
    surface_money,
)
from goldfinger.vault_security import (
    DEFAULT_LAYERS,
    expected_breach_time,
    layered_security_score,
    marginal_improvements,
    penetration_probability,
    vault_security_verdict,
    weakest_layer,
)
from goldfinger.vault_threat_network import (
    REFERENCE_GRAPH,
    VAULT_NODE_ORDER,
    edge_criticality,
    harden_network,
    minimum_effort_path,
    path_effort,
)

__version__ = "0.2.0"

#: Mission identity for this film package (single source of truth).
FILM = "goldfinger"
CODENAME = "GRAND SLAM"

#: Deterministic mission seed recorded in provenance. The mission performs no
#: random draws; the seed is declared so replays are auditable.
MISSION_SEED = 2026

#: Power threshold (W) above which a laser is classified a *serious* threat by
#: :func:`goldfinger.laser_physics.laser_threat_severity`. Shared by the
#: mission adapter and the manuscript token map so the two cannot disagree.
LASER_SEVERITY_THRESHOLD_W = 1000.0

#: Effective burn range (m) at or above which the thermal engagement is
#: classified a standoff ("serious") laser threat rather than short-range.
LASER_STANDOFF_RANGE_M = 25.0

__all__ = [
    "CODENAME",
    "CONVERGENCE_TOLERANCE",
    "CornerResult",
    "DEFAULT_LAYERS",
    "FILM",
    "LASER_SEVERITY_THRESHOLD_W",
    "LASER_STANDOFF_RANGE_M",
    "MISSION_SEED",
    "REFERENCE_ATTACK",
    "REFERENCE_BEAM",
    "REFERENCE_GRAPH",
    "BurnRangeResult",
    "VAULT_NODE_ORDER",
    "__version__",
    "attack_time",
    "burn_through_time",
    "convergence_residual",
    "corner_valuation",
    "domestic_credit",
    "edge_criticality",
    "effective_burn_range",
    "effective_supply",
    "expected_breach_time",
    "floating_depreciation",
    "harden_network",
    "has_converged",
    "laser_threat_severity",
    "layered_security_score",
    "marginal_improvements",
    "max_burn_thickness",
    "melt_time_at_distance",
    "minimum_effort_path",
    "path_effort",
    "penetration_probability",
    "power_density",
    "power_for_burn_through",
    "price_gain",
    "rayleigh_range",
    "reserve_floor_time",
    "reserve_level",
    "shadow_rate",
    "shocked_equilibrium_price",
    "simulate_corner",
    "simulate_reserve_crisis",
    "spot_radius_at_distance",
    "surface_melt_time",
    "surface_money",
    "thermal_surface_temperature",
    "vault_security_verdict",
    "weakest_layer",
]
