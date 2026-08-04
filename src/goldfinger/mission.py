"""GRAND SLAM mission provider — the BOND-API adapter for goldfinger.

This module is the *thin adapter* between the pure domain core
(:mod:`goldfinger.market_attack`, :mod:`goldfinger.vault_security`,
:mod:`goldfinger.laser_physics`) and the frozen BOND-API mission protocol. It
implements the five lifecycle stages (brief / recon / plan / execute /
debrief), registers the mission's gadgets with the ``bond_api.GadgetRegistry``,
and returns a fully-determined :class:`MissionOutcome` with provenance.

Discovery contract (see ``bond_api.discovery``): the module is importable at
top level as ``goldfinger.mission`` exposing a ``MissionProvider`` class
whose ``film`` matches the slug, so the orchestrator can find it.
"""

from __future__ import annotations

from typing import Any

from bond_api.protocol import (
    Asset,
    Constraint,
    Debrief,
    Finding,
    MissionBrief,
    MissionOutcome,
    MissionPlan,
    Provenance,
    ReconReport,
    ReconRequest,
    Step,
)
from bond_api.registry import GadgetRegistry

from goldfinger.laser_physics import (
    REFERENCE_PHYSICS,
    burn_through_time,
    laser_threat_severity,
)
from goldfinger.market_attack import REFERENCE_MODEL, price_gain, simulate_corner
from goldfinger.vault_security import (
    REFERENCE_RATINGS,
    layered_security_score,
    penetration_probability,
    vault_security_verdict,
    weakest_layer,
)

__all__ = ["MissionProvider", "build_provider", "register_market_gadgets"]

#: Fixed deterministic RNG seed (this mission performs no random draws).
_SEED = 2026
#: Package version baked into provenance.
_SUBPACKAGE_VERSION = "goldfinger.mission/0.1.0"

#: Gadget registry the mission registers its concept tools into.
GADGETS: GadgetRegistry = GadgetRegistry()


def _corner_intel() -> dict[str, Any]:
    """Compute the deterministic market-corner headline numbers."""
    model = REFERENCE_MODEL
    result = simulate_corner(
        model["reference_price"],
        model["supply_0"],
        model["fraction_removed"],
        model["elasticity"],
        model["adjustment"],
        model["steps"],
    )
    return {
        "fraction_removed": model["fraction_removed"],
        "shocked_price": result.shocked_price,
        "price_gain": result.gain,
        "trajectory": result.trajectory,
    }


def _vault_intel() -> dict[str, Any]:
    """Compute the deterministic vault-defense headline numbers."""
    ratings = REFERENCE_RATINGS
    score = layered_security_score(ratings)
    return {
        "layered_score": score,
        "verdict": vault_security_verdict(score),
        "penetration_probability": penetration_probability(ratings),
        "weakest_layer": weakest_layer(ratings),
    }


def _laser_intel() -> dict[str, Any]:
    """Compute the deterministic laser-threat headline numbers."""
    phys = REFERENCE_PHYSICS
    t_burn = burn_through_time(
        phys["power"],
        phys["area"],
        phys["density"],
        phys["thickness"],
        phys["specific_heat"],
        phys["delta_temperature"],
        phys["absorptivity"],
    )
    return {
        "burn_through_time_s": t_burn,
        "severity": laser_threat_severity(phys["power"], 1000.0),
        "power_w": phys["power"],
    }


def register_market_gadgets(registry: GadgetRegistry = GADGETS) -> None:
    """Register the mission's gadgets (concept callables) with a registry.

    Registers three opaque gadgets — ``market_corner``, ``vault_defense``, and
    ``laser_threat`` — exposing the domain functions to the BOND suite.
    Idempotent: re-registration merges/replaces in place.
    """
    registry.register(
        "goldfinger",
        {
            "market_corner": price_gain,
            "vault_defense": layered_security_score,
            "laser_threat": burn_through_time,
        },
    )


class MissionProvider:  # noqa: N801 — class name fixed by the discovery contract
    """Deterministic GRAND SLAM mission implementing the BOND-API protocol."""

    film = "goldfinger"

    def __init__(self) -> None:
        # Bind gadgets at construction so discovery yields a ready provider.
        register_market_gadgets(GADGETS)

    def brief(self) -> MissionBrief:
        """Declare the GRAND SLAM mission: corner the gold market, assess and
        neutralise the vault and its laser threat."""
        return MissionBrief(
            film=self.film,
            codename="GRAND SLAM",
            objectives=(
                "corner the gold market via a controlled supply shock",
                "assess Fort Knox-style layered vault defense",
                "quantify the laser burn-through threat and its defeat",
            ),
            assets=(
                Asset(kind="model", name="market_corner", payload=REFERENCE_MODEL),
                Asset(kind="model", name="vault_defense", payload=dict(REFERENCE_RATINGS)),
                Asset(kind="model", name="laser_threat", payload=REFERENCE_PHYSICS),
            ),
            constraints=(
                Constraint(kind="determinism", detail="no random draws, no external calls"),
                Constraint(kind="location", detail="local-only working tree; no remote"),
            ),
        )

    def recon(self, request: ReconRequest) -> ReconReport:
        """Survey the request, the three models, and the determinism constraint."""
        return ReconReport(
            findings=(
                Finding(label="goal", detail=request.goal),
                Finding(label="models", detail="market_corner, vault_defense, laser_threat"),
                Finding(label="determinism", detail="fixed seed, zero wall-clock dependence"),
                Finding(label="scope", detail="goldfinger package only"),
            )
        )

    def plan(self, brief: MissionBrief) -> MissionPlan:
        """Plan the four deterministic compute steps."""
        return MissionPlan(
            steps=(
                Step(
                    name="corner",
                    action="simulate_market_corner",
                    params={"model": brief.assets[0].name},
                ),
                Step(
                    name="vault",
                    action="assess_vault_defense",
                    params={"model": brief.assets[1].name},
                ),
                Step(
                    name="laser",
                    action="assess_laser_threat",
                    params={"model": brief.assets[2].name},
                ),
                Step(
                    name="synthesis",
                    action="combine_outcome",
                    params={"objectives": len(brief.objectives)},
                ),
            )
        )

    def execute(self, plan: MissionPlan) -> MissionOutcome:
        """Run the plan's compute steps and return a deterministic outcome."""
        corner = _corner_intel()
        vault = _vault_intel()
        laser = _laser_intel()
        results: dict[str, Any] = {
            "steps_completed": len(plan.steps),
            "corner": corner,
            "vault": vault,
            "laser": laser,
            "all_converged": corner["trajectory"][-1] == corner["shocked_price"],
        }
        return MissionOutcome(
            success=True,
            results=results,
            provenance=Provenance(
                package_version=_SUBPACKAGE_VERSION,
                seed=_SEED,
                input_hash="goldfinger-grand-slam-input-v1",
                wall_time_s=0.0,
            ),
        )

    def debrief(self, outcome: MissionOutcome) -> Debrief:
        """Summarize the mission and record the standing lessons learned."""
        return Debrief(
            outcome=outcome,
            lessons=(
                "a corner raises price by (S0/S_eff)^(1/eta) at constant elasticity",
                "defense-in-depth penetration probability is the product of pass-through rates",
                "burn-through time scales linearly with plate thickness and material heat load",
                "pure deterministic models keep the mission reproducible local-first",
            ),
        )


def build_provider() -> MissionProvider:
    """Construct a configured :class:`MissionProvider` instance."""
    return MissionProvider()
