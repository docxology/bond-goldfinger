"""Macroeconomic attack — first-generation speculative attack on a gold peg.

The macroeconomic extension of Operation Grand Slam. The corner is only one
front; the deeper play is to *weaponise the monetary system itself*. Under a
gold-standard peg the central bank stands ready to sell gold (its reserves) at
a fixed parity :math:`\\bar{S}` (units of home currency per unit of gold). A
determined accumulator of gold — Auric Goldfinger — progressively widens the
attack by forcing the central bank to exhaust its reserves defending the peg.

This module implements the canonical **first-generation speculative-attack
model** of Flood & Garber (1984): a small open economy pegging its currency to
gold, an expanding domestic-credit base, and a rational-expectations shadow
floating exchange rate. When the shadow rate crosses the fixed parity, the peg
collapses in a discrete attack and the currency depreciates.

Model
-----
Money demand (linear in the interest rate):

.. math:: m_t - p_t = -\\alpha i_t, \\quad \\alpha > 0.

Purchasing-power parity pins the price level to the exchange rate
(:math:`p_t = s_t`), and uncovered interest parity gives
:math:`i_t = i^\\ast + \\dot s_t` under perfect foresight. The money supply is
:math:`M_t = R_t + D_t` (reserves plus domestic credit), and credit expands
exponentially, :math:`D_t = D_0 e^{\\mu t}`.

*Fixed regime.* With no expected depreciation, :math:`i = i^\\ast` and money is
constant, :math:`M = \\bar{S} - \\alpha i^\\ast`; reserves therefore drain as

.. math:: R_t = (\\bar{S} - \\alpha i^\\ast) - D_0 e^{\\mu t}.

*Shadow floating rate* (post-abandonment, reserves exhausted, :math:`M=D_t`):

.. math:: \\tilde{s}_t = \\frac{D_0 e^{\\mu t}}{1 - \\alpha\\mu} + \\alpha i^\\ast.

*Attack time.* The peg collapses at the first time the shadow rate equals the
parity,

.. math:: t^\\ast = \\frac{1}{\\mu}\\ln\\frac{(1-\\alpha\\mu)(\\bar{S} - \\alpha i^\\ast)}{D_0},

which precedes the gradual reserve-exhaustion time :math:`t_B = (1/\\mu)\\ln
((\\bar{S}-\\alpha i^\\ast)/D_0)` — the suddenness of the attack is the model's
headline. The post-float depreciation is the shadow rate once reserves are
gone, relative to parity.

The module is pure (no I/O), deterministic, and infrastructure-free.
"""

from __future__ import annotations

import math
from typing import TypedDict

__all__ = [
    "REFERENCE_ATTACK",
    "attack_time",
    "domestic_credit",
    "floating_depreciation",
    "reserve_floor_time",
    "reserve_level",
    "shadow_rate",
    "simulate_reserve_crisis",
    "surface_money",
]


def _positive(value: float, label: str, *, strict: bool = True) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{label} must be a number")
    if not math.isfinite(value):
        raise ValueError(f"{label} must be finite")
    if value <= 0 if strict else value < 0:
        raise ValueError(f"{label} must be {'positive' if strict else 'non-negative'}")


def _require_stable_peg(
    parity: float,
    foreign_rate: float,
    interest_elasticity: float,
    credit_0: float,
    growth: float,
) -> None:
    """Validate the model's economic-feasibility conditions."""
    _positive(parity, "parity")
    _positive(foreign_rate, "foreign_rate", strict=False)
    _positive(interest_elasticity, "interest_elasticity")
    _positive(credit_0, "credit_0")
    _positive(growth, "growth")
    denominator = 1.0 - interest_elasticity * growth
    if not (0.0 < denominator < 1.0):
        raise ValueError(
            "peg must be stable from the start: require 0 < interest_elasticity*growth < 1"
        )
    if credit_0 >= denominator * (parity - interest_elasticity * foreign_rate):
        raise ValueError("initial credit is too large for a future attack (peg already collapsed)")


def surface_money(parity: float, foreign_rate: float, interest_elasticity: float) -> float:
    """Constant real money stock implied by the fixed peg."""
    _positive(parity, "parity")
    _positive(foreign_rate, "foreign_rate", strict=False)
    _positive(interest_elasticity, "interest_elasticity")
    return float(parity - interest_elasticity * foreign_rate)


