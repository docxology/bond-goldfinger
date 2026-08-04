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
from goldfinger.market_attack import REFERENCE_MODEL, price_gain, simulate_corner
from goldfinger.vault_security import (
    REFERENCE_RATINGS,
    layered_security_score,
    penetration_probability,
    vault_security_verdict,
    weakest_layer,
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
        # Vault defense
        "VAULT_SCORE": _fmt(score, 3),
        "VAULT_VERDICT": vault_security_verdict(score),
        "VAULT_PENETRATION_PCT": _fmt(penetration_probability(ratings) * 100, 1),
        "VAULT_WEAKEST": weakest,
        # Laser physics
        "LASER_POWER_W": _fmt(phys["power"], 0),
        "LASER_BURN_THROUGH_S": _fmt(t_burn, 2),
        "LASER_SEVERITY": laser_threat_severity(phys["power"], 1000.0),
        "LASER_THICKNESS_MM": _fmt(phys["thickness"] * 1000, 0),
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
    "VAULT_SCORE",
    "VAULT_VERDICT",
    "VAULT_PENETRATION_PCT",
    "VAULT_WEAKEST",
    "LASER_POWER_W",
    "LASER_BURN_THROUGH_S",
    "LASER_SEVERITY",
    "LASER_THICKNESS_MM",
    "GENERATION_TIMESTAMP",
    "GOLDFINGER_VERSION_HASH",
)
