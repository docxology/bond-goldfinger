"""BOND-API protocol integration tests for the goldfinger provider.

Verifies the film satisfies the frozen contract exactly as bond-api's own
discovery and serialization machinery expects: loadable by slug on ``sys.path``,
runtime-checkable through ``MissionProvider``, fully drivable by ``run_mission``,
and round-trippable through the tagged JSON serializer.
"""

from __future__ import annotations

from pathlib import Path

from bond_api.discovery import load_provider
from bond_api.protocol import MissionProvider, ReconRequest, run_mission
from bond_api.serialization import from_json, to_json

from goldfinger.mission import build_provider

_SRC = Path(__file__).resolve().parents[1] / "src"


def test_discoverable_by_slug_on_sys_path() -> None:
    provider = load_provider("goldfinger", search_paths=[str(_SRC)])
    assert provider.film == "goldfinger"


def test_runtime_checkable_protocol() -> None:
    provider = build_provider()
    assert isinstance(provider, MissionProvider)


def test_full_mission_flow_via_run_mission() -> None:
    provider = build_provider()
    debrief = run_mission(provider, ReconRequest(goal="assess GRAND SLAM target"))
    assert debrief.outcome.success is True
    assert debrief.outcome.results["steps_completed"] == 7
    assert len(debrief.lessons) >= 1


def test_mission_flow_order() -> None:
    # run_mission drives exactly brief -> recon -> plan -> execute -> debrief.
    from goldfinger.mission import build_provider as _build

    provider = _build()
    calls: list[str] = []

    class Recording(MissionProvider):
        film = "goldfinger"

        def brief(self):
            calls.append("brief")
            return provider.brief()

        def recon(self, request):
            calls.append("recon")
            return provider.recon(request)

        def plan(self, brief):
            calls.append("plan")
            return provider.plan(brief)

        def execute(self, plan):
            calls.append("execute")
            return provider.execute(plan)

        def debrief(self, outcome):
            calls.append("debrief")
            return provider.debrief(outcome)

    run_mission(Recording(), ReconRequest(goal="flow"))
    assert calls == ["brief", "recon", "plan", "execute", "debrief"]


def test_outcome_serialization_round_trip() -> None:
    outcome = build_provider().execute(build_provider().plan(build_provider().brief()))
    wire = to_json(outcome)
    rebuilt = from_json(wire)
    assert rebuilt == outcome


def test_discovery_after_gadget_binding() -> None:
    provider = load_provider("goldfinger", search_paths=[str(_SRC)])
    # Construction registers gadgets, so the discovered provider is ready.
    from goldfinger.mission import GADGETS

    assert GADGETS.contains("goldfinger", "market_corner")
    assert isinstance(provider, MissionProvider)


def test_deterministic_provenance() -> None:
    provider = build_provider()
    o1 = provider.execute(provider.plan(provider.brief()))
    o2 = provider.execute(provider.plan(provider.brief()))
    assert o1.provenance.input_hash == o2.provenance.input_hash
    assert o1.provenance.seed == o2.provenance.seed
    # The input hash is a real fingerprint of the reference intel, not a
    # hand-typed literal: it must equal the canonical fingerprint of the parts
    # the execute() helpers actually consume, and a one-value edit to any
    # constant must change it (V1 positive control).
    assert o1.provenance.input_hash != "goldfinger-grand-slam-input-v2"
    assert o1.provenance.input_hash == _fingerprint_of_shipped_intel()


def _shipped_intel_parts():
    from goldfinger.laser_physics import REFERENCE_PHYSICS
    from goldfinger.laser_thermal import REFERENCE_BEAM
    from goldfinger.market_attack import REFERENCE_MODEL
    from goldfinger.reserve_attack import REFERENCE_ATTACK
    from goldfinger.vault_security import REFERENCE_RATINGS
    from goldfinger.vault_threat_network import (
        REFERENCE_GRAPH,
        REFERENCE_HARDENING,
        REFERENCE_TARGET,
    )

    return (
        REFERENCE_MODEL,
        REFERENCE_ATTACK,
        REFERENCE_RATINGS,
        REFERENCE_GRAPH,
        REFERENCE_HARDENING,
        REFERENCE_TARGET,
        REFERENCE_PHYSICS,
        REFERENCE_BEAM,
    )


def _fingerprint_of_shipped_intel() -> str:
    from bond_api.capabilities import fingerprint

    return fingerprint(*_shipped_intel_parts())


def test_input_hash_is_sensitive_to_any_constant_edit() -> None:
    """Positive control for C1: perturbing one constant changes the hash."""
    from bond_api.capabilities import fingerprint

    from goldfinger.market_attack import REFERENCE_MODEL

    perturbed = dict(REFERENCE_MODEL)
    perturbed["elasticity"] = 1.5  # a single one-value change anywhere
    parts = list(_shipped_intel_parts())
    parts[0] = perturbed
    assert fingerprint(*parts) != fingerprint(*_shipped_intel_parts())
