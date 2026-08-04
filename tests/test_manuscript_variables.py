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
    """Every ``{{TOKEN}}`` referenced in numbered prose sections must exist.

    Scans ``manuscript/[0-9]*.md`` only (guide files legitimately show literal
    ``{{TOKEN}}`` placeholders).
    """
    variables = generate_variables(
        project_root=_PKG_ROOT, now=datetime(2026, 1, 1, tzinfo=timezone.utc)
    )
    prose = sorted(_PKG_ROOT.glob("manuscript/[0-9]*.md"))
    assert prose, "expected numbered manuscript sections to exist"
    tokens: set[str] = set()
    for section in prose:
        text = section.read_text(encoding="utf-8")
        tokens.update(re.findall(r"\{\{([A-Z0-9_]+)\}\}", text))
    assert tokens, "no tokens found in manuscript prose"
    missing = sorted(tok for tok in tokens if tok not in variables)
    assert not missing, f"unresolved manuscript tokens: {missing}"
