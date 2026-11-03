"""GRAND SLAM mission provider — the BOND-API adapter for goldfinger.

This module is the *thin adapter* between the pure domain core (six modules:
``market_attack``, ``reserve_attack``, ``vault_security``,
``vault_threat_network``, ``laser_physics``, ``laser_thermal``) and the frozen
BOND-API mission protocol. It implements the five lifecycle stages (brief /
recon / plan / execute / debrief), registers the mission's gadgets with the
``bond_api.GadgetRegistry``, and returns a fully-determined
:class:`MissionOutcome` with provenance.

Discovery contract (see ``bond_api.discovery``): the module is importable at
top level as ``goldfinger.mission`` exposing a ``MissionProvider`` class whose
``film`` matches the slug, so the orchestrator can find it. The public adapter
shape is stable across phases — only the mission *internals* deepen.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from bond_api.capabilities import derive_provenance
from bond_api.protocol import (
    Asset,
    Constraint,
    Debrief,
    Finding,
    MissionBrief,
    MissionOutcome,
    MissionPlan,
    ReconReport,
    ReconRequest,
    Step,
)
from bond_api.registry import GadgetRegistry

from goldfinger import (
    LASER_SEVERITY_THRESHOLD_W,
    LASER_STANDOFF_RANGE_M,
    MISSION_SEED,
)
from goldfinger.laser_physics import (
    REFERENCE_PHYSICS,
    burn_through_time,
    laser_threat_severity,
)
from goldfinger.laser_thermal import REFERENCE_BEAM, effective_burn_range, melt_time_at_distance
from goldfinger.market_attack import (
    CONVERGENCE_TOLERANCE,
    REFERENCE_MODEL,
    convergence_residual,
    has_converged,
    price_gain,
    simulate_corner,
)
from goldfinger.reserve_attack import (
    REFERENCE_ATTACK,
    attack_time,
    floating_depreciation,
    reserve_floor_time,
    reserve_level,
    shadow_rate,
)
from goldfinger.vault_security import (
    REFERENCE_RATINGS,
    layered_security_score,
    penetration_probability,
    vault_security_verdict,
    weakest_layer,
)
from goldfinger.vault_threat_network import (
    REFERENCE_GRAPH,
    REFERENCE_HARDENING,
    REFERENCE_TARGET,
    edge_criticality,
    harden_network,
    minimum_effort_path,
)

__all__ = ["MissionProvider", "build_provider", "register_market_gadgets"]

#: Fixed deterministic RNG seed (this mission performs no random draws).
#: Sourced from the package constant so provenance and the manuscript's
#: ``GOLDFINGER_SEED`` token cannot disagree.
_SEED = MISSION_SEED
#: Package version baked into provenance.
_SUBPACKAGE_VERSION = "goldfinger.mission/0.2.0"


#: Reference intel actually consumed by :meth:`MissionProvider.execute`, in a
#: fixed order, so the provenance ``input_hash`` is a real fingerprint of the
#: inputs rather than a hand-maintained literal. ``derive_provenance`` hashes
#: these parts (JSON-canonical) into the provenance ``input_hash``.
_PROVENANCE_INPUT_PARTS: tuple[Any, ...] = (
    REFERENCE_MODEL,
    REFERENCE_ATTACK,
    REFERENCE_RATINGS,
    REFERENCE_GRAPH,
    REFERENCE_HARDENING,
    REFERENCE_TARGET,
    REFERENCE_PHYSICS,
    REFERENCE_BEAM,
)


def _provenance_inputs() -> tuple[Any, ...]:
    """Return the exact reference-intel parts hashed into provenance.

    Every value here is one the six ``_*_intel()`` helpers read in
    :meth:`MissionProvider.execute`. Two runs with unchanged constants produce
    the same parts and therefore the same ``input_hash``; editing any one
    constant changes the hash, so an auditor comparing two provenance records
    can see at a glance whether the mission's inputs moved.
    """
    return _PROVENANCE_INPUT_PARTS


def persist_grand_slam_record(
    outcome: MissionOutcome,
    path: str | Path,
) -> Path:
    """Write a deterministic GRAND SLAM mission record readable by bond-utilities.

    Delegates to ``bond_utilities.mission_io.record_provenance_outcome`` so
    the outcome survives as a schema-validated, provenance-verified record
    that the fleet's ``verify_provenance`` / ``load_records`` can read back.
    Determinism: the input payload is the same reference intel that produced
    the ``input_hash`` (via :func:`_provenance_inputs`), the seed is the
    package's fixed mission seed, and ``started_at`` is pinned to a committed
    value rather than a wall clock — ``record_provenance_outcome``'s default
    ``started_at`` (``datetime.now``) is never taken, so the persisted record
    is byte-identical on every run. The concept core never sees this I/O;
    only this adapter does.
    """
    from bond_utilities.mission_io import record_provenance_outcome

    input_payload = {"reference_intel": _provenance_inputs()}
    record_provenance_outcome(
        mission_id="goldfinger-grand-slam",
        seed=outcome.provenance.seed,
        version=outcome.provenance.package_version,
        input_payload=input_payload,
        outcome={"results": outcome.results},
        path=path,
        codename="GRAND SLAM",
        started_at="committed-tree",
    )
    return Path(path)


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
        "convergence_residual": convergence_residual(result),
        "converged": has_converged(result, CONVERGENCE_TOLERANCE),
    }


def _reserve_intel() -> dict[str, Any]:
    """Compute the deterministic speculative-attack headline numbers."""
    a = REFERENCE_ATTACK
    floor = reserve_floor_time(
        a["parity"], a["foreign_rate"], a["interest_elasticity"], a["credit_0"], a["growth"]
    )
    attack = attack_time(
        a["parity"], a["foreign_rate"], a["interest_elasticity"], a["credit_0"], a["growth"]
    )
    return {
        "attack_time": attack,
        "reserve_floor_time": floor,
        "attack_suddenness": floor - attack,  # the model's headline: attack precedes gradual drain
        "initial_reserves": reserve_level(
            0.0,
            a["parity"],
            a["foreign_rate"],
            a["interest_elasticity"],
            a["credit_0"],
            a["growth"],
        ),
        "shadow_at_attack": shadow_rate(
            attack,
            a["parity"],
            a["foreign_rate"],
            a["interest_elasticity"],
            a["credit_0"],
            a["growth"],
        ),
        "floating_depreciation": floating_depreciation(
            a["parity"], a["foreign_rate"], a["interest_elasticity"], a["credit_0"], a["growth"]
        ),
    }


def _vault_intel() -> dict[str, Any]:
    """Compute the deterministic layered vault-defense headline numbers."""
    ratings = REFERENCE_RATINGS
    score = layered_security_score(ratings)
    return {
        "layered_score": score,
        "verdict": vault_security_verdict(score),
        "penetration_probability": penetration_probability(ratings),
        "weakest_layer": weakest_layer(ratings),
    }


def _vault_net_intel() -> dict[str, Any]:
    """Compute the deterministic network penetration / hardening headline numbers."""
    source, target = REFERENCE_TARGET
    effort, path = minimum_effort_path(REFERENCE_GRAPH, source, target)
    hardening = harden_network(
        REFERENCE_GRAPH,
        source,
        target,
        budget=REFERENCE_HARDENING["budget"],
        gain_per_unit=REFERENCE_HARDENING["gain_per_unit"],
    )
    critical = edge_criticality(REFERENCE_GRAPH, source, target)
    return {
        "min_effort": effort,
        "weak_path": path,
        "weak_path_edges": len(path) - 1,
        "hardened_effort": hardening["min_effort_after"],
        "effort_raised": hardening["effort_raised"],
        "critical_edge_count": len(critical),
        "hardening_allocation": hardening["allocation"],
    }


def _laser_intel() -> dict[str, Any]:
    """Compute the deterministic laser burn-through headline numbers."""
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
        "severity": laser_threat_severity(phys["power"], LASER_SEVERITY_THRESHOLD_W),
        "severity_threshold_w": LASER_SEVERITY_THRESHOLD_W,
        "power_w": phys["power"],
    }


def _laser_thermal_intel() -> dict[str, Any]:
    """Compute the deterministic Gaussian-beam / heat-conduction headline numbers."""
    b = REFERENCE_BEAM
    burn_range = effective_burn_range(
        b["power"],
        b["waist"],
        b["wavelength"],
        b["absorptivity"],
        b["conductivity"],
        b["density"],
        b["specific_heat"],
        b["melt_temp"],
        b["ambient"],
        b["threat_window"],
    )
    range_m = burn_range.range_m
    burns_at_focus = burn_range.burns_at_focus
    t_focus = melt_time_at_distance(
        b["power"],
        b["waist"],
        b["wavelength"],
        0.0,
        b["absorptivity"],
        b["conductivity"],
        b["density"],
        b["specific_heat"],
        b["melt_temp"],
        b["ambient"],
    )
    return {
        "effective_burn_range_m": range_m,
        "burns_at_focus": burns_at_focus,
        "surface_melt_time_at_focus_s": t_focus,
        "threat_window_s": b["threat_window"],
        "waist_mm": b["waist"] * 1000.0,
        "type": "serious" if range_m >= LASER_STANDOFF_RANGE_M else "short-range",
    }


def register_market_gadgets(registry: GadgetRegistry = GADGETS) -> None:
    """Register the mission's gadgets (concept callables) with a registry.

    Registers the six concept tools — ``market_corner``, ``reserve_attack``,
    ``vault_defense``, ``vault_hardening``, ``laser_threat``, and
    ``laser_thermal`` — exposing the domain functions to the BOND suite.
    Idempotent: re-registration merges/replaces in place.
    """
    registry.register(
        "goldfinger",
        {
            "market_corner": price_gain,
            "reserve_attack": attack_time,
            "vault_defense": layered_security_score,
            "vault_hardening": harden_network,
            "laser_threat": burn_through_time,
            "laser_thermal": effective_burn_range,
        },
    )


class MissionProvider:  # noqa: N801 — class name fixed by the discovery contract
    """Deterministic GRAND SLAM mission implementing the BOND-API protocol."""

    film = "goldfinger"

    def __init__(self) -> None:
        # Bind gadgets at construction so discovery yields a ready provider.
        register_market_gadgets(GADGETS)

    def brief(self) -> MissionBrief:
        """Declare the GRAND SLAM mission: corner the gold market, weaponise the
        peg, assess and neutralise the vault and its laser threat."""
        return MissionBrief(
            film=self.film,
            codename="GRAND SLAM",
            objectives=(
                "corner the gold market via a controlled supply shock",
                "weaponise the gold peg via a speculative reserve attack",
                "assess Fort Knox-style layered and network vault defense",
                "quantify the laser burn-through and thermal engagement threat",
            ),
            assets=(
                Asset(kind="model", name="market_corner", payload=REFERENCE_MODEL),
                Asset(kind="model", name="reserve_attack", payload=REFERENCE_ATTACK),
                Asset(kind="model", name="vault_defense", payload=dict(REFERENCE_RATINGS)),
                Asset(kind="model", name="vault_network", payload=REFERENCE_GRAPH),
                Asset(kind="model", name="laser_threat", payload=REFERENCE_PHYSICS),
                Asset(kind="model", name="laser_thermal", payload=REFERENCE_BEAM),
            ),
            constraints=(
                Constraint(kind="determinism", detail="no random draws, no external calls"),
                Constraint(
                    kind="location",
                    detail="path-scoped commits inside github.com/docxology/bond-goldfinger",
                ),
            ),
        )

    def recon(self, request: ReconRequest) -> ReconReport:
        """Survey the request, the six models, and the determinism constraint."""
        return ReconReport(
            findings=(
                Finding(label="goal", detail=request.goal),
                Finding(label="models", detail="six GRAND SLAM concept models"),
                Finding(label="determinism", detail="fixed seed, zero wall-clock dependence"),
                Finding(label="scope", detail="goldfinger package only"),
            )
        )

    def plan(self, brief: MissionBrief) -> MissionPlan:
        """Plan the seven deterministic compute steps."""
        return MissionPlan(
            steps=(
                Step(
                    name="corner",
                    action="simulate_market_corner",
                    params={"model": brief.assets[0].name},
                ),
                Step(
                    name="reserve",
                    action="simulate_reserve_attack",
                    params={"model": brief.assets[1].name},
                ),
                Step(
                    name="vault",
                    action="assess_vault_defense",
                    params={"model": brief.assets[2].name},
                ),
                Step(
                    name="vault_network",
                    action="assess_vault_network",
                    params={"model": brief.assets[3].name},
                ),
                Step(
                    name="laser",
                    action="assess_laser_threat",
                    params={"model": brief.assets[4].name},
                ),
                Step(
                    name="laser_thermal",
                    action="assess_laser_thermal",
                    params={"model": brief.assets[5].name},
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
        reserve = _reserve_intel()
        vault = _vault_intel()
        vault_net = _vault_net_intel()
        laser = _laser_intel()
        laser_thermal = _laser_thermal_intel()
        results: dict[str, Any] = {
            "steps_completed": len(plan.steps),
            "corner": corner,
            "reserve": reserve,
            "vault": vault,
            "vault_network": vault_net,
            "laser": laser,
            "laser_thermal": laser_thermal,
            "all_converged": corner["converged"],
        }
        return MissionOutcome(
            success=True,
            results=results,
            provenance=derive_provenance(
                package_version=_SUBPACKAGE_VERSION,
                seed=_SEED,
                inputs=_provenance_inputs(),
                wall_time_s=0.0,
            ),
        )

    def debrief(self, outcome: MissionOutcome) -> Debrief:
        """Summarize the mission and record the standing lessons learned."""
        return Debrief(
            outcome=outcome,
            lessons=(
                "a corner raises price by (S0/S_eff)^(1/eta) at constant elasticity",
                "a gold peg is drained by credit growth; the attack lands at shadow-rate parity",
                "network hardening raises the intruder's minimum effort on the weak path",
                "defocusing shortens effective burn range; surface melting follows Carslaw-Jaeger",
                "six pure deterministic models keep the mission reproducible local-first",
            ),
        )


def build_provider() -> MissionProvider:
    """Construct a configured :class:`MissionProvider` instance."""
    return MissionProvider()
