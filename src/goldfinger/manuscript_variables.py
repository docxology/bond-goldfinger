"""Manuscript variable hydration for the goldfinger manuscript.

Reads ``manuscript/config.yaml`` for identity / publication metadata and
combines it with the deterministic reference outputs of the GRAND SLAM concept
modules (market corner, vault defense, laser physics) into a
``{{TOKEN}} → value`` mapping. Scripts render this into prose so no metric is
hand-authored.

Determinism: ``generate_variables`` accepts a ``now`` override (the script
passes ``None`` and the wall clock is used only for the generation timestamp,
which is expected to vary run to run).
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from goldfinger import __version__
from goldfinger.laser_physics import REFERENCE_PHYSICS, burn_through_time, laser_threat_severity
from goldfinger.laser_thermal import (
    REFERENCE_BEAM,
    effective_burn_range,
    melt_time_at_distance,
    rayleigh_range,
)
from goldfinger.market_attack import REFERENCE_MODEL, price_gain, simulate_corner
from goldfinger.reserve_attack import (
    REFERENCE_ATTACK,
    attack_time,
    floating_depreciation,
    reserve_floor_time,
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
    edge_criticality,
    harden_network,
    minimum_effort_path,
)

__all__ = ["GOLDFINGER_TOKENS", "generate_variables", "load_mission_config"]


def load_mission_config(project_root: Path) -> dict[str, Any]:
    """Load ``manuscript/config.yaml`` from ``project_root`` (must exist)."""
    config_path = project_root / "manuscript" / "config.yaml"
    if not config_path.is_file():
        raise FileNotFoundError(f"manuscript config not found: {config_path}")
    with config_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError("manuscript/config.yaml must contain a YAML mapping")
    return data


def _fmt(value: float, digits: int = 2) -> str:
    return f"{value:.{digits}f}"


def generate_variables(
    require_analysis_outputs: bool = True,
    project_root: Path | None = None,
    now: datetime | None = None,
) -> dict[str, str]:
    """Compute the full ``{{TOKEN}} → value`` map for the manuscript.

    Args:
        require_analysis_outputs: Kept for signature parity; GRAND SLAM computes
            its result tokens deterministically from the domain core, so those
            values are always available.
        project_root: Project root; defaults to three levels above this module
            (``src/goldfinger/`` under the package root).
        now: Timestamp override for the ``GENERATION_TIMESTAMP`` token
            (defaults to the current UTC time).
    """
    root = project_root or Path(__file__).resolve().parents[2]
    config = load_mission_config(root)

    paper = config.get("paper", {})
    if not isinstance(paper, dict):
        paper = {}
    author = (config.get("authors") or [{}])[0]
    if not isinstance(author, dict):
        author = {}
    keywords: list[str] = config.get("keywords") or []
    if not isinstance(keywords, list):
        keywords = []

    # Deterministic computed result tokens from the concept cores.
    model = REFERENCE_MODEL
    result = simulate_corner(
        model["reference_price"],
        model["supply_0"],
        model["fraction_removed"],
        model["elasticity"],
        model["adjustment"],
        model["steps"],
    )
    gain = price_gain(
        model["reference_price"],
        model["supply_0"],
        model["fraction_removed"],
        model["elasticity"],
    )
    ratings = REFERENCE_RATINGS
    score = layered_security_score(ratings)
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
    weakest = weakest_layer(ratings)

    # Deterministic intel from the phase-4 deepened modules.
    a = REFERENCE_ATTACK
    attack = attack_time(
        a["parity"], a["foreign_rate"], a["interest_elasticity"], a["credit_0"], a["growth"]
    )
    floor = reserve_floor_time(
        a["parity"], a["foreign_rate"], a["interest_elasticity"], a["credit_0"], a["growth"]
    )
    depreciation = floating_depreciation(
        a["parity"], a["foreign_rate"], a["interest_elasticity"], a["credit_0"], a["growth"]
    )

    net_effort, weak_path = minimum_effort_path(REFERENCE_GRAPH, "perimeter", "gold_chamber")
    hardening = harden_network(
        REFERENCE_GRAPH, "perimeter", "gold_chamber", budget=10, gain_per_unit=0.5
    )
    critical_count = len(edge_criticality(REFERENCE_GRAPH, "perimeter", "gold_chamber"))

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
    focus_melt = melt_time_at_distance(
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
    z_r = rayleigh_range(b["waist"], b["wavelength"])

    stamp = (now or datetime.now(timezone.utc)).strftime("%Y-%m-%d %H:%M:%S UTC")
    version = str(paper.get("version", __version__))

    variables: dict[str, str] = {
        "GOLDFINGER_TITLE": str(paper.get("title", "Goldfinger: GRAND SLAM")),
        "GOLDFINGER_SUBTITLE": str(paper.get("subtitle", "")),
        "GOLDFINGER_CODENAME": "GRAND SLAM",
        "GOLDFINGER_FILM": "Goldfinger (1964)",
        "GOLDFINGER_VERSION": version,
        "GOLDFINGER_AUTHOR": str(author.get("name", "Daniel Ari Friedman")),
        "GOLDFINGER_ORCID": str(author.get("orcid", "")),
        "GOLDFINGER_AFFILIATION": str(author.get("affiliation", "Active Inference Institute")),
        "GOLDFINGER_KEYWORDS": ", ".join(keywords),
        # Market corner
        "MARKET_REFERENCE_PRICE": _fmt(model["reference_price"]),
        "MARKET_FRACTION_REMOVED": _fmt(model["fraction_removed"] * 100, 0),
        "MARKET_ELASTICITY": _fmt(model["elasticity"], 2),
        "MARKET_SHOCKED_PRICE": _fmt(result.shocked_price),
        "MARKET_PRICE_GAIN_PCT": _fmt(gain * 100, 1),
        "MARKET_CONVERGED": "true" if result.trajectory[-1] == result.shocked_price else "false",
        # Reserve attack (macro)
        "RESERVE_ATTACK_TIME": _fmt(attack, 2),
        "RESERVE_FLOOR_TIME": _fmt(floor, 2),
        "RESERVE_ATTACK_SUDDENNESS": _fmt(floor - attack, 2),
        "RESERVE_DEPRECIATION_PCT": _fmt(depreciation * 100, 0),
        # Vault layered defense
        "VAULT_SCORE": _fmt(score, 3),
        "VAULT_VERDICT": vault_security_verdict(score),
        "VAULT_PENETRATION_PCT": _fmt(penetration_probability(ratings) * 100, 1),
        "VAULT_WEAKEST": weakest,
        # Vault network penetration / hardening
        "VAULT_MIN_EFFORT": _fmt(net_effort, 2),
        "VAULT_HARDENED_EFFORT": _fmt(hardening["min_effort_after"], 2),
        "VAULT_EFFORT_RAISED": _fmt(hardening["effort_raised"], 2),
        "VAULT_WEAK_PATH_EDGES": str(len(weak_path) - 1),
        "VAULT_CRITICAL_EDGES": str(critical_count),
        # Laser physics
        "LASER_POWER_W": _fmt(phys["power"], 0),
        "LASER_BURN_THROUGH_S": _fmt(t_burn, 2),
        "LASER_SEVERITY": laser_threat_severity(phys["power"], 1000.0),
        "LASER_THICKNESS_MM": _fmt(phys["thickness"] * 1000, 0),
        # Laser thermal (beam + heat conduction)
        "LASER_EFFECTIVE_RANGE_M": _fmt(burn_range, 1),
        "LASER_FOCUS_MELT_S": _fmt(focus_melt, 4),
        "LASER_RAYLEIGH_RANGE_M": _fmt(z_r, 2),
        "LASER_WAIST_MM": _fmt(b["waist"] * 1000.0, 2),
        "LASER_THREAT_WINDOW_S": _fmt(b["threat_window"], 1),
        # Environment / reproducibility
        "GENERATION_TIMESTAMP": stamp,
    }
    variables["GOLDFINGER_VERSION_HASH"] = _sha8(json.dumps(variables, sort_keys=True))
    return variables


def _sha8(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:8]


#: Manuscript identity and result tokens (used by tests and docs).
GOLDFINGER_TOKENS: tuple[str, ...] = (
    "GOLDFINGER_TITLE",
    "GOLDFINGER_SUBTITLE",
    "GOLDFINGER_CODENAME",
    "GOLDFINGER_FILM",
    "GOLDFINGER_VERSION",
    "GOLDFINGER_AUTHOR",
    "GOLDFINGER_ORCID",
    "GOLDFINGER_AFFILIATION",
    "GOLDFINGER_KEYWORDS",
    "MARKET_REFERENCE_PRICE",
    "MARKET_FRACTION_REMOVED",
    "MARKET_ELASTICITY",
    "MARKET_SHOCKED_PRICE",
    "MARKET_PRICE_GAIN_PCT",
    "MARKET_CONVERGED",
    "RESERVE_ATTACK_TIME",
    "RESERVE_FLOOR_TIME",
    "RESERVE_ATTACK_SUDDENNESS",
    "RESERVE_DEPRECIATION_PCT",
    "VAULT_SCORE",
    "VAULT_VERDICT",
    "VAULT_PENETRATION_PCT",
    "VAULT_WEAKEST",
    "VAULT_MIN_EFFORT",
    "VAULT_HARDENED_EFFORT",
    "VAULT_EFFORT_RAISED",
    "VAULT_WEAK_PATH_EDGES",
    "VAULT_CRITICAL_EDGES",
    "LASER_POWER_W",
    "LASER_BURN_THROUGH_S",
    "LASER_SEVERITY",
    "LASER_THICKNESS_MM",
    "LASER_EFFECTIVE_RANGE_M",
    "LASER_FOCUS_MELT_S",
    "LASER_RAYLEIGH_RANGE_M",
    "LASER_WAIST_MM",
    "LASER_THREAT_WINDOW_S",
    "GENERATION_TIMESTAMP",
    "GOLDFINGER_VERSION_HASH",
)
