"""Real-data tests for the goldfinger speculative-attack (reserve_attack) module."""

from __future__ import annotations

import pytest

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

A = REFERENCE_ATTACK


def test_surface_money_hand_vector() -> None:
    # m = S_bar - alpha*i* = 1.0 - 8*0.02
    assert surface_money(A["parity"], A["foreign_rate"], A["interest_elasticity"]) == pytest.approx(
        0.84
    )


def test_domestic_credit_grows() -> None:
    assert domestic_credit(0.0, A["credit_0"], A["growth"]) == pytest.approx(A["credit_0"])
    later = domestic_credit(5.0, A["credit_0"], A["growth"])
    assert later > A["credit_0"]


def test_reserves_drain_over_time() -> None:
    r0 = reserve_level(
        0.0, A["parity"], A["foreign_rate"], A["interest_elasticity"], A["credit_0"], A["growth"]
    )
    r1 = reserve_level(
        4.0, A["parity"], A["foreign_rate"], A["interest_elasticity"], A["credit_0"], A["growth"]
    )
    assert r0 > r1 > 0.0
    assert r0 == pytest.approx(0.74)  # 0.84 - 0.10


def test_shadow_rate_rises_over_time() -> None:
    s0 = shadow_rate(
        0.0, A["parity"], A["foreign_rate"], A["interest_elasticity"], A["credit_0"], A["growth"]
    )
    s1 = shadow_rate(
        4.0, A["parity"], A["foreign_rate"], A["interest_elasticity"], A["credit_0"], A["growth"]
    )
    assert s1 > s0
    # At t=0 the peg is still credible (shadow below parity).
    assert s0 < A["parity"]


def test_attack_time_closed_form() -> None:
    attack = attack_time(
        A["parity"], A["foreign_rate"], A["interest_elasticity"], A["credit_0"], A["growth"]
    )
    assert attack == pytest.approx(5.188, abs=1e-2)
    assert attack > 0.0


def test_attack_precedes_gradual_exhaustion() -> None:
    attack = attack_time(
        A["parity"], A["foreign_rate"], A["interest_elasticity"], A["credit_0"], A["growth"]
    )
    floor = reserve_floor_time(
        A["parity"], A["foreign_rate"], A["interest_elasticity"], A["credit_0"], A["growth"]
    )
    assert 0.0 < attack < floor


def test_shadow_equals_parity_at_attack() -> None:
    attack = attack_time(
        A["parity"], A["foreign_rate"], A["interest_elasticity"], A["credit_0"], A["growth"]
    )
    shadow = shadow_rate(
        attack, A["parity"], A["foreign_rate"], A["interest_elasticity"], A["credit_0"], A["growth"]
    )
    assert shadow == pytest.approx(A["parity"], abs=1e-9)


def test_floating_depreciation_positive() -> None:
    dep = floating_depreciation(
        A["parity"], A["foreign_rate"], A["interest_elasticity"], A["credit_0"], A["growth"]
    )
    assert dep > 0.0


def test_simulate_reserve_crisis_paths() -> None:
    crisis = simulate_reserve_crisis(
        (0.0, 2.0, 4.0),
        A["parity"],
        A["foreign_rate"],
        A["interest_elasticity"],
        A["credit_0"],
        A["growth"],
    )
    assert crisis["times"] == (0.0, 2.0, 4.0)
    assert len(crisis["reserves"]) == 3
    assert len(crisis["shadow_rates"]) == 3
    # Reserves fall and shadow rises monotonically over the window.
    assert crisis["reserves"][0] > crisis["reserves"][-1]
    assert crisis["shadow_rates"][0] < crisis["shadow_rates"][-1]


def test_simulate_reserve_crisis_empty_raises() -> None:
    with pytest.raises(ValueError):
        simulate_reserve_crisis(
            (), A["parity"], A["foreign_rate"], A["interest_elasticity"], A["credit_0"], A["growth"]
        )


def test_unstable_peg_raises() -> None:
    # alpha*mu >= 1 -> denominator <= 0 -> unstable from the start.
    with pytest.raises(ValueError):
        attack_time(A["parity"], A["foreign_rate"], 12.0, A["credit_0"], A["growth"])
    # credit_0 too large -> peg already collapsed.
    with pytest.raises(ValueError):
        attack_time(A["parity"], A["foreign_rate"], A["interest_elasticity"], 0.9, A["growth"])


def test_invalid_inputs() -> None:
    with pytest.raises(TypeError):
        domestic_credit(0.0, "0.1", A["growth"])
    with pytest.raises(ValueError):
        reserve_level(
            0.0, -1.0, A["foreign_rate"], A["interest_elasticity"], A["credit_0"], A["growth"]
        )
    with pytest.raises(ValueError):
        shadow_rate(
            -1.0,
            A["parity"],
            A["foreign_rate"],
            A["interest_elasticity"],
            A["credit_0"],
            A["growth"],
        )


def test_determinism() -> None:
    a1 = attack_time(
        A["parity"], A["foreign_rate"], A["interest_elasticity"], A["credit_0"], A["growth"]
    )
    a2 = attack_time(
        A["parity"], A["foreign_rate"], A["interest_elasticity"], A["credit_0"], A["growth"]
    )
    assert a1 == a2
