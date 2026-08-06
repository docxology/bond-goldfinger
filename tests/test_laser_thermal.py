"""Real-data tests for the goldfinger laser thermal engagement module."""

from __future__ import annotations

import math

import pytest

from goldfinger.laser_thermal import (
    REFERENCE_BEAM,
    effective_burn_range,
    melt_time_at_distance,
    power_density,
    rayleigh_range,
    spot_radius_at_distance,
    surface_melt_time,
    thermal_surface_temperature,
)

B = REFERENCE_BEAM


def test_rayleigh_range_formula() -> None:
    assert rayleigh_range(1.0e-3, 1.0e-6) == pytest.approx(math.pi * 1e-6 / 1e-6)


def test_spot_radius_at_waist_and_growth() -> None:
    assert spot_radius_at_distance(B["waist"], B["wavelength"], 0.0) == pytest.approx(B["waist"])
    far = spot_radius_at_distance(B["waist"], B["wavelength"], 50.0)
    assert far > B["waist"]


def test_power_density_formula() -> None:
    # a*P/(pi r^2): r chosen so area = 1e-5 -> flux = 3000/1e-5
    r = math.sqrt(1e-5 / math.pi)
    assert power_density(5000.0, r, 0.6) == pytest.approx(3.0e8, rel=1e-6)


def test_power_density_invalid() -> None:
    with pytest.raises(ValueError):
        power_density(-1.0, B["waist"])
    with pytest.raises(ValueError):
        power_density(5000.0, 0.0)
    with pytest.raises(ValueError):
        power_density(5000.0, B["waist"], absorptivity=1.5)


def test_surface_temperature_rises_with_sqrt_t() -> None:
    t1 = thermal_surface_temperature(
        1.0, 3.0e8, B["conductivity"], B["density"], B["specific_heat"], B["ambient"]
    )
    t4 = thermal_surface_temperature(
        4.0, 3.0e8, B["conductivity"], B["density"], B["specific_heat"], B["ambient"]
    )
    assert t4 > t1
    # Doubling sqrt(t) (4x t) doubles the temperature rise above ambient.
    assert (t4 - B["ambient"]) == pytest.approx(2.0 * (t1 - B["ambient"]))


def test_surface_melt_time_inverse_in_flux() -> None:
    slow = surface_melt_time(
        1.0e8, B["conductivity"], B["density"], B["specific_heat"], B["melt_temp"], B["ambient"]
    )
    fast = surface_melt_time(
        2.0e8, B["conductivity"], B["density"], B["specific_heat"], B["melt_temp"], B["ambient"]
    )
    assert slow == pytest.approx(4.0 * fast)  # t ~ 1/flux^2


def test_surface_melt_time_requires_melt_above_ambient() -> None:
    with pytest.raises(ValueError):
        surface_melt_time(1.0e8, B["conductivity"], B["density"], B["specific_heat"], 200.0, 300.0)
    with pytest.raises(ValueError):
        surface_melt_time(
            -1.0, B["conductivity"], B["density"], B["specific_heat"], B["melt_temp"], B["ambient"]
        )


def test_melt_time_lengthens_with_distance() -> None:
    near = melt_time_at_distance(
        B["power"],
        B["waist"],
        B["wavelength"],
        0.0,
        B["absorptivity"],
        B["conductivity"],
        B["density"],
        B["specific_heat"],
        B["melt_temp"],
        B["ambient"],
    )
    far = melt_time_at_distance(
        B["power"],
        B["waist"],
        B["wavelength"],
        60.0,
        B["absorptivity"],
        B["conductivity"],
        B["density"],
        B["specific_heat"],
        B["melt_temp"],
        B["ambient"],
    )
    assert near < far


