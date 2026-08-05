"""Tests for goldfinger manuscript variable hydration and the live token gate."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

import pytest

from goldfinger.manuscript_variables import (
    GOLDFINGER_TOKENS,
    generate_variables,
    load_mission_config,
    manuscript_prose_paths,
)

_PKG_ROOT = Path(__file__).resolve().parents[1]


def _write_config(root: Path) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    manuscript = root / "manuscript"
    manuscript.mkdir(parents=True, exist_ok=True)
    config = manuscript / "config.yaml"
    config.write_text(
        "paper:\n"
        '  title: "Goldfinger: GRAND SLAM"\n'
        '  subtitle: "Special-Agent Mission Software"\n'
        '  version: "0.1.0"\n'
        "authors:\n"
        '  - name: "Daniel Ari Friedman"\n'
        '    orcid: "0000-0001-6232-9096"\n'
        '    affiliation: "Active Inference Institute"\n'
        "keywords:\n"
        '  - "gold-market cornering"\n'
        '  - "vault defense"\n',
        encoding="utf-8",
    )
    return root


def test_load_mission_config_missing_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_mission_config(tmp_path)


def test_generate_variables_uses_provided_root(tmp_path: Path) -> None:
    root = _write_config(tmp_path)
    fixed = datetime(2026, 8, 4, 12, 0, 0, tzinfo=timezone.utc)
    variables = generate_variables(require_analysis_outputs=True, project_root=root, now=fixed)
    assert variables["GOLDFINGER_TITLE"] == "Goldfinger: GRAND SLAM"
    assert variables["GOLDFINGER_CODENAME"] == "GRAND SLAM"
    assert variables["GOLDFINGER_VERSION"] == "0.1.0"
    assert variables["GENERATION_TIMESTAMP"] == "2026-08-04 12:00:00 UTC"


def test_generate_variables_all_tokens_present(tmp_path: Path) -> None:
    root = _write_config(tmp_path)
    variables = generate_variables(project_root=root, now=datetime(2026, 1, 1, tzinfo=timezone.utc))
    for token in GOLDFINGER_TOKENS:
        assert token in variables


def test_generate_variables_computed_metrics(tmp_path: Path) -> None:
    root = _write_config(tmp_path)
    variables = generate_variables(project_root=root, now=datetime(2026, 1, 1, tzinfo=timezone.utc))
    # Market: 30% supply cut at elasticity 1.25 -> positive double-digit gain.
    assert float(variables["MARKET_PRICE_GAIN_PCT"]) > 25.0
    assert float(variables["MARKET_SHOCKED_PRICE"]) > float(variables["MARKET_REFERENCE_PRICE"])
    # Vault: medium-grade composite, single-digit penetration %.
    assert variables["VAULT_VERDICT"] == "medium"
    assert 0.0 <= float(variables["VAULT_PENETRATION_PCT"]) < 1.0
    # Laser: sub-second burn-through at reference power.
    assert float(variables["LASER_BURN_THROUGH_S"]) < 2.0


def test_generate_variables_version_hash_is_stable(tmp_path: Path) -> None:
    root = _write_config(tmp_path)
    fixed = datetime(2026, 1, 1, tzinfo=timezone.utc)
    a = generate_variables(project_root=root, now=fixed)
    b = generate_variables(project_root=root, now=fixed)
    assert a["GOLDFINGER_VERSION_HASH"] == b["GOLDFINGER_VERSION_HASH"]


def test_all_manuscript_tokens_are_generated_live() -> None:
    """Every ``{{TOKEN}}`` in a *rendered* manuscript file must exist.

    Rendered files are the numbered sections plus ``preamble.md``
    (:func:`manuscript_prose_paths`). Guide files legitimately show literal
    ``{{TOKEN}}`` placeholders and are excluded.
    """
    variables = generate_variables(
        project_root=_PKG_ROOT, now=datetime(2026, 1, 1, tzinfo=timezone.utc)
    )
    prose = manuscript_prose_paths(_PKG_ROOT)
    assert prose, "expected rendered manuscript files to exist"
    tokens: set[str] = set()
    for section in prose:
        text = section.read_text(encoding="utf-8")
        tokens.update(re.findall(r"\{\{([A-Z0-9_]+)\}\}", text))
    assert tokens, "no tokens found in manuscript prose"
    missing = sorted(tok for tok in tokens if tok not in variables)
    assert not missing, f"unresolved manuscript tokens: {missing}"


def test_the_scanned_file_set_includes_the_preamble() -> None:
    """The preamble's six identity tokens are inside the gate, not beside it."""
    names = {path.name for path in manuscript_prose_paths(_PKG_ROOT)}
    assert "preamble.md" in names
    assert "01_introduction.md" in names
    assert "README.md" not in names, "guide files must stay out of the token gate"


def test_prose_paths_omit_a_preamble_that_does_not_exist(tmp_path: Path) -> None:
    """A tree without a preamble yields only its numbered sections."""
    manuscript = tmp_path / "manuscript"
    manuscript.mkdir(parents=True)
    (manuscript / "01_intro.md").write_text("# intro\n", encoding="utf-8")
    (manuscript / "README.md").write_text("# guide\n", encoding="utf-8")
    assert [p.name for p in manuscript_prose_paths(tmp_path)] == ["01_intro.md"]


def test_the_live_token_gate_can_actually_fail_on_the_preamble() -> None:
    """Positive control: an unknown token in the preamble is caught.

    Reads the committed preamble, appends a token that is not generated, and
    shows the same membership check the gate performs now reports it.
    """
    variables = generate_variables(
        project_root=_PKG_ROOT, now=datetime(2026, 1, 1, tzinfo=timezone.utc)
    )
    preamble = (_PKG_ROOT / "manuscript" / "preamble.md").read_text(encoding="utf-8")
    contaminated = preamble + "\nversion {{GOLDFINGER_VERSIOM}}\n"
    found = set(re.findall(r"\{\{([A-Z0-9_]+)\}\}", contaminated))
    assert "GOLDFINGER_VERSIOM" in found
    assert [tok for tok in found if tok not in variables] == ["GOLDFINGER_VERSIOM"]
