"""Guard-path and cross-module contract tests for the GRAND SLAM package.

Two jobs, both with real computation and no mocking:

1. **Guard paths** — every type/value guard in the pure domain core is driven
   through a real call with a real bad argument, so the error branches are
   proven to fire rather than merely present.
2. **Contracts** — the invariants that let the manuscript describe itself
   without a hand-counted number: the declared token tuple must equal the
   generated key set, the derived structural counts must match what is on
   disk, and the shared constants must be single-sourced (the mission seed the
   provenance records is the seed the manuscript reports).
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

import pytest

import goldfinger
import goldfinger.market_attack
from goldfinger.figures import FIGURE_RENDERERS
from goldfinger.laser_physics import absorbed_power
from goldfinger.laser_thermal import (
    effective_burn_range,
    power_density,
    spot_radius_at_distance,
    thermal_surface_temperature,
)
from goldfinger.manuscript_variables import (
    GOLDFINGER_TOKENS,
    concept_module_names,
    generate_variables,
    load_mission_config,
    render_counts_markdown,
)
from goldfinger.market_attack import (
    CONVERGENCE_TOLERANCE,
    convergence_residual,
    has_converged,
    simulate_corner,
)
from goldfinger.vault_security import LAYER_ORDER, weakest_layer
from goldfinger.vault_threat_network import (
    edge_criticality,
    harden_network,
    minimum_effort_path,
    path_effort,
)

_PKG_ROOT = Path(__file__).resolve().parents[1]
_FIXED_NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)

# A diamond graph on non-canonical node names: a→d costs 2.0 by two symmetric
# routes, so removing either shortest-path edge leaves the effort unchanged.
_DIAMOND: dict[str, dict[str, float]] = {
    "a": {"b": 1.0, "c": 1.0},
    "b": {"a": 1.0, "d": 1.0},
    "c": {"a": 1.0, "d": 1.0},
    "d": {"b": 1.0, "c": 1.0},
}


# --------------------------------------------------------------------------
# Guard paths — laser physics / thermal
# --------------------------------------------------------------------------


def test_absorbed_power_rejects_non_numeric_absorptivity() -> None:
    with pytest.raises(TypeError, match="absorptivity must be a number"):
        absorbed_power(5000.0, absorptivity="0.6")  # type: ignore[arg-type]


def test_power_density_rejects_non_numeric_absorptivity() -> None:
    with pytest.raises(TypeError, match="absorptivity must be a number"):
        power_density(5000.0, 1.0e-3, absorptivity=None)  # type: ignore[arg-type]


def test_thermal_surface_temperature_rejects_non_numeric_time() -> None:
    with pytest.raises(TypeError, match="time must be a number"):
        thermal_surface_temperature("1.0", 1.0e8, 45.0, 7800.0, 460.0, 300.0)  # type: ignore[arg-type]


def test_thermal_surface_temperature_rejects_non_numeric_ambient() -> None:
    with pytest.raises(TypeError, match="ambient must be a number"):
        thermal_surface_temperature(1.0, 1.0e8, 45.0, 7800.0, 460.0, "300")  # type: ignore[arg-type]


def test_spot_radius_rejects_non_numeric_distance() -> None:
    with pytest.raises(TypeError, match="distance must be a number"):
        spot_radius_at_distance(1.78e-3, 1.064e-6, "10")  # type: ignore[arg-type]


def test_spot_radius_rejects_negative_distance() -> None:
    with pytest.raises(ValueError, match="distance must be non-negative"):
        spot_radius_at_distance(1.78e-3, 1.064e-6, -1.0)


def test_thermal_surface_temperature_rejects_negative_ambient() -> None:
    with pytest.raises(ValueError, match="ambient must be non-negative"):
        thermal_surface_temperature(1.0, 1.0e8, 45.0, 7800.0, 460.0, -5.0)


def test_effective_burn_range_rejects_negative_max_distance() -> None:
    beam = goldfinger.REFERENCE_BEAM
    with pytest.raises(ValueError, match="max_distance must be non-negative"):
        effective_burn_range(
            beam["power"],
            beam["waist"],
            beam["wavelength"],
            beam["absorptivity"],
            beam["conductivity"],
            beam["density"],
            beam["specific_heat"],
            beam["melt_temp"],
            beam["ambient"],
            beam["threat_window"],
            max_distance=-1.0,
        )


def test_effective_burn_range_returns_zero_when_window_is_unreachable() -> None:
    """A window far shorter than the focal melt time yields the 0.0 sentinel."""
    beam = goldfinger.REFERENCE_BEAM
    unreachable = effective_burn_range(
        beam["power"],
        beam["waist"],
        beam["wavelength"],
        beam["absorptivity"],
        beam["conductivity"],
        beam["density"],
        beam["specific_heat"],
        beam["melt_temp"],
        beam["ambient"],
        threat_window=1.0e-12,
    )
    assert unreachable == 0.0


# --------------------------------------------------------------------------
# Guard paths — vault security
# --------------------------------------------------------------------------


def test_weakest_layer_accepts_a_uniformly_perfect_vault() -> None:
    """All-1.0 ratings are valid: the first layer in traversal order wins."""
    perfect = dict.fromkeys(LAYER_ORDER, 1.0)
    assert weakest_layer(perfect) == LAYER_ORDER[0]


def test_weakest_layer_rejects_ratings_outside_the_traversal_order() -> None:
    with pytest.raises(ValueError, match="no rated layer appears in LAYER_ORDER"):
        weakest_layer({"moat": 0.4, "drawbridge": 0.2})


# --------------------------------------------------------------------------
# Guard paths — vault threat network
# --------------------------------------------------------------------------


def test_minimum_effort_path_rejects_non_numeric_edge_cost() -> None:
    graph = {"a": {"b": "cheap"}, "b": {"a": "cheap"}}
    with pytest.raises(TypeError, match="must be a number"):
        minimum_effort_path(graph, "a", "b")  # type: ignore[arg-type]


def test_path_effort_rejects_empty_path() -> None:
    with pytest.raises(ValueError, match="path must not be empty"):
        path_effort(_DIAMOND, ())


def test_path_effort_rejects_a_disconnected_hop() -> None:
    with pytest.raises(ValueError, match="no edge from 'a' to 'd'"):
        path_effort(_DIAMOND, ("a", "d"))


def test_edge_criticality_is_empty_when_a_symmetric_detour_exists() -> None:
    """Removing a shortest-path edge that a twin route replaces is not critical."""
    base_effort, path = minimum_effort_path(_DIAMOND, "a", "d")
    assert base_effort == 2.0
    assert len(path) == 3
    assert edge_criticality(_DIAMOND, "a", "d") == ()


def test_harden_network_stops_immediately_on_an_edgeless_graph() -> None:
    """Budget cannot be spent when there is no edge to raise."""
    report = harden_network({"vault": {}}, "vault", "vault", budget=3)
    assert report["allocation"] == {}
    assert report["min_effort_before"] == 0.0
    assert report["min_effort_after"] == 0.0
    assert report["effort_raised"] == 0.0


# --------------------------------------------------------------------------
# Guard paths — manuscript config loading
# --------------------------------------------------------------------------


def _write(root: Path, body: str) -> Path:
    (root / "manuscript").mkdir(parents=True, exist_ok=True)
    (root / "manuscript" / "config.yaml").write_text(body, encoding="utf-8")
    return root


def test_load_mission_config_rejects_a_non_mapping_document(tmp_path: Path) -> None:
    _write(tmp_path, "- first\n- second\n")
    with pytest.raises(ValueError, match="must contain a YAML mapping"):
        load_mission_config(tmp_path)


def test_generate_variables_tolerates_malformed_metadata_blocks(tmp_path: Path) -> None:
    """Non-conforming paper/authors/keywords blocks degrade to defaults."""
    _write(
        tmp_path,
        'paper: "not-a-mapping"\nauthors: "not-a-list-of-mappings"\nkeywords: "not-a-list"\n',
    )
    variables = generate_variables(project_root=tmp_path, now=_FIXED_NOW)
    assert variables["GOLDFINGER_TITLE"] == "Goldfinger: GRAND SLAM"
    assert variables["GOLDFINGER_AUTHOR"] == "Daniel Ari Friedman"
    assert variables["GOLDFINGER_KEYWORDS"] == ""
    # The computed result tokens are unaffected by broken identity metadata.
    assert float(variables["MARKET_PRICE_GAIN_PCT"]) > 25.0


# --------------------------------------------------------------------------
# Contracts — the manuscript describes itself from derived values
# --------------------------------------------------------------------------


def test_declared_token_tuple_equals_the_generated_key_set() -> None:
    variables = generate_variables(project_root=_PKG_ROOT, now=_FIXED_NOW)
    assert set(GOLDFINGER_TOKENS) == set(variables)
    assert len(GOLDFINGER_TOKENS) == len(set(GOLDFINGER_TOKENS)), "duplicate token declared"


def test_token_count_token_matches_the_declared_tuple_length() -> None:
    variables = generate_variables(project_root=_PKG_ROOT, now=_FIXED_NOW)
    assert variables["GOLDFINGER_TOKEN_COUNT"] == str(len(GOLDFINGER_TOKENS))


def test_concept_module_names_are_the_modules_actually_on_disk() -> None:
    names = concept_module_names()
    package_dir = Path(goldfinger.__file__).resolve().parent
    for name in names:
        assert (package_dir / f"{name}.py").is_file()
    assert "mission" not in names, "the bond-api adapter is not a concept module"
    assert "manuscript_variables" not in names, "token plumbing is not a concept module"
    assert {"market_attack", "reserve_attack", "vault_security"} <= set(names)
    assert {"vault_threat_network", "laser_physics", "laser_thermal"} <= set(names)


def test_module_and_figure_count_tokens_are_derived_not_declared() -> None:
    variables = generate_variables(project_root=_PKG_ROOT, now=_FIXED_NOW)
    assert variables["GOLDFINGER_MODULE_COUNT"] == str(len(concept_module_names()))
    assert variables["GOLDFINGER_FIGURE_COUNT"] == str(len(FIGURE_RENDERERS))


def test_figure_renderers_tuple_matches_the_exported_callables() -> None:
    exported = {name for name in goldfinger.figures.__all__ if name.startswith("plot_")}
    assert set(FIGURE_RENDERERS) == exported
    for name in FIGURE_RENDERERS:
        assert callable(getattr(goldfinger.figures, name))


def test_seed_token_matches_the_package_mission_seed() -> None:
    variables = generate_variables(project_root=_PKG_ROOT, now=_FIXED_NOW)
    assert variables["GOLDFINGER_SEED"] == str(goldfinger.MISSION_SEED)


def test_laser_severity_threshold_is_single_sourced() -> None:
    variables = generate_variables(project_root=_PKG_ROOT, now=_FIXED_NOW)
    assert float(variables["LASER_SEVERITY_THRESHOLD_W"]) == goldfinger.LASER_SEVERITY_THRESHOLD_W


# --------------------------------------------------------------------------
# Convergence is measured against a tolerance, not exact float equality
# --------------------------------------------------------------------------


def test_convergence_residual_rejects_a_non_result() -> None:
    with pytest.raises(TypeError, match="result must be a CornerResult"):
        convergence_residual({"shocked_price": 1.0})  # type: ignore[arg-type]


def test_reference_corner_never_attains_exact_equality() -> None:
    """The exact-equality test this package used to ship is false here.

    Tâtonnement is geometric, so the final price is close to but not equal to
    ``P*``. Asserting that keeps the tolerance-based check honest: it is doing
    real work, not restating an equality that already holds.
    """
    model = goldfinger.market_attack.REFERENCE_MODEL
    result = simulate_corner(
        model["reference_price"],
        model["supply_0"],
        model["fraction_removed"],
        model["elasticity"],
        model["adjustment"],
        model["steps"],
    )
    assert result.trajectory[-1] != result.shocked_price
    assert 0.0 < convergence_residual(result) <= CONVERGENCE_TOLERANCE
    assert has_converged(result, CONVERGENCE_TOLERANCE)


def test_a_truncated_trajectory_does_not_converge() -> None:
    """Positive control: the convergence gate can fail."""
    model = goldfinger.market_attack.REFERENCE_MODEL
    truncated = simulate_corner(
        model["reference_price"],
        model["supply_0"],
        model["fraction_removed"],
        model["elasticity"],
        model["adjustment"],
        steps=3,
    )
    assert convergence_residual(truncated) > CONVERGENCE_TOLERANCE
    assert not has_converged(truncated, CONVERGENCE_TOLERANCE)


def test_has_converged_rejects_a_non_positive_tolerance() -> None:
    model = goldfinger.market_attack.REFERENCE_MODEL
    result = simulate_corner(
        model["reference_price"],
        model["supply_0"],
        model["fraction_removed"],
        model["elasticity"],
    )
    with pytest.raises(ValueError, match="tolerance must be positive"):
        has_converged(result, tolerance=0.0)


def test_converged_token_and_mission_outcome_agree() -> None:
    """The manuscript's convergence claim is the mission's convergence claim."""
    from goldfinger.mission import build_provider

    variables = generate_variables(project_root=_PKG_ROOT, now=_FIXED_NOW)
    provider = build_provider()
    outcome = provider.execute(provider.plan(provider.brief()))
    token_says = variables["MARKET_CONVERGED"] == "true"
    assert token_says is outcome.results["all_converged"]
    assert token_says is True, "the reference corner is expected to converge"


# --------------------------------------------------------------------------
# Anti-hardcode gate: no computed result value appears as a prose literal
# --------------------------------------------------------------------------

#: Tokens whose values are *computed outcomes*. If one of these values turns up
#: in the prose as a literal, someone typed a number instead of a token, and it
#: will silently rot the next time the reference intel changes.
_RESULT_TOKENS = (
    "MARKET_SHOCKED_PRICE",
    "MARKET_PRICE_GAIN_PCT",
    "RESERVE_ATTACK_TIME",
    "RESERVE_FLOOR_TIME",
    "RESERVE_ATTACK_SUDDENNESS",
    "VAULT_SCORE",
    "VAULT_MIN_EFFORT",
    "VAULT_HARDENED_EFFORT",
    "LASER_BURN_THROUGH_S",
    "LASER_EFFECTIVE_RANGE_M",
    "LASER_RAYLEIGH_RANGE_M",
)


def _prose_without_tokens() -> str:
    sections = sorted(_PKG_ROOT.glob("manuscript/[0-9]*.md"))
    assert sections, "expected numbered manuscript sections to exist"
    joined = "\n".join(section.read_text(encoding="utf-8") for section in sections)
    return re.sub(r"\{\{[A-Z0-9_]+\}\}", " ", joined)


def test_no_computed_result_value_is_hardcoded_in_the_prose() -> None:
    variables = generate_variables(project_root=_PKG_ROOT, now=_FIXED_NOW)
    prose = _prose_without_tokens()
    offenders = [
        f"{token}={variables[token]}" for token in _RESULT_TOKENS if variables[token] in prose
    ]
    assert not offenders, f"result values hardcoded in manuscript prose: {offenders}"


def test_counts_document_reports_the_gate_when_nothing_was_measured() -> None:
    variables = generate_variables(project_root=_PKG_ROOT, now=_FIXED_NOW)
    document = render_counts_markdown(variables)
    assert "not measured in this run" in document
    assert "gate is **>=90%**" in document
    # Structural counts are taken from the same map the manuscript renders.
    assert f"Pure domain modules: **{variables['GOLDFINGER_MODULE_COUNT']}**" in document
    assert f"Manuscript tokens: **{variables['GOLDFINGER_TOKEN_COUNT']}**" in document


def test_counts_document_reports_measurements_when_they_are_supplied() -> None:
    variables = generate_variables(project_root=_PKG_ROOT, now=_FIXED_NOW)
    document = render_counts_markdown(variables, tests_collected=151, coverage_percent=99.5)
    assert "**151 collected**" in document
    assert "**99.50%**" in document
    assert "not measured in this run" not in document


def test_counts_renderer_refuses_an_incomplete_variable_map() -> None:
    variables = generate_variables(project_root=_PKG_ROOT, now=_FIXED_NOW)
    del variables["VAULT_SCORE"]
    with pytest.raises(KeyError, match="VAULT_SCORE"):
        render_counts_markdown(variables)


def test_generated_counts_file_matches_a_fresh_render() -> None:
    """The committed COUNTS.md must be what the generator produces today.

    Only the derived lines are compared: the measured test/coverage lines
    legitimately differ between a bare regeneration and a gated one.
    """
    counts_path = _PKG_ROOT / "docs" / "_generated" / "COUNTS.md"
    assert counts_path.is_file(), "docs/_generated/COUNTS.md must be committed"
    committed = counts_path.read_text(encoding="utf-8")
    variables = generate_variables(project_root=_PKG_ROOT, now=_FIXED_NOW)
    fresh = render_counts_markdown(variables)
    derived = [
        line
        for line in fresh.splitlines()
        if line.startswith(("- Pure domain modules", "- Manuscript tokens", "- Figures", "|"))
    ]
    assert derived, "expected derived lines to compare"
    stale = [line for line in derived if line not in committed]
    assert not stale, f"docs/_generated/COUNTS.md is stale; regenerate it. Stale lines: {stale}"


def test_the_anti_hardcode_gate_can_actually_fail() -> None:
    """Positive control for the gate above — a pasted value must be caught."""
    variables = generate_variables(project_root=_PKG_ROOT, now=_FIXED_NOW)
    contaminated = _prose_without_tokens() + (
        f"\nThe vault scores {variables['VAULT_SCORE']} on the composite.\n"
    )
    offenders = [token for token in _RESULT_TOKENS if variables[token] in contaminated]
    assert "VAULT_SCORE" in offenders
