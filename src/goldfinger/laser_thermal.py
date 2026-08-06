"""Laser thermal engagement — Gaussian beam focusing and heat conduction.

The laser-threat extension. :mod:`goldfinger.laser_physics` gives a scalar
energy-balance burn-through time; this module models the *spatio-temporal*
physics of the threat:

* **Beam optics** — the beam is Gaussian. Its waist :math:`w_0` and wavelength
  :math:`\\lambda` give the Rayleigh range :math:`z_R = \\pi w_0^2/\\lambda` and
  the spot radius grows as :math:`w(z) = w_0\\sqrt{1+(z/z_R)^2}`, so defocusing
  with range lowers the intensity the target absorbs
  (:math:`I = a P/(\\pi w^2)`).

* **Heat conduction** — under constant absorbed surface flux the surface
  temperature of a semi-infinite solid follows the Carslaw–Jaeger solution

  .. math:: T(0,t) = T_\\text{amb} + \\frac{2 I_a}{\\sqrt{\\pi k\\rho c}}\\sqrt{t},

  so the time for the surface to reach the melt temperature is

  .. math::
     t_\\text{melt} = \\frac{\\pi}{4}\\frac{k\\rho c\\,(T_\\text{melt}-T_\\text{amb})^2}{I_a^2}.

* **Engagement envelope** — combining the two, the effective burn range is the
  greatest distance at which the defocused beam still melts the target within a
  given threat window.

The module is pure (no I/O), deterministic, and infrastructure-free (stdlib
``math`` only).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TypedDict


@dataclass(frozen=True)
class BurnRangeResult:
    """The effective burn range and whether the beam melts at focus.

    The range alone is two-valued: ``range_m == 0.0`` means *either* "only the
    focal point melts within the window" *or* "no scanned distance melts". The
    explicit ``burns_at_focus`` flag disambiguates, so a caller needs no second
    melt-time evaluation to interpret a zero range.
    """

    range_m: float
    burns_at_focus: bool


__all__ = [
    "REFERENCE_BEAM",
    "BurnRangeResult",
    "effective_burn_range",
    "melt_time_at_distance",
    "power_density",
    "rayleigh_range",
    "spot_radius_at_distance",
    "surface_melt_time",
    "thermal_surface_temperature",
]


def _positive(value: float, label: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{label} must be a number")
    if not math.isfinite(value):
        raise ValueError(f"{label} must be finite")
    if value <= 0:
        raise ValueError(f"{label} must be positive")


def _non_negative(value: float, label: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{label} must be a number")
    if not math.isfinite(value):
        raise ValueError(f"{label} must be finite")
    if value < 0:
        raise ValueError(f"{label} must be non-negative")


def _absorptivity(value: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError("absorptivity must be a number")
    if not (0.0 < value <= 1.0):
        raise ValueError("absorptivity must be in (0, 1]")
    return float(value)


def rayleigh_range(waist: float, wavelength: float) -> float:
    """Rayleigh range of a Gaussian beam, :math:`\\pi w_0^2/\\lambda` (m)."""
    _positive(waist, "waist")
    _positive(wavelength, "wavelength")
    return float(math.pi * waist**2 / wavelength)


def spot_radius_at_distance(waist: float, wavelength: float, distance: float) -> float:
    """Gaussian spot radius (m) at a given axial distance from the waist."""
    _positive(waist, "waist")
    _positive(wavelength, "wavelength")
    _non_negative(distance, "distance")
    z_r = rayleigh_range(waist, wavelength)
    return float(waist * math.sqrt(1.0 + (distance / z_r) ** 2))


def power_density(power: float, spot_radius: float, absorptivity: float = 1.0) -> float:
    """Absorbed surface power density, :math:`a P/(\\pi r^2)` (W/m²)."""
    _positive(power, "power")
    _positive(spot_radius, "spot_radius")
    a = _absorptivity(absorptivity)
    return float(a * power / (math.pi * spot_radius**2))


def thermal_surface_temperature(
    time: float,
    flux: float,
    conductivity: float,
    density: float,
    specific_heat: float,
    ambient: float,
) -> float:
    """Carslaw–Jaeger surface temperature (K) under constant flux at ``time``."""
    _positive(time, "time")
    _positive(flux, "flux")
    _positive(conductivity, "conductivity")
    _positive(density, "density")
    _positive(specific_heat, "specific_heat")
    _non_negative(ambient, "ambient")
    factor = float(2.0 * flux / math.sqrt(math.pi * conductivity * density * specific_heat))
    return float(ambient + factor * math.sqrt(time))


def surface_melt_time(
    flux: float,
    conductivity: float,
    density: float,
    specific_heat: float,
    melt_temp: float,
    ambient: float,
) -> float:
    """Time (s) until the surface reaches ``melt_temp`` under constant flux."""
    _positive(flux, "flux")
    _positive(conductivity, "conductivity")
    _positive(density, "density")
    _positive(specific_heat, "specific_heat")
    _positive(melt_temp, "melt_temp")
    _non_negative(ambient, "ambient")
    if melt_temp <= ambient:
        raise ValueError("melt_temp must exceed ambient for a finite melt time")
    d_t = melt_temp - ambient
    material = conductivity * density * specific_heat
    return float((math.pi / 4.0) * material * d_t**2 / flux**2)


def melt_time_at_distance(
    power: float,
    waist: float,
    wavelength: float,
    distance: float,
    absorptivity: float,
    conductivity: float,
    density: float,
    specific_heat: float,
    melt_temp: float,
    ambient: float,
) -> float:
    """Surface melt time (s) for a beam aimed at a target ``distance`` away."""
    spot = spot_radius_at_distance(waist, wavelength, distance)
    flux = power_density(power, spot, absorptivity)
    return surface_melt_time(flux, conductivity, density, specific_heat, melt_temp, ambient)


def effective_burn_range(
    power: float,
    waist: float,
    wavelength: float,
    absorptivity: float,
    conductivity: float,
    density: float,
    specific_heat: float,
    melt_temp: float,
    ambient: float,
    threat_window: float,
    max_distance: float = 200.0,
    step: float = 1.0,
) -> BurnRangeResult:
    """Return the burn range and whether the beam melts at focus.

    Scans ``0 .. max_distance`` in ``step`` increments and returns a
    :class:`BurnRangeResult` whose ``range_m`` is the largest scanned distance
    whose melt time is within the threat window. The companion ``burns_at_focus``
    flag carries whether the focal point (0 m) melts within the window, so a
    zero ``range_m`` is never ambiguous: focus-only melting yields
    ``(0.0, True)`` and no melting anywhere in the window yields
    ``(0.0, False)`` — a distinction the bare float return could not express.
    """
    _positive(conductivity, "conductivity")
    _positive(threat_window, "threat_window")
    _non_negative(max_distance, "max_distance")
    _positive(step, "step")

    def _melt(d: float) -> float:
        return melt_time_at_distance(
            power,
            waist,
            wavelength,
            d,
            absorptivity,
            conductivity,
            density,
            specific_heat,
            melt_temp,
            ambient,
        )

    burns_at_focus = _melt(0.0) <= threat_window
    burn_distance = 0.0
    distance = 0.0
    while distance <= max_distance:
        if _melt(distance) <= threat_window:
            burn_distance = distance
        distance += step
    return BurnRangeResult(range_m=float(burn_distance), burns_at_focus=burns_at_focus)


class _BeamIntel(TypedDict):
    """Typed shape of the GRAND SLAM reference laser thermal intel (SI units)."""

    power: float
    waist: float
    wavelength: float
    absorptivity: float
    conductivity: float
    density: float
    specific_heat: float
    melt_temp: float
    ambient: float
    threat_window: float


#: Reference intel — an Nd:YAG-class continuous-wave laser vs a steel plate.
#:
#: This is the *same* reference plate as
#: :data:`goldfinger.laser_physics.REFERENCE_PHYSICS`: ``density`` and
#: ``specific_heat`` match that module's values, and ``melt_temp - ambient``
#: equals its ``delta_temperature``. ``tests/test_reference_intel.py`` asserts
#: the agreement, so the two models cannot describe different steel.
REFERENCE_BEAM: _BeamIntel = {
    "power": 5000.0,  # W
    "waist": 1.78e-3,  # m — ~1.8 mm focus radius (spot area ~1e-5 m^2)
    "wavelength": 1.064e-6,  # m — Nd:YAG
    "absorptivity": 0.6,
    "conductivity": 45.0,  # W/(m·K) — steel
    "density": 7800.0,  # kg/m^3
    "specific_heat": 460.0,  # J/(kg·K)
    "melt_temp": 1500.0,  # K
    "ambient": 300.0,  # K
    "threat_window": 5.0,  # s — threat is "serious" if it melts within 5s
}
