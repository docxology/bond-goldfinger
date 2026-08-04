"""Fort Knox-style vault defense assessment (layered security scoring).

The security core of the GRAND SLAM mission. A high-value vault is defended
by concentric layers — perimeter, fence, guard response, vault door,
combination lock, and the gold storage cell itself. This module turns an
assessment of each layer into (1) a composite defense-in-depth score and
(2) a sequential-penetration probability, so a defensive posture can be
reasoned about quantitatively.

Model
-----
* **Layered score** — each layer :math:`i` has a strength rating
  :math:`r_i \\in [0, 1]` and a weight :math:`w_i \\ge 0`. The composite
  score is the weighted average :math:`\\sum_i r_i w_i / \\sum_i w_i`.
* **Penetration probability** — an intruder must defeat layers *in order*.
  If a layer stops the intruder with probability equal to its rating
  (independent layers), the overall chance the vault is breached is

  .. math:: P_{\\text{breach}} = \\prod_i (1 - r_i),

  the product rule for sequential independent barriers (defense in depth).
* **Fortification prioritization** — the marginal gain of raising each layer
  by a fixed delta ranks where the next strengthening dollar should go.

The module is pure (no I/O), deterministic, and infrastructure-free.
"""

from __future__ import annotations

from collections.abc import Mapping

__all__ = [
    "DEFAULT_LAYERS",
    "expected_breach_time",
    "layered_security_score",
    "marginal_improvements",
    "penetration_probability",
    "vault_security_verdict",
    "weakest_layer",
]

#: Canonical Fort Knox-style defensive layers and their relative weights.
#: Stored alphabetically; the *ordinal* order used by the penetration model is
#: :data:`LAYER_ORDER`.
DEFAULT_LAYERS: tuple[str, ...] = (
    "combination_lock",
    "fence",
    "gold_storage",
    "guard_response",
    "perimeter",
    "vault_door",
)

#: The sequence an intruder must traverse to reach the gold.
LAYER_ORDER: tuple[str, ...] = (
    "perimeter",
    "fence",
    "guard_response",
    "vault_door",
    "combination_lock",
    "gold_storage",
)

#: Default relative importance of each layer for the weighted score.
DEFAULT_WEIGHTS: Mapping[str, float] = {
    "perimeter": 1.0,
    "fence": 1.0,
    "guard_response": 1.2,
    "vault_door": 1.5,
    "combination_lock": 1.2,
    "gold_storage": 1.3,
}


