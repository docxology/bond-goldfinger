"""Tests for the goldfinger concept figure renderers."""

from __future__ import annotations

from pathlib import Path

from goldfinger.figures import (
    plot_laser_burn_through,
    plot_market_corner_trajectory,
    plot_vault_layered_score,
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


def test_all_figures_to_default_dir_are_deterministic(tmp_path: Path) -> None:
    # Rendering twice produces byte-identical PNGs (fully deterministic input).
    a = plot_market_corner_trajectory(tmp_path)
    bytes_a = a.read_bytes()
    b = plot_market_corner_trajectory(tmp_path)
    assert a.read_bytes() == bytes_a
    assert b.exists()  # same path, regenerated deterministically
    assert b.read_bytes() == bytes_a


def test_default_figure_dir_created(tmp_path: Path) -> None:
    # Pass a nested output dir that does not exist yet.
    nested = tmp_path / "a" / "b"
    path = plot_laser_burn_through(nested)
    assert path.parent == nested
    assert path.exists()
