"""Manuscript variable hydration for the goldfinger manuscript.

Reads ``manuscript/config.yaml`` for identity / publication metadata and
combines it with the deterministic reference outputs of the six GRAND SLAM
concept modules (market corner, reserve attack, layered vault defense, vault
threat network, laser physics, laser thermal engagement) into a
``{{TOKEN}} → value`` mapping. Scripts render this into prose so no metric is
hand-authored.

Three *structural* tokens are derived rather than declared:
``GOLDFINGER_MODULE_COUNT`` counts the concept modules on disk,
``GOLDFINGER_FIGURE_COUNT`` counts the exported figure renderers, and
``GOLDFINGER_TOKEN_COUNT`` is the length of :data:`GOLDFINGER_TOKENS`. This
keeps the manuscript's own self-description from drifting when modules,
figures, or tokens are added.

Determinism: ``generate_variables`` accepts a ``now`` override (the script
passes ``None`` and the wall clock is used only for the generation timestamp,
which is expected to vary run to run).
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from goldfinger import LASER_SEVERITY_THRESHOLD_W, MISSION_SEED, __version__
from goldfinger.figures import FIGURE_RENDERERS
from goldfinger.laser_physics import REFERENCE_PHYSICS, burn_through_time, laser_threat_severity
from goldfinger.laser_thermal import (
    REFERENCE_BEAM,
    effective_burn_range,
    melt_time_at_distance,
    rayleigh_range,
)
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

__all__ = [
    "GOLDFINGER_TOKENS",
    "concept_module_names",
    "generate_variables",
    "load_mission_config",
    "render_counts_markdown",
]

#: Package modules that are *not* concept models (adapter / plumbing).
_NON_CONCEPT_MODULES = frozenset({"__init__", "mission", "manuscript_variables"})


def concept_module_names() -> tuple[str, ...]:
    """Names of the pure concept modules shipped in ``src/goldfinger/``.

    Derived from the package directory rather than a hand-maintained list, so
    the manuscript's module count cannot drift from what is actually on disk.
    The mission adapter and the manuscript plumbing are excluded.
    """
    package_dir = Path(__file__).resolve().parent
    return tuple(
        sorted(
            path.stem for path in package_dir.glob("*.py") if path.stem not in _NON_CONCEPT_MODULES
        )
    )


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

    source, target = REFERENCE_TARGET
    net_effort, weak_path = minimum_effort_path(REFERENCE_GRAPH, source, target)
    hardening = harden_network(
        REFERENCE_GRAPH,
        source,
        target,
        budget=REFERENCE_HARDENING["budget"],
        gain_per_unit=REFERENCE_HARDENING["gain_per_unit"],
    )
    critical_count = len(edge_criticality(REFERENCE_GRAPH, source, target))

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
        # Structural self-description (derived, never hand-counted)
        "GOLDFINGER_MODULE_COUNT": str(len(concept_module_names())),
        "GOLDFINGER_FIGURE_COUNT": str(len(FIGURE_RENDERERS)),
        "GOLDFINGER_TOKEN_COUNT": str(len(GOLDFINGER_TOKENS)),
        # Market corner — inputs
        "MARKET_REFERENCE_PRICE": _fmt(model["reference_price"]),
        "MARKET_FRACTION_REMOVED": _fmt(model["fraction_removed"] * 100, 0),
        "MARKET_ELASTICITY": _fmt(model["elasticity"], 2),
        "MARKET_SUPPLY_INDEX": _fmt(model["supply_0"], 1),
        "MARKET_ADJUSTMENT": _fmt(model["adjustment"], 2),
        "MARKET_STEPS": str(model["steps"]),
        # Market corner — results
        "MARKET_SHOCKED_PRICE": _fmt(result.shocked_price),
        "MARKET_PRICE_GAIN_PCT": _fmt(gain * 100, 1),
        "MARKET_CONVERGED": "true" if has_converged(result, CONVERGENCE_TOLERANCE) else "false",
        "MARKET_CONVERGENCE_RESIDUAL": f"{convergence_residual(result):.2e}",
        "MARKET_CONVERGENCE_TOLERANCE": f"{CONVERGENCE_TOLERANCE:.0e}",
        # Reserve attack (macro) — inputs
        "RESERVE_PARITY": _fmt(a["parity"], 2),
        "RESERVE_FOREIGN_RATE": _fmt(a["foreign_rate"], 2),
        "RESERVE_ALPHA": _fmt(a["interest_elasticity"], 1),
        "RESERVE_CREDIT_0": _fmt(a["credit_0"], 2),
        "RESERVE_GROWTH": _fmt(a["growth"], 2),
        # Reserve attack (macro) — results
        "RESERVE_ATTACK_TIME": _fmt(attack, 2),
        "RESERVE_FLOOR_TIME": _fmt(floor, 2),
        "RESERVE_ATTACK_SUDDENNESS": _fmt(floor - attack, 2),
        "RESERVE_DEPRECIATION_PCT": _fmt(depreciation * 100, 0),
        # Vault layered defense
        "VAULT_LAYER_COUNT": str(len(ratings)),
        "VAULT_SCORE": _fmt(score, 3),
        "VAULT_VERDICT": vault_security_verdict(score),
        "VAULT_PENETRATION_PCT": f"{penetration_probability(ratings) * 100:.4g}",
        "VAULT_WEAKEST": weakest,
        # Vault network penetration / hardening
        "VAULT_ZONE_COUNT": str(len(REFERENCE_GRAPH)),
        "VAULT_HARDENING_BUDGET": str(hardening["budget"]),
        "VAULT_GAIN_PER_UNIT": _fmt(hardening["gain_per_unit"], 2),
        "VAULT_MIN_EFFORT": _fmt(net_effort, 2),
        "VAULT_HARDENED_EFFORT": _fmt(hardening["min_effort_after"], 2),
        "VAULT_EFFORT_RAISED": _fmt(hardening["effort_raised"], 2),
        "VAULT_WEAK_PATH_EDGES": str(len(weak_path) - 1),
        "VAULT_CRITICAL_EDGES": str(critical_count),
        # Laser physics — inputs
        "LASER_POWER_W": _fmt(phys["power"], 0),
        "LASER_SPOT_AREA_M2": f"{phys['area']:.1e}",
        "LASER_DENSITY_KGM3": _fmt(phys["density"], 0),
        "LASER_THICKNESS_MM": _fmt(phys["thickness"] * 1000, 0),
        "LASER_SPECIFIC_HEAT": _fmt(phys["specific_heat"], 0),
        "LASER_DELTA_T_K": _fmt(phys["delta_temperature"], 0),
        "LASER_ABSORPTIVITY": _fmt(phys["absorptivity"], 2),
        # Laser physics — results
        "LASER_BURN_THROUGH_S": _fmt(t_burn, 2),
        "LASER_SEVERITY": laser_threat_severity(phys["power"], LASER_SEVERITY_THRESHOLD_W),
        "LASER_SEVERITY_THRESHOLD_W": _fmt(LASER_SEVERITY_THRESHOLD_W, 0),
        # Laser thermal — inputs
        "LASER_WAIST_MM": _fmt(b["waist"] * 1000.0, 2),
        "LASER_WAVELENGTH_NM": _fmt(b["wavelength"] * 1.0e9, 0),
        "LASER_CONDUCTIVITY": _fmt(b["conductivity"], 0),
        "LASER_MELT_TEMP_K": _fmt(b["melt_temp"], 0),
        "LASER_AMBIENT_K": _fmt(b["ambient"], 0),
        "LASER_THREAT_WINDOW_S": _fmt(b["threat_window"], 1),
        # Laser thermal — results
        "LASER_EFFECTIVE_RANGE_M": _fmt(burn_range, 1),
        "LASER_FOCUS_MELT_S": _fmt(focus_melt, 4),
        "LASER_RAYLEIGH_RANGE_M": _fmt(z_r, 2),
        # Environment / reproducibility
        "GOLDFINGER_SEED": str(MISSION_SEED),
        "GENERATION_TIMESTAMP": stamp,
    }
    variables["GOLDFINGER_VERSION_HASH"] = _sha8(json.dumps(variables, sort_keys=True))
    return variables


def _sha8(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:8]


#: Manuscript identity, input, and result tokens (used by tests and docs).
#:
#: This tuple is the declared token contract:
#: ``tests/test_manuscript_variables.py`` asserts it is exactly equal to the
#: key set of :func:`generate_variables`, and ``GOLDFINGER_TOKEN_COUNT`` is
#: derived from its length, so the manuscript can state its own token count
#: without anyone hand-counting.
GOLDFINGER_TOKENS: tuple[str, ...] = (
    # Identity
    "GOLDFINGER_TITLE",
    "GOLDFINGER_SUBTITLE",
    "GOLDFINGER_CODENAME",
    "GOLDFINGER_FILM",
    "GOLDFINGER_VERSION",
    "GOLDFINGER_AUTHOR",
    "GOLDFINGER_ORCID",
    "GOLDFINGER_AFFILIATION",
    "GOLDFINGER_KEYWORDS",
    # Structural self-description
    "GOLDFINGER_MODULE_COUNT",
    "GOLDFINGER_FIGURE_COUNT",
    "GOLDFINGER_TOKEN_COUNT",
    # Market corner
    "MARKET_REFERENCE_PRICE",
    "MARKET_FRACTION_REMOVED",
    "MARKET_ELASTICITY",
    "MARKET_SUPPLY_INDEX",
    "MARKET_ADJUSTMENT",
    "MARKET_STEPS",
    "MARKET_SHOCKED_PRICE",
    "MARKET_PRICE_GAIN_PCT",
    "MARKET_CONVERGED",
    "MARKET_CONVERGENCE_RESIDUAL",
    "MARKET_CONVERGENCE_TOLERANCE",
    # Reserve attack
    "RESERVE_PARITY",
    "RESERVE_FOREIGN_RATE",
    "RESERVE_ALPHA",
    "RESERVE_CREDIT_0",
    "RESERVE_GROWTH",
    "RESERVE_ATTACK_TIME",
    "RESERVE_FLOOR_TIME",
    "RESERVE_ATTACK_SUDDENNESS",
    "RESERVE_DEPRECIATION_PCT",
    # Vault (layered + network)
    "VAULT_LAYER_COUNT",
    "VAULT_SCORE",
    "VAULT_VERDICT",
    "VAULT_PENETRATION_PCT",
    "VAULT_WEAKEST",
    "VAULT_ZONE_COUNT",
    "VAULT_HARDENING_BUDGET",
    "VAULT_GAIN_PER_UNIT",
    "VAULT_MIN_EFFORT",
    "VAULT_HARDENED_EFFORT",
    "VAULT_EFFORT_RAISED",
    "VAULT_WEAK_PATH_EDGES",
    "VAULT_CRITICAL_EDGES",
    # Laser (scalar + thermal)
    "LASER_POWER_W",
    "LASER_SPOT_AREA_M2",
    "LASER_DENSITY_KGM3",
    "LASER_THICKNESS_MM",
    "LASER_SPECIFIC_HEAT",
    "LASER_DELTA_T_K",
    "LASER_ABSORPTIVITY",
    "LASER_BURN_THROUGH_S",
    "LASER_SEVERITY",
    "LASER_SEVERITY_THRESHOLD_W",
    "LASER_WAIST_MM",
    "LASER_WAVELENGTH_NM",
    "LASER_CONDUCTIVITY",
    "LASER_MELT_TEMP_K",
    "LASER_AMBIENT_K",
    "LASER_THREAT_WINDOW_S",
    "LASER_EFFECTIVE_RANGE_M",
    "LASER_FOCUS_MELT_S",
    "LASER_RAYLEIGH_RANGE_M",
    # Environment / reproducibility
    "GOLDFINGER_SEED",
    "GENERATION_TIMESTAMP",
    "GOLDFINGER_VERSION_HASH",
)


def render_counts_markdown(
    variables: Mapping[str, str],
    tests_collected: int | None = None,
    coverage_percent: float | None = None,
) -> str:
    """Render ``docs/_generated/COUNTS.md`` from a generated token map.

    Structural counts and headline results are read out of ``variables`` — the
    same map the manuscript renders from — so this file cannot disagree with
    the prose.

    ``tests_collected`` and ``coverage_percent`` are *measurements*: they are
    only available after a real gate run, so the caller passes them in. When
    either is omitted the corresponding line states the enforced gate instead
    of inventing a figure, which is the honest fallback for a number nobody
    measured.

    Args:
        variables: Token map from :func:`generate_variables`.
        tests_collected: Test count observed in a real pytest run, if any.
        coverage_percent: Line+branch coverage observed in that run, if any.

    Returns:
        The complete markdown document, ending in a newline.
    """
    missing = sorted(token for token in _COUNTS_TOKENS if token not in variables)
    if missing:
        raise KeyError(f"variables map is missing tokens required by COUNTS.md: {missing}")

    if tests_collected is None:
        tests_line = "- Test suite: gated at **0 failures, 0 skipped** (not measured in this run)."
    else:
        tests_line = f"- Test suite: **{tests_collected} collected**, 0 skipped, 0 failed."
    if coverage_percent is None:
        coverage_line = "- Coverage on `src/goldfinger/`: gate is **>=90%** line+branch."
    else:
        coverage_line = (
            f"- Coverage on `src/goldfinger/` (line + branch): "
            f"**{coverage_percent:.2f}%** (gate: >=90%)."
        )

    modules = ", ".join(f"`{name}`" for name in concept_module_names())
    figures = ", ".join(f"`{name.removeprefix('plot_')}`" for name in FIGURE_RENDERERS)
    return f"""# Live counts — goldfinger (GRAND SLAM)

