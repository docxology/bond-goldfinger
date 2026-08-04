"""Laser threat physics — burn-through time vs material and power.

The weapons-physics core of the GRAND SLAM mission. Auric Goldfinger's
signature gadget is a laser cutting tool; its threat to a vault is quantified
by how long a beam of a given power takes to burn through a plate of a given
material. This module implements the energy-balance (thermal) model of laser
penetration.

Model
-----
A continuous-wave laser of power :math:`P` (W) is focused onto a spot of area
:math:`A` (m²); the target absorbs a fraction ``a`` of the incident power, so

.. math:: P_{\\text{abs}} = a P.

To burn through a slab of thickness :math:`d`, density :math:`\\rho`, and
specific-heat capacity :math:`c`, the material column under the spot (mass
:math:`m = \\rho A d`) must be raised by :math:`\\Delta T` (ambient to
melting/vaporization threshold):

.. math:: Q = m c \\Delta T = \\rho A d c \\Delta T.

Equating absorbed power and energy gives the **burn-through time**

.. math:: t_{\\text{burn}} = \\frac{Q}{P_{\\text{abs}}}
    = \\frac{\\rho A d c \\Delta T}{a P}.

The module solves the same relation for power and thickness, so an operator
(the "laser threat") can be characterized from any two of
power / time / thickness. All values are SI; the module is pure (no I/O),
deterministic, and infrastructure-free.
"""

from __future__ import annotations

from typing import TypedDict

__all__ = [
    "absorbed_power",
    "burn_through_time",
    "energy_to_burn",
    "laser_threat_severity",
    "max_burn_thickness",
    "power_for_burn_through",
]

#: Threat classifications relative to a mission threshold (watts).
THREAT_LEVELS: tuple[str, ...] = ("trivial", "serious", "critical")


def _positive(value: float, label: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{label} must be a number")
    if value <= 0:
        raise ValueError(f"{label} must be positive")


def _absorptivity(value: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError("absorptivity must be a number")
    if not (0.0 < value <= 1.0):
        raise ValueError("absorptivity must be in (0, 1]")
    return float(value)


def absorbed_power(power: float, absorptivity: float = 1.0) -> float:
    """Power absorbed by the target: ``a * P``."""
    _positive(power, "power")
    return _absorptivity(absorptivity) * power


def energy_to_burn(
    area: float,
    density: float,
    thickness: float,
    specific_heat: float,
    delta_temperature: float,
) -> float:
    """Energy required to bring the material column under the spot to melt."""
    for value, label in (
        (area, "area"),
        (density, "density"),
        (thickness, "thickness"),
        (specific_heat, "specific_heat"),
        (delta_temperature, "delta_temperature"),
    ):
        _positive(value, label)
    return density * area * thickness * specific_heat * delta_temperature


def burn_through_time(
    power: float,
    area: float,
    density: float,
    thickness: float,
    specific_heat: float,
    delta_temperature: float,
    absorptivity: float = 1.0,
) -> float:
    """Seconds for a ``power``-watt beam (``absorptivity``) to burn through.

    Returns :func:`energy_to_burn` divided by :func:`absorbed_power`.
    """
    energy = energy_to_burn(area, density, thickness, specific_heat, delta_temperature)
    return energy / absorbed_power(power, absorptivity)


def power_for_burn_through(
    target_time: float,
    area: float,
    density: float,
    thickness: float,
    specific_heat: float,
    delta_temperature: float,
    absorptivity: float = 1.0,
) -> float:
    """Watts required to burn through in exactly ``target_time`` seconds."""
    _positive(target_time, "target_time")
    energy = energy_to_burn(area, density, thickness, specific_heat, delta_temperature)
    return energy / (target_time * _absorptivity(absorptivity))


def max_burn_thickness(
    time_budget: float,
    power: float,
    area: float,
    density: float,
    specific_heat: float,
    delta_temperature: float,
    absorptivity: float = 1.0,
) -> float:
    """Maximum plate thickness burnable within ``time_budget`` seconds."""
    _positive(time_budget, "time_budget")
    energy = time_budget * absorbed_power(power, absorptivity)
    denom = area * density * specific_heat * delta_temperature
    _positive(denom, "material energy constant")
    return energy / denom


def laser_threat_severity(power: float, threshold_power: float) -> str:
    """Classify a laser by its power against a mission threshold.

    ``"critical"`` when ``power >= 10 * threshold``, ``"serious"`` when
    ``power >= threshold``, otherwise ``"trivial"``.
    """
    _positive(power, "power")
    _positive(threshold_power, "threshold_power")
    if power >= 10.0 * threshold_power:
        return "critical"
    if power >= threshold_power:
        return "serious"
    return "trivial"


class _Physics(TypedDict):
    """Typed shape of the GRAND SLAM reference laser intel (SI units)."""

    power: float
    area: float
    density: float
    thickness: float
    specific_heat: float
    delta_temperature: float
    absorptivity: float


#: Reference intel used by the GRAND SLAM mission provider (SI units).
REFERENCE_PHYSICS: _Physics = {
    "power": 5000.0,  # W — military-grade continuous-wave laser
    "area": 1.0e-5,  # m² — focused spot (≈3.6 mm diameter)
    "density": 7800.0,  # kg/m³ — mild steel vault plate
    "thickness": 0.05,  # m — 50 mm vault plate
    "specific_heat": 500.0,  # J/(kg·K) — steel specific heat
    "delta_temperature": 1500.0,  # K — ambient → melting threshold
    "absorptivity": 0.6,  # fraction of incident power absorbed
}