def _rating(value: float, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{label} must be a number")
    if not (0.0 <= value <= 1.0):
        raise ValueError(f"{label} must be in [0, 1]")
    return float(value)


def _require_layers(ratings: Mapping[str, float]) -> None:
    if not ratings:
        raise ValueError("ratings must not be empty")


def layered_security_score(
    ratings: Mapping[str, float],
    weights: Mapping[str, float] = DEFAULT_WEIGHTS,
) -> float:
    """Weighted defense-in-depth score in ``[0, 1]``.

    Args:
        ratings: Layer name → strength rating in ``[0, 1]``.
        weights: Layer name → weight (defaults to :data:`DEFAULT_WEIGHTS`).
            Layers present in ``ratings`` but absent from ``weights`` count as
            weight ``1.0``; layers present in ``weights`` but not ``ratings``
            are ignored.

    Returns:
        ``sum(r * w) / sum(w)`` over the layers that have both a rating and a
        weight.
    """
    _require_layers(ratings)
    total_weight = 0.0
    total_score = 0.0
    for name, raw_rating in ratings.items():
        rating = _rating(raw_rating, f"ratings[{name!r}]")
        weight = float(weights.get(name, 1.0))
        total_weight += weight
        total_score += rating * weight
    if total_weight == 0.0:
        raise ValueError("no layer has a positive weight in the given ratings")
    return total_score / total_weight


def penetration_probability(ratings: Mapping[str, float]) -> float:
    """Probability an intruder breaches every ordered layer.

    Layers are traversed in :data:`LAYER_ORDER`; any layer rated outside
    ``[0, 1]`` raises. Returns the product of ``(1 - r_i)``.
    """
    _require_layers(ratings)
    prob = 1.0
    for name in LAYER_ORDER:
        if name not in ratings:
            continue
        rating = _rating(ratings[name], f"ratings[{name!r}]")
        prob *= 1.0 - rating
    return prob


def expected_breach_time(
    ratings: Mapping[str, float],
    per_layer_time: float = 1.0,
) -> float:
    """Expected time an intruder spends before the vault is breached or the
    assault is stopped.

    In the sequential defense model the intruder attempts each layer in
    :data:`LAYER_ORDER`, spending ``per_layer_time`` there. Layer :math:`i`
    stops the intruder with probability :math:`r_i`; otherwise they proceed to
    the next. The chance of *reaching* layer :math:`i` is the product of the
    pass-through probabilities of all earlier layers, so

    .. math:: E[T] = t \\sum_i \\prod_{j < i} (1 - r_j),

    over the rated layers in traversal order (unrated layers are not
    attempted).
    """
    _positive(per_layer_time, "per_layer_time")
    expected = 0.0
    pass_through = 1.0
    for name in LAYER_ORDER:
        if name not in ratings:
            continue
        expected += per_layer_time * pass_through
        pass_through *= 1.0 - _rating(ratings[name], f"ratings[{name!r}]")
    return expected


def _positive(value: float, label: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{label} must be a number")
    if value <= 0:
        raise ValueError(f"{label} must be positive")


def weakest_layer(ratings: Mapping[str, float]) -> str:
    """Name of the lowest-rated layer (ties broken by :data:`LAYER_ORDER`)."""
    _require_layers(ratings)
    weakest: str | None = None
    weakest_rating = 1.0
    for name in LAYER_ORDER:
        if name not in ratings:
            continue
        rating = _rating(ratings[name], f"ratings[{name!r}]")
        if rating < weakest_rating:
            weakest_rating = rating
            weakest = name
    if weakest is None:
        raise ValueError("no rated layers to compare")
    return weakest


def marginal_improvements(
    ratings: Mapping[str, float],
    delta: float = 0.1,
    weights: Mapping[str, float] = DEFAULT_WEIGHTS,
) -> tuple[tuple[str, float], ...]:
    """Rank layers by the composite-score gain from raising each by ``delta``.

    Returns an ordered tuple of ``(layer, gain)`` descending by gain — the
    fortification priority list.
    """
    _require_layers(ratings)
    if isinstance(delta, bool) or not isinstance(delta, (int, float)) or delta <= 0:
        raise ValueError("delta must be a positive number")
    base = layered_security_score(ratings, weights)
    gains: list[tuple[str, float]] = []
    for name, raw in ratings.items():
        rating = _rating(raw, f"ratings[{name!r}]")
        raised = min(1.0, rating + delta)
        trial = dict(ratings)
        trial[name] = raised
        gains.append((name, layered_security_score(trial, weights) - base))
    gains.sort(key=lambda item: item[1], reverse=True)
    return tuple(gains)


def vault_security_verdict(
    score: float,
    high_threshold: float = 0.8,
    medium_threshold: float = 0.5,
) -> str:
    """Classify a composite score into a severity verdict.

    Returns ``"high"``, ``"medium"``, or ``"low"`` security depending on how
    the score compares to the (ordered) thresholds.
    """
    _rating(score, "score")
    if score >= high_threshold:
        return "high"
    if score >= medium_threshold:
        return "medium"
    return "low"


#: Reference intel used by the GRAND SLAM mission provider (pure constants).
REFERENCE_RATINGS: Mapping[str, float] = {
    "perimeter": 0.70,
    "fence": 0.60,
    "guard_response": 0.80,
    "vault_door": 0.90,
    "combination_lock": 0.75,
    "gold_storage": 0.85,
}
