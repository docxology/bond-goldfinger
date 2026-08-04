"""Gold-market cornering model — Operation Grand Slam.

The economic core of the GRAND SLAM mission. Auric Goldfinger's scheme is to
drive the price of gold up by removing a large tranche of the floatable supply
from the market (a *corner*). This module formalizes that with a
constant-elasticity inverse-demand model joined to a tatonnement price
adjustment, so the resulting corner can be *simulated*: how far the price
jumps and how quickly it converges to the shocked equilibrium.

Model
-----
Let :math:`\\mathcal{S}_0` be the floatable supply under normal conditions,
clearing at a reference price :math:`P_0`. Operation Grand Slam sterilizes a
fraction :math:`f \\in [0,1)` of that supply, so the effective supply becomes

.. math:: \\mathcal{S}_{\\text{eff}} = \\mathcal{S}_0\\,(1 - f).

With constant-elasticity demand :math:`Q_d(P) = k P^{-\\eta}` (elasticity
:math:`\\eta > 0`), market clearing determines the shocked equilibrium price

.. math:: P^* = P_0\\, \\left(\\frac{\\mathcal{S}_0}{\\mathcal{S}_{\\text{eff}}}\\right)^{1/\\eta}.

Price does not jump instantly; it adjusts toward :math:`P^*` via a discrete
tatonnement process with adjustment coefficient :math:`\\lambda \\in (0, 2)`,

.. math:: P_{t+1} = P_t + \\lambda\\,(P^* - P_t),

yielding a deterministic trajectory that converges to :math:`P^*`.

The module is pure (no I/O), deterministic, and infrastructure-free.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypedDict

__all__ = [
    "CornerResult",
    "corner_valuation",
    "effective_supply",
    "price_gain",
    "shocked_equilibrium_price",
    "simulate_corner",
]


def _positive(value: float, label: str, *, strict: bool = True) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{label} must be a number")
    if value <= 0 if strict else value < 0:
        raise ValueError(f"{label} must be {'positive' if strict else 'non-negative'}")


@dataclass(frozen=True)
class CornerResult:
    """The computed corner: equilibrium shift and the price trajectory."""

    shocked_price: float
    gain: float  # fractional price gain over the reference (P*/P0 - 1)
    trajectory: tuple[float, ...]  # per-step prices starting at P0


def effective_supply(supply_0: float, fraction_removed: float) -> float:
    """Return the floatable supply after ``fraction_removed`` is sterilized.

    Args:
        supply_0: Floatable supply under normal conditions (positive).
        fraction_removed: Fraction of supply removed, in ``[0, 1)``.

    Returns:
        The effective trading supply ``supply_0 * (1 - fraction_removed)``.
    """
    _positive(supply_0, "supply_0")
    if isinstance(fraction_removed, bool) or not isinstance(fraction_removed, (int, float)):
        raise TypeError("fraction_removed must be a number")
    if not (0.0 <= fraction_removed < 1.0):
        raise ValueError("fraction_removed must be in [0, 1)")
    return supply_0 * (1.0 - fraction_removed)


def shocked_equilibrium_price(
    reference_price: float,
    supply_0: float,
    effective_supply_value: float,
    elasticity: float,
) -> float:
    """Market-clearing price after the supply shock.

    Args:
        reference_price: Pre-shock clearing price ``P0`` (positive).
        supply_0: Pre-shock floatable supply (positive).
        effective_supply_value: Post-shock effective supply (positive).
        elasticity: Constant price-elasticity of demand ``eta > 0``.

    Returns:
        The shocked equilibrium price :math:`P0 (S0 / S_eff)^{1/eta}`.
    """
    _positive(reference_price, "reference_price")
    _positive(supply_0, "supply_0")
    _positive(effective_supply_value, "effective_supply_value")
    _positive(elasticity, "elasticity")
    ratio = supply_0 / effective_supply_value
    return float(reference_price * ratio ** (1.0 / elasticity))


def price_gain(
    reference_price: float,
    supply_0: float,
    fraction_removed: float,
    elasticity: float,
) -> float:
    """Fractional price gain from a corner (shocked price over reference minus one)."""
    effective = effective_supply(supply_0, fraction_removed)
    shocked = shocked_equilibrium_price(reference_price, supply_0, effective, elasticity)
    return shocked / reference_price - 1.0


def simulate_corner(
    reference_price: float,
    supply_0: float,
    fraction_removed: float,
    elasticity: float,
    adjustment: float = 0.4,
    steps: int = 40,
) -> CornerResult:
    """Simulate the tatonnement price trajectory of a gold-market corner.

    Args:
        reference_price: Pre-shock clearing price (positive).
        supply_0: Pre-shock floatable supply (positive).
        fraction_removed: Fraction sterilized / removed, in ``[0, 1)``.
        elasticity: Price elasticity of demand (positive).
        adjustment: Tatonnement coefficient ``lambda`` in ``(0, 2)``.
        steps: Number of adjustment steps (non-negative int).

    Returns:
        A :class:`CornerResult` with the shocked price, fractional gain, and
        the deterministic per-step trajectory (``steps + 1`` points, starting
        at the reference price).
    """
    _positive(reference_price, "reference_price")
    _positive(supply_0, "supply_0")
    effective = effective_supply(supply_0, fraction_removed)
    shocked = shocked_equilibrium_price(reference_price, supply_0, effective, elasticity)
    if isinstance(adjustment, bool) or not isinstance(adjustment, (int, float)):
        raise TypeError("adjustment must be a number")
    if not (0.0 < adjustment < 2.0):
        raise ValueError("adjustment must be in (0, 2)")
    if isinstance(steps, bool) or not isinstance(steps, int):
        raise TypeError("steps must be an int")
    if steps < 0:
        raise ValueError("steps must be non-negative")

    price = float(reference_price)
    trajectory: list[float] = [price]
    for _ in range(steps):
        price = price + adjustment * (shocked - price)
        trajectory.append(price)
    return CornerResult(
        shocked_price=float(shocked),
        gain=float(shocked / reference_price - 1.0),
        trajectory=tuple(trajectory),
    )


def corner_valuation(reference_price: float, quantity_seized: float) -> float:
    """Nominal value of a seized stockpile at the reference price.

    Args:
        reference_price: Price per unit of gold (positive).
        quantity_seized: Amount of gold cornered (non-negative).

    Returns:
        ``reference_price * quantity_seized``.
    """
    _positive(reference_price, "reference_price")
    _positive(quantity_seized, "quantity_seized", strict=False)
    return reference_price * quantity_seized


class _MarketModel(TypedDict):
    """Typed shape of the GRAND SLAM reference market intel."""

    reference_price: float
    supply_0: float
    fraction_removed: float
    elasticity: float
    adjustment: float
    steps: int


#: Reference intel used by the GRAND SLAM mission provider (pure constants).
REFERENCE_MODEL: _MarketModel = {
    "reference_price": 1850.0,  # USD per troy ounce (reference clearing price)
    "supply_0": 100.0,  # normalized floatable-supply index
    "fraction_removed": 0.30,  # Operation Grand Slam sterilizes 30% of float
    "elasticity": 1.25,
    "adjustment": 0.4,
    "steps": 40,
}
