"""goldfinger — special-agent mission software (film: Goldfinger, 1964).

Mission codename: **GRAND SLAM**.

The package models the three operational concepts behind the mission:

* :mod:`goldfinger.market_attack` — Operation Grand Slam gold-market cornering
  model (supply shock → price dynamics) via constant-elasticity inverse demand
  and tatonnement adjustment.
* :mod:`goldfinger.vault_security` — Fort Knox-style vault defense assessment
  (layered defense-in-depth scoring and sequential penetration probability).
* :mod:`goldfinger.laser_physics` — laser threat physics (burn-through time
  vs material and power) via an energy-balance thermal model.

The three concept modules are *pure* (no I/O), deterministic, and importable
with only NumPy/standards — they do **not** depend on bond-api. The mission
adapter (:mod:`goldfinger.mission`) implements the frozen BOND-API
``MissionProvider`` protocol and is the only module that imports bond-api.
"""

from __future__ import annotations

from goldfinger.laser_physics import (
    burn_through_time,
    laser_threat_severity,
    max_burn_thickness,
    power_for_burn_through,
)
from goldfinger.market_attack import (
    CornerResult,
    corner_valuation,
    effective_supply,
    price_gain,
    shocked_equilibrium_price,
    simulate_corner,
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

__version__ = "0.1.0"

#: Mission identity for this film package (single source of truth).
FILM = "goldfinger"
CODENAME = "GRAND SLAM"

__all__ = [
    "CODENAME",
    "CornerResult",
    "DEFAULT_LAYERS",
    "FILM",
    "__version__",
    "burn_through_time",
    "corner_valuation",
    "effective_supply",
    "expected_breach_time",
    "laser_threat_severity",
    "layered_security_score",
    "marginal_improvements",
    "max_burn_thickness",
    "penetration_probability",
    "power_for_burn_through",
    "price_gain",
    "shocked_equilibrium_price",
    "simulate_corner",
    "vault_security_verdict",
    "weakest_layer",
]
