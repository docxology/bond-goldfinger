"""Real-data tests for the goldfinger Fort Knox-style vault defense assessment."""

from __future__ import annotations

import pytest

from goldfinger.vault_security import (
    REFERENCE_RATINGS,
    expected_breach_time,
    layered_security_score,
    marginal_improvements,
    penetration_probability,
    vault_security_verdict,
    weakest_layer,
)


def test_layered_score_weighted_average() -> None:
    # All layers rated 1.0 -> composite 1.0; all 0.5 -> composite 0.5.
    uniform_strong = {name: 1.0 for name in REFERENCE_RATINGS}
    uniform_weak = {name: 0.5 for name in REFERENCE_RATINGS}
    assert layered_security_score(uniform_strong) == pytest.approx(1.0)
    assert layered_security_score(uniform_weak) == pytest.approx(0.5)


def test_layered_score_with_custom_weights() -> None:
    ratings = {"perimeter": 1.0, "fence": 0.0}
    weights = {"perimeter": 3.0, "fence": 1.0}
    assert layered_security_score(ratings, weights) == pytest.approx(0.75)


def test_layered_score_missing_weight_defaults_to_one() -> None:
    # fence absent from weights defaults to weight 1.0.
    ratings = {"perimeter": 1.0, "fence": 0.0}
    assert layered_security_score(ratings) == pytest.approx(0.5)


def test_layered_score_empty_ratings() -> None:
    with pytest.raises(ValueError):
        layered_security_score({})


def test_layered_score_zero_weight_raises() -> None:
    with pytest.raises(ValueError):
        layered_security_score({"perimeter": 0.5}, {"perimeter": 0.0})


def test_layered_score_out_of_range_raises() -> None:
    with pytest.raises(ValueError):
        layered_security_score({"perimeter": 1.5})
    with pytest.raises(TypeError):
        layered_security_score({"perimeter": "high"})


def test_penetration_product_rule() -> None:
    # Two independent layers rated 0.5 -> penetration (0.5)^2.
    assert penetration_probability({"perimeter": 0.5, "fence": 0.5}) == pytest.approx(0.25)
    # Perfect defense stops everything.
    assert penetration_probability({"perimeter": 1.0}) == pytest.approx(0.0)
    # No defense lets everything through.
    assert penetration_probability({"perimeter": 0.0}) == pytest.approx(1.0)


def test_penetration_order_independent() -> None:
    # The product rule is symmetric: order of the dict doesn't matter.
    a = penetration_probability({"perimeter": 0.3, "fence": 0.6, "vault_door": 0.9})
    b = penetration_probability({"vault_door": 0.9, "fence": 0.6, "perimeter": 0.3})
    assert a == pytest.approx(b)


def test_reference_penetration_small() -> None:
    prob = penetration_probability(REFERENCE_RATINGS)
    assert 0.0 <= prob <= 1.0
    assert prob < 0.01  # well-defended vault


def test_expected_breach_time_single_layer() -> None:
    # One perfect layer: intruder spends exactly per_layer_time then is stopped.
    assert expected_breach_time({"perimeter": 1.0}, per_layer_time=2.0) == pytest.approx(2.0)
    # One useless layer: intruder spends the time and passes.
    assert expected_breach_time({"perimeter": 0.0}, per_layer_time=2.0) == pytest.approx(2.0)


def test_expected_breach_time_two_layers() -> None:
    # Layer 1 stops with p=0.5: spends t, then with p=0.5 attempts layer 2 (t).
    assert expected_breach_time(
        {"perimeter": 0.5, "fence": 0.5}, per_layer_time=1.0
    ) == pytest.approx(1.5)


def test_expected_breach_time_invalid() -> None:
    with pytest.raises(ValueError):
        expected_breach_time({"perimeter": 0.5}, per_layer_time=0.0)
    with pytest.raises(TypeError):
        expected_breach_time({"perimeter": 0.5}, per_layer_time="fast")


def test_weakest_layer() -> None:
    assert weakest_layer({"perimeter": 0.9, "fence": 0.4, "vault_door": 0.8}) == "fence"
    assert weakest_layer(REFERENCE_RATINGS) == "fence"
    with pytest.raises(ValueError):
        weakest_layer({})


def test_marginal_improvements_ranks_lowest_layer_first() -> None:
    # Custom weights give the weaker, higher-weighted layer the larger gain.
    weights = {"perimeter": 3.0, "fence": 1.0}
    gains = marginal_improvements({"perimeter": 0.5, "fence": 0.9}, weights=weights)
    assert len(gains) == 2
    assert gains[0][0] == "perimeter"
    assert gains[0][1] > gains[1][1]


def test_marginal_improvements_invalid_delta() -> None:
    with pytest.raises(ValueError):
        marginal_improvements({"perimeter": 0.5}, delta=0.0)


def test_verdict_thresholds() -> None:
    assert vault_security_verdict(0.95) == "high"
    assert vault_security_verdict(0.6) == "medium"
    assert vault_security_verdict(0.1) == "low"
    with pytest.raises(ValueError):
        vault_security_verdict(1.5)


def test_reference_score_deterministic() -> None:
    score = layered_security_score(REFERENCE_RATINGS)
    assert 0.0 <= score <= 1.0
    assert score == layered_security_score(dict(REFERENCE_RATINGS))
