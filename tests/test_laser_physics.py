"""Real-data tests for the goldfinger laser threat physics module."""

from __future__ import annotations

import math

import pytest

from goldfinger.laser_physics import (
    REFERENCE_PHYSICS,
    THREAT_LEVELS,
    absorbed_power,
    burn_through_time,
    energy_to_burn,
    laser_threat_severity,
    max_burn_thickness,
    power_for_burn_through,
)


def test_absorbed_power() -> None:
    assert absorbed_power(5000.0) == pytest.approx(5000.0)
    assert absorbed_power(5000.0, absorptivity=0.6) == pytest.approx(3000.0)


def test_absorbed_power_invalid() -> None:
    with pytest.raises(ValueError):
        absorbed_power(0.0)
    with pytest.raises(ValueError):
        absorbed_power(5000.0, absorptivity=0.0)
    with pytest.raises(ValueError):
        absorbed_power(5000.0, absorptivity=1.5)
    with pytest.raises(TypeError):
        absorbed_power(True)


def test_energy_to_burn_hand_vector() -> None:
    # rho*A*d*c*dT = 7800 * 1e-5 * 0.05 * 500 * 1500
    energy = energy_to_burn(1.0e-5, 7800.0, 0.05, 500.0, 1500.0)
    assert energy == pytest.approx(2925.0)


def test_energy_to_burn_invalid() -> None:
    with pytest.raises(ValueError):
        energy_to_burn(-1.0e-5, 7800.0, 0.05, 500.0, 1500.0)


def test_burn_through_time_reference() -> None:
    # Q = 2925 J, P_abs = 3000 W -> t ~ 0.975 s
    t = burn_through_time(5000.0, 1.0e-5, 7800.0, 0.05, 500.0, 1500.0, absorptivity=0.6)
    assert t == pytest.approx(0.975, rel=1e-6)
    assert t == burn_through_time(
        REFERENCE_PHYSICS["power"],
        REFERENCE_PHYSICS["area"],
        REFERENCE_PHYSICS["density"],
        REFERENCE_PHYSICS["thickness"],
        REFERENCE_PHYSICS["specific_heat"],
        REFERENCE_PHYSICS["delta_temperature"],
        REFERENCE_PHYSICS["absorptivity"],
    )


def test_burn_through_time_inverse_scales_with_power() -> None:
    t1 = burn_through_time(2000.0, 1.0e-5, 7800.0, 0.05, 500.0, 1500.0, absorptivity=1.0)
    t2 = burn_through_time(4000.0, 1.0e-5, 7800.0, 0.05, 500.0, 1500.0, absorptivity=1.0)
    assert t1 == pytest.approx(2.0 * t2)


def test_burn_through_time_linear_in_thickness() -> None:
    thin = burn_through_time(5000.0, 1.0e-5, 7800.0, 0.02, 500.0, 1500.0, absorptivity=0.6)
    thick = burn_through_time(5000.0, 1.0e-5, 7800.0, 0.05, 500.0, 1500.0, absorptivity=0.6)
    assert thick == pytest.approx(thin * (0.05 / 0.02))


def test_power_for_burn_through_round_trips() -> None:
    power = 5000.0
    t = burn_through_time(power, 1.0e-5, 7800.0, 0.05, 500.0, 1500.0, absorptivity=0.6)
    required = power_for_burn_through(t, 1.0e-5, 7800.0, 0.05, 500.0, 1500.0, absorptivity=0.6)
    assert required == pytest.approx(power)


def test_max_burn_thickness_round_trips() -> None:
    t = burn_through_time(5000.0, 1.0e-5, 7800.0, 0.05, 500.0, 1500.0, absorptivity=0.6)
    d = max_burn_thickness(t, 5000.0, 1.0e-5, 7800.0, 500.0, 1500.0, absorptivity=0.6)
    assert d == pytest.approx(0.05)


def test_max_burn_thickness_invalid() -> None:
    with pytest.raises(ValueError):
        max_burn_thickness(-1.0, 5000.0, 1.0e-5, 7800.0, 500.0, 1500.0)


def test_threat_severity_levels() -> None:
    assert laser_threat_severity(5000.0, 1000.0) == "serious"
    assert laser_threat_severity(20000.0, 1000.0) == "critical"
    assert laser_threat_severity(100.0, 1000.0) == "trivial"
    assert set(THREAT_LEVELS) == {"trivial", "serious", "critical"}


def test_threat_severity_boundary() -> None:
    # power == 10 * threshold is critical (>=).
    assert laser_threat_severity(10000.0, 1000.0) == "critical"
    assert laser_threat_severity(1000.0, 1000.0) == "serious"


def test_threat_severity_invalid() -> None:
    with pytest.raises(ValueError):
        laser_threat_severity(-5.0, 1000.0)
    with pytest.raises(ValueError):
        laser_threat_severity(5000.0, 0.0)


def test_reference_physics_deterministic() -> None:
    t1 = burn_through_time(
        REFERENCE_PHYSICS["power"],
        REFERENCE_PHYSICS["area"],
        REFERENCE_PHYSICS["density"],
        REFERENCE_PHYSICS["thickness"],
        REFERENCE_PHYSICS["specific_heat"],
        REFERENCE_PHYSICS["delta_temperature"],
        REFERENCE_PHYSICS["absorptivity"],
    )
    assert t1 == burn_through_time(
        REFERENCE_PHYSICS["power"],
        REFERENCE_PHYSICS["area"],
        REFERENCE_PHYSICS["density"],
        REFERENCE_PHYSICS["thickness"],
        REFERENCE_PHYSICS["specific_heat"],
        REFERENCE_PHYSICS["delta_temperature"],
        REFERENCE_PHYSICS["absorptivity"],
    )
    assert math.isfinite(t1)