> Generated by `scripts/z_generate_counts.py` from
> `goldfinger.manuscript_variables.render_counts_markdown`. Do not hand-edit:
> regenerate instead. Never copy these numbers into other prose — cite this
> file or use the manuscript `{{{{TOKEN}}}}`.

{tests_line}
{coverage_line}
- Pure domain modules: **{variables["GOLDFINGER_MODULE_COUNT"]}** ({modules}).
- Manuscript tokens: **{variables["GOLDFINGER_TOKEN_COUNT"]}**.
- Figures: **{variables["GOLDFINGER_FIGURE_COUNT"]}** ({figures}).
- Deterministic seed: **{variables["GOLDFINGER_SEED"]}** (no random draws).

## Result headline values (deterministic, from the pure core)

| Quantity | Token | Value |
|---|---|---|
| Corner price gain | `MARKET_PRICE_GAIN_PCT` | {variables["MARKET_PRICE_GAIN_PCT"]}% |
| Corner convergence residual | `MARKET_CONVERGENCE_RESIDUAL` | \
{variables["MARKET_CONVERGENCE_RESIDUAL"]} |
| Speculative attack time | `RESERVE_ATTACK_TIME` | {variables["RESERVE_ATTACK_TIME"]} |
| Gradual reserve floor | `RESERVE_FLOOR_TIME` | {variables["RESERVE_FLOOR_TIME"]} |
| Post-float depreciation | `RESERVE_DEPRECIATION_PCT` | {variables["RESERVE_DEPRECIATION_PCT"]}% |
| Layered vault score | `VAULT_SCORE` | \
{variables["VAULT_SCORE"]} ({variables["VAULT_VERDICT"]}) |
| Sequential penetration | `VAULT_PENETRATION_PCT` | {variables["VAULT_PENETRATION_PCT"]}% |
| Minimum intrusion effort | `VAULT_MIN_EFFORT` | \
{variables["VAULT_MIN_EFFORT"]} → {variables["VAULT_HARDENED_EFFORT"]} hardened |
| Laser burn-through | `LASER_BURN_THROUGH_S` | {variables["LASER_BURN_THROUGH_S"]} s |
| Laser effective range | `LASER_EFFECTIVE_RANGE_M` | \
{variables["LASER_EFFECTIVE_RANGE_M"]} m (Rayleigh {variables["LASER_RAYLEIGH_RANGE_M"]} m) |
"""


#: Tokens :func:`render_counts_markdown` reads; validated up front so a missing
#: token fails loudly instead of rendering a hole into the generated file.
_COUNTS_TOKENS: tuple[str, ...] = (
    "GOLDFINGER_MODULE_COUNT",
    "GOLDFINGER_TOKEN_COUNT",
    "GOLDFINGER_FIGURE_COUNT",
    "GOLDFINGER_SEED",
    "MARKET_PRICE_GAIN_PCT",
    "MARKET_CONVERGENCE_RESIDUAL",
    "RESERVE_ATTACK_TIME",
    "RESERVE_FLOOR_TIME",
    "RESERVE_DEPRECIATION_PCT",
    "VAULT_SCORE",
    "VAULT_VERDICT",
    "VAULT_PENETRATION_PCT",
    "VAULT_MIN_EFFORT",
    "VAULT_HARDENED_EFFORT",
    "LASER_BURN_THROUGH_S",
    "LASER_EFFECTIVE_RANGE_M",
    "LASER_RAYLEIGH_RANGE_M",
)
