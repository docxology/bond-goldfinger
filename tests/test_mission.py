"""Tests for the goldfinger GRAND SLAM MissionProvider adapter."""

from __future__ import annotations

import pytest

from goldfinger.mission import GADGETS, MissionProvider, build_provider, register_market_gadgets


@pytest.fixture()
def provider() -> MissionProvider:
    return build_provider()


def test_film_identity(provider: MissionProvider) -> None:
    assert provider.film == "goldfinger"


def test_brief_declares_mission(provider: MissionProvider) -> None:
    brief = provider.brief()
    assert brief.codename == "GRAND SLAM"
    assert brief.film == "goldfinger"
    assert len(brief.objectives) == 4
    assert len(brief.assets) == 6
    assert any(c.kind == "determinism" for c in brief.constraints)


def test_recon_returns_findings(provider: MissionProvider) -> None:
    from bond_api.protocol import ReconRequest

    report = provider.recon(ReconRequest(goal="assess target"))
    assert len(report.findings) >= 3
    assert report.findings[0].label == "goal"


def test_plan_has_compute_steps(provider: MissionProvider) -> None:
    plan = provider.plan(provider.brief())
    actions = [step.action for step in plan.steps]
    assert actions == [
        "simulate_market_corner",
        "simulate_reserve_attack",
        "assess_vault_defense",
        "assess_vault_network",
        "assess_laser_threat",
        "assess_laser_thermal",
        "combine_outcome",
    ]


def test_execute_deterministic_outcome(provider: MissionProvider) -> None:
    plan = provider.plan(provider.brief())
    first = provider.execute(plan)
    second = provider.execute(plan)
    assert first.success is True
    assert first.provenance.seed >= 0
    assert first.results == second.results
    assert first.results["steps_completed"] == 7


def test_execute_result_shapes(provider: MissionProvider) -> None:
    plan = provider.plan(provider.brief())
    outcome = provider.execute(plan)
    corner = outcome.results["corner"]
    assert corner["shocked_price"] > corner["trajectory"][0]
    assert corner["price_gain"] > 0.0
    vault = outcome.results["vault"]
    assert vault["verdict"] in {"low", "medium", "high"}
    assert 0.0 <= vault["penetration_probability"] <= 1.0
    laser = outcome.results["laser"]
    assert laser["burn_through_time_s"] > 0.0
    assert laser["severity"] in {"trivial", "serious", "critical"}
    # Phase-4 deepened results are present and non-degenerate.
    reserve = outcome.results["reserve"]
    assert reserve["attack_time"] > 0.0
    assert reserve["attack_suddenness"] > 0.0
    net = outcome.results["vault_network"]
    assert net["min_effort"] > 0.0
    assert net["hardened_effort"] > net["min_effort"]
    thermal = outcome.results["laser_thermal"]
    assert thermal["effective_burn_range_m"] > 0.0


def test_debrief_returns_lessons(provider: MissionProvider) -> None:
    plan = provider.plan(provider.brief())
    debrief = provider.debrief(provider.execute(plan))
    assert len(debrief.lessons) == 5
    assert all(isinstance(lesson, str) and lesson for lesson in debrief.lessons)


def test_gadgets_registered(provider: MissionProvider) -> None:
    assert GADGETS.contains("goldfinger", "market_corner")
    assert GADGETS.contains("goldfinger", "reserve_attack")
    assert GADGETS.contains("goldfinger", "vault_defense")
    assert GADGETS.contains("goldfinger", "vault_hardening")
    assert GADGETS.contains("goldfinger", "laser_threat")
    assert GADGETS.contains("goldfinger", "laser_thermal")


def test_register_market_gadgets_is_idempotent() -> None:
    from bond_api.registry import GadgetRegistry

    registry = GadgetRegistry()
    register_market_gadgets(registry)
    register_market_gadgets(registry)
    assert set(registry.gadgets_for("goldfinger")) == {
        "market_corner",
        "reserve_attack",
        "vault_defense",
        "vault_hardening",
        "laser_threat",
        "laser_thermal",
    }


def test_build_provider_returns_mission_provider() -> None:
    assert isinstance(build_provider(), MissionProvider)
