"""Real-data tests for the goldfinger market-cornering model (Operation Grand Slam)."""

from __future__ import annotations

import math

import pytest

from goldfinger.market_attack import (
    REFERENCE_MODEL,
    CornerResult,
    corner_valuation,
    effective_supply,
    price_gain,
    shocked_equilibrium_price,
    simulate_corner,
)


def test_effective_supply_reduces_float() -> None:
    assert effective_supply(100.0, 0.30) == pytest.approx(70.0)


def test_effective_supply_none_removed() -> None:
    assert effective_supply(100.0, 0.0) == pytest.approx(100.0)


def test_effective_supply_invalid_fraction() -> None:
    with pytest.raises(ValueError):
        effective_supply(100.0, 1.0)
    with pytest.raises(ValueError):
        effective_supply(100.0, -0.1)
    with pytest.raises(TypeError):
        effective_supply(100.0, True)


def test_effective_supply_invalid_supply() -> None:
    with pytest.raises(ValueError):
        effective_supply(0.0, 0.1)
    with pytest.raises(TypeError):
        effective_supply("100", 0.1)


def test_shocked_equilibrium_price_hand_vector() -> None:
    # With a 30% supply cut and elasticity 1, price doubles.
    price = shocked_equilibrium_price(100.0, 100.0, 70.0, 1.0)
    assert price == pytest.approx(100.0 * (100.0 / 70.0))


def test_shocked_price_monotonic_in_supply_cut() -> None:
    low_cut = shocked_equilibrium_price(1850.0, 100.0, effective_supply(100.0, 0.1), 1.25)
    high_cut = shocked_equilibrium_price(1850.0, 100.0, effective_supply(100.0, 0.5), 1.25)
    assert high_cut > low_cut > 1850.0


def test_shocked_price_invalid_inputs() -> None:
    with pytest.raises(ValueError):
        shocked_equilibrium_price(-1.0, 100.0, 70.0, 1.0)
    with pytest.raises(ValueError):
        shocked_equilibrium_price(100.0, 0.0, 70.0, 1.0)
    with pytest.raises(ValueError):
        shocked_equilibrium_price(100.0, 100.0, 70.0, 0.0)


def test_price_gain_matches_direct_computation() -> None:
    gain = price_gain(1850.0, 100.0, 0.30, 1.25)
    shocked = shocked_equilibrium_price(1850.0, 100.0, effective_supply(100.0, 0.30), 1.25)
    assert gain == pytest.approx(shocked / 1850.0 - 1.0)


def test_simulate_corner_returns_corner_result() -> None:
    result = simulate_corner(1850.0, 100.0, 0.30, 1.25)
    assert isinstance(result, CornerResult)
    assert len(result.trajectory) == REFERENCE_MODEL["steps"] + 1
    # Trajectory starts at the reference price and heads toward the shock.
    assert result.trajectory[0] == pytest.approx(1850.0)
    assert result.shocked_price > 1850.0


def test_simulate_corner_converges_to_shocked_price() -> None:
    result = simulate_corner(1850.0, 100.0, 0.30, 1.25, adjustment=0.5, steps=200)
    assert result.trajectory[-1] == pytest.approx(result.shocked_price, abs=1e-6)


def test_simulate_corner_diverges_for_adjustment_ge_two() -> None:
    with pytest.raises(ValueError):
        simulate_corner(1850.0, 100.0, 0.30, 1.25, adjustment=2.0)
    with pytest.raises(ValueError):
        simulate_corner(1850.0, 100.0, 0.30, 1.25, adjustment=0.0)
    with pytest.raises(TypeError):
        simulate_corner(1850.0, 100.0, 0.30, 1.25, adjustment=True)


def test_simulate_corner_negative_steps() -> None:
    with pytest.raises(ValueError):
        simulate_corner(1850.0, 100.0, 0.30, 1.25, steps=-1)
    with pytest.raises(TypeError):
        simulate_corner(1850.0, 100.0, 0.30, 1.25, steps=1.5)


def test_corner_valuation() -> None:
    assert corner_valuation(1850.0, 100.0) == pytest.approx(185000.0)
    assert corner_valuation(1850.0, 0.0) == pytest.approx(0.0)
    with pytest.raises(ValueError):
        corner_valuation(1850.0, -1.0)
    with pytest.raises(TypeError):
        corner_valuation("1850", 100.0)


def test_reference_model_is_deterministic() -> None:
    first = simulate_corner(
        REFERENCE_MODEL["reference_price"],
        REFERENCE_MODEL["supply_0"],
        REFERENCE_MODEL["fraction_removed"],
        REFERENCE_MODEL["elasticity"],
        REFERENCE_MODEL["adjustment"],
        REFERENCE_MODEL["steps"],
    )
    second = simulate_corner(
        REFERENCE_MODEL["reference_price"],
        REFERENCE_MODEL["supply_0"],
        REFERENCE_MODEL["fraction_removed"],
        REFERENCE_MODEL["elasticity"],
        REFERENCE_MODEL["adjustment"],
        REFERENCE_MODEL["steps"],
    )
    assert first.trajectory == second.trajectory
    assert math.isfinite(first.shocked_price)
