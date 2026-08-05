"""Tests for the goldfinger concept figure renderers."""

from __future__ import annotations

from pathlib import Path

import pytest

import goldfinger.figures
from goldfinger.figures import (
    FIGURE_RENDERERS,
    plot_laser_burn_through,
    plot_laser_engagement,
    plot_market_corner_trajectory,
    plot_reserve_crisis,
    plot_vault_layered_score,
    plot_vault_network,
)


def test_market_corner_figure(tmp_path: Path) -> None:
    path = plot_market_corner_trajectory(tmp_path)
    assert path.exists()
    assert path.suffix == ".png"
    assert path.stat().st_size > 1000


def test_vault_score_figure(tmp_path: Path) -> None:
    path = plot_vault_layered_score(tmp_path)
    assert path.exists()
    assert path.stat().st_size > 1000


def test_laser_burn_through_figure(tmp_path: Path) -> None:
    path = plot_laser_burn_through(tmp_path)
    assert path.exists()
    assert path.stat().st_size > 1000


@pytest.mark.parametrize("name", FIGURE_RENDERERS)
def test_every_figure_renderer_is_byte_deterministic(name: str, tmp_path: Path) -> None:
    """Render twice into separate directories and compare bytes.

    Parametrised over :data:`FIGURE_RENDERERS`, so *every* renderer is double-
    rendered — the earlier version of this test double-rendered one of six and
    checked the other five only for existence and size, while the manuscript
    rested a byte-determinism claim on it. A renderer added to the package is
    covered automatically.
    """
    renderer = getattr(goldfinger.figures, name)
    first = renderer(tmp_path / "first")
    second = renderer(tmp_path / "second")
    assert first.name == second.name
    assert first.read_bytes() == second.read_bytes(), f"{name} is not byte-deterministic"


@pytest.mark.parametrize("name", FIGURE_RENDERERS)
def test_every_figure_renderer_overwrites_deterministically(name: str, tmp_path: Path) -> None:
    """Re-rendering over an existing file reproduces the same bytes."""
    renderer = getattr(goldfinger.figures, name)
    original = renderer(tmp_path).read_bytes()
    assert renderer(tmp_path).read_bytes() == original


def test_the_determinism_gate_covers_every_exported_renderer() -> None:
    """The parametrisation is the full renderer set, not a chosen subset."""
    exported = {n for n in goldfinger.figures.__all__ if n.startswith("plot_")}
    assert set(FIGURE_RENDERERS) == exported
    assert len(FIGURE_RENDERERS) > 1


def test_default_figure_dir_created(tmp_path: Path) -> None:
    # Pass a nested output dir that does not exist yet.
    nested = tmp_path / "a" / "b"
    path = plot_laser_burn_through(nested)
    assert path.parent == nested
    assert path.exists()


def test_reserve_crisis_figure(tmp_path: Path) -> None:
    path = plot_reserve_crisis(tmp_path)
    assert path.name == "reserve_crisis.png"
    assert path.stat().st_size > 1000


def test_vault_network_figure(tmp_path: Path) -> None:
    path = plot_vault_network(tmp_path)
    assert path.name == "vault_network.png"
    assert path.stat().st_size > 1000


def test_laser_engagement_figure(tmp_path: Path) -> None:
    path = plot_laser_engagement(tmp_path)
    assert path.name == "laser_engagement.png"
    assert path.stat().st_size > 1000