def domestic_credit(time: float, credit_0: float, growth: float) -> float:
    """Domestic credit ``D_0 e^(mu*t)`` at time ``time``."""
    _positive(time, "time", strict=False)
    _positive(credit_0, "credit_0")
    _positive(growth, "growth")
    return float(credit_0 * math.exp(growth * time))


def reserve_level(
    time: float,
    parity: float,
    foreign_rate: float,
    interest_elasticity: float,
    credit_0: float,
    growth: float,
) -> float:
    """Central-bank gold reserves under the fixed regime at ``time``."""
    _positive(time, "time", strict=False)
    _require_stable_peg(parity, foreign_rate, interest_elasticity, credit_0, growth)
    return float(
        surface_money(parity, foreign_rate, interest_elasticity)
        - domestic_credit(time, credit_0, growth)
    )


def shadow_rate(
    time: float,
    parity: float,
    foreign_rate: float,
    interest_elasticity: float,
    credit_0: float,
    growth: float,
) -> float:
    """Rational-expectations shadow floating exchange rate at ``time``."""
    _positive(time, "time", strict=False)
    _require_stable_peg(parity, foreign_rate, interest_elasticity, credit_0, growth)
    d_t = domestic_credit(time, credit_0, growth)
    denom = 1.0 - interest_elasticity * growth
    return float(d_t / denom + interest_elasticity * foreign_rate)


def attack_time(
    parity: float,
    foreign_rate: float,
    interest_elasticity: float,
    credit_0: float,
    growth: float,
) -> float:
    """First time the shadow floating rate crosses the fixed parity."""
    _require_stable_peg(parity, foreign_rate, interest_elasticity, credit_0, growth)
    base = surface_money(parity, foreign_rate, interest_elasticity) * (
        1.0 - interest_elasticity * growth
    )
    return float(math.log(base / credit_0) / growth)


def reserve_floor_time(
    parity: float,
    foreign_rate: float,
    interest_elasticity: float,
    credit_0: float,
    growth: float,
) -> float:
    """Time at which reserves would be *gradually* exhausted (`t_B`)."""
    _require_stable_peg(parity, foreign_rate, interest_elasticity, credit_0, growth)
    base = surface_money(parity, foreign_rate, interest_elasticity)
    return float(math.log(base / credit_0) / growth)


def floating_depreciation(
    parity: float,
    foreign_rate: float,
    interest_elasticity: float,
    credit_0: float,
    growth: float,
) -> float:
    """Depreciation once reserves are gone, as a fraction of parity.

    The shadow exchange rate evaluated at the reserve-exhaustion time, relative
    to parity: ``shadow(t_B)/parity - 1``.
    """
    _require_stable_peg(parity, foreign_rate, interest_elasticity, credit_0, growth)
    t_b = reserve_floor_time(parity, foreign_rate, interest_elasticity, credit_0, growth)
    shadow = shadow_rate(t_b, parity, foreign_rate, interest_elasticity, credit_0, growth)
    return float(shadow / parity - 1.0)


def simulate_reserve_crisis(
    times: tuple[float, ...],
    parity: float,
    foreign_rate: float,
    interest_elasticity: float,
    credit_0: float,
    growth: float,
) -> dict[str, tuple[float, ...]]:
    """Deterministic reserve / shadow trajectory over ``times``.

    Returns ``{"times", "reserves", "shadow_rates"}`` — the reserve-drain path
    under the peg and the rising shadow floating rate that triggers the attack.
    """
    if not times:
        raise ValueError("times must not be empty")
    reserves: list[float] = []
    shadows: list[float] = []
    for t in times:
        reserves.append(
            reserve_level(t, parity, foreign_rate, interest_elasticity, credit_0, growth)
        )
        shadows.append(shadow_rate(t, parity, foreign_rate, interest_elasticity, credit_0, growth))
    return {"times": times, "reserves": tuple(reserves), "shadow_rates": tuple(shadows)}


class _AttackIntel(TypedDict):
    """Typed shape of the GRAND SLAM reference speculative-attack intel."""

    parity: float
    foreign_rate: float
    interest_elasticity: float
    credit_0: float
    growth: float


#: Reference intel (Flood-Garber canonical parameters, normalised peg = 1.0).
REFERENCE_ATTACK: _AttackIntel = {
    "parity": 1.0,  # units of home currency per unit of gold (fixed peg)
    "foreign_rate": 0.02,  # foreign interest rate (fractional)
    "interest_elasticity": 8.0,  # alpha: money-demand semi-elasticity
    "credit_0": 0.10,  # initial domestic credit (fraction of money)
    "growth": 0.10,  # domestic-credit growth rate mu
}