def test_effective_burn_range_is_interior_and_valid() -> None:
    rng = effective_burn_range(
        B["power"],
        B["waist"],
        B["wavelength"],
        B["absorptivity"],
        B["conductivity"],
        B["density"],
        B["specific_heat"],
        B["melt_temp"],
        B["ambient"],
        B["threat_window"],
        max_distance=100.0,
        step=1.0,
    )
    assert isinstance(rng.range_m, float) and 0.0 < rng.range_m < 100.0
    assert rng.burns_at_focus is True  # the reference beam melts at focus
    # At the returned range the melt time is still within the window.
    t_at = melt_time_at_distance(
        B["power"],
        B["waist"],
        B["wavelength"],
        rng.range_m,
        B["absorptivity"],
        B["conductivity"],
        B["density"],
        B["specific_heat"],
        B["melt_temp"],
        B["ambient"],
    )
    assert t_at <= B["threat_window"]
    # Just past the range (+step) the melt time exceeds the window.
    t_past = melt_time_at_distance(
        B["power"],
        B["waist"],
        B["wavelength"],
        rng.range_m + 1.0,
        B["absorptivity"],
        B["conductivity"],
        B["density"],
        B["specific_heat"],
        B["melt_temp"],
        B["ambient"],
    )
    assert t_past > B["threat_window"]


def test_effective_burn_range_invalid() -> None:
    with pytest.raises(ValueError):
        effective_burn_range(
            B["power"],
            B["waist"],
            B["wavelength"],
            B["absorptivity"],
            -1.0,
            B["density"],
            B["specific_heat"],
            B["melt_temp"],
            B["ambient"],
            B["threat_window"],
        )
    with pytest.raises(ValueError):
        effective_burn_range(
            B["power"],
            B["waist"],
            B["wavelength"],
            B["absorptivity"],
            B["conductivity"],
            B["density"],
            B["specific_heat"],
            B["melt_temp"],
            B["ambient"],
            -1.0,
        )


def test_burn_range_disambiguates_focus_only_from_never_melts() -> None:
    """C2: a zero range is never ambiguous — the flag carries the meaning.

    A very short window that still lets the *focal* point melt yields
    ``burns_at_focus`` True (focus-only), while a window too short even for
    the focus yields False (never melts). A bare float could not express this.
    """
    # Focus-only: a window strictly between the focal melt time and the 1 m
    # melt time — the focal point melts but no positive scan step does, so the
    # range is 0 yet burns_at_focus is True.
    focal_melt = melt_time_at_distance(
        B["power"],
        B["waist"],
        B["wavelength"],
        0.0,
        B["absorptivity"],
        B["conductivity"],
        B["density"],
        B["specific_heat"],
        B["melt_temp"],
        B["ambient"],
    )
    at_one = melt_time_at_distance(
        B["power"],
        B["waist"],
        B["wavelength"],
        1.0,
        B["absorptivity"],
        B["conductivity"],
        B["density"],
        B["specific_heat"],
        B["melt_temp"],
        B["ambient"],
    )
    tight_window = (focal_melt + at_one) / 2.0  # between the two melt times
    focus_only = effective_burn_range(
        B["power"],
        B["waist"],
        B["wavelength"],
        B["absorptivity"],
        B["conductivity"],
        B["density"],
        B["specific_heat"],
        B["melt_temp"],
        B["ambient"],
        threat_window=tight_window,
    )
    assert focus_only.range_m == 0.0
    assert focus_only.burns_at_focus is True

    # Never-melts: window far shorter than the focal melt time.
    never = effective_burn_range(
        B["power"],
        B["waist"],
        B["wavelength"],
        B["absorptivity"],
        B["conductivity"],
        B["density"],
        B["specific_heat"],
        B["melt_temp"],
        B["ambient"],
        threat_window=1.0e-12,
    )
    assert never.range_m == 0.0
    assert never.burns_at_focus is False
    # The two cases are now distinguishable without a second melt-time call.
    assert focus_only.burns_at_focus is not never.burns_at_focus


def test_reference_deterministic() -> None:
    a = effective_burn_range(
        B["power"],
        B["waist"],
        B["wavelength"],
        B["absorptivity"],
        B["conductivity"],
        B["density"],
        B["specific_heat"],
        B["melt_temp"],
        B["ambient"],
        B["threat_window"],
    )
    b = effective_burn_range(
        B["power"],
        B["waist"],
        B["wavelength"],
        B["absorptivity"],
        B["conductivity"],
        B["density"],
        B["specific_heat"],
        B["melt_temp"],
        B["ambient"],
        B["threat_window"],
    )
    assert a == b  # frozen dataclasses compare field-wise
    assert a.range_m == pytest.approx(65.0, abs=1.0)  # reference effective range
    assert a.burns_at_focus is True
