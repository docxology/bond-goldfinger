"""Matplotlib renderers for the GRAND SLAM concept models.

Each ``plot_*`` function writes a PNG to ``output_dir`` (default
``<project_root>/output/figures``) and returns the path it wrote. All data is
computed deterministically by the pure domain modules — nothing is sampled.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless rendering; no display window

import matplotlib.pyplot as plt  # noqa: E402

from goldfinger.laser_physics import REFERENCE_PHYSICS, burn_through_time
from goldfinger.market_attack import REFERENCE_MODEL, simulate_corner
from goldfinger.vault_security import (
    REFERENCE_RATINGS,
    layered_security_score,
    penetration_probability,
)

__all__ = [
    "plot_laser_burn_through",
    "plot_market_corner_trajectory",
    "plot_vault_layered_score",
]

_PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _figure_dir(output_dir: Path | None) -> Path:
    target = Path(output_dir) if output_dir is not None else _PROJECT_ROOT / "output" / "figures"
    target.mkdir(parents=True, exist_ok=True)
    return target


def plot_market_corner_trajectory(output_dir: Path | None = None) -> Path:
    """Render the tatonnement price-trajectory figure for the market corner."""
    model = REFERENCE_MODEL
    result = simulate_corner(
        model["reference_price"],
        model["supply_0"],
        model["fraction_removed"],
        model["elasticity"],
        model["adjustment"],
        model["steps"],
    )
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(
        range(len(result.trajectory)), result.trajectory, marker="o", markersize=3, linewidth=1.5
    )
    ax.axhline(
        result.shocked_price,
        color="crimson",
        linestyle="--",
        linewidth=1,
        label=f"Shocked equilibrium (${result.shocked_price:.0f}/oz)",
    )
    ax.axhline(
        model["reference_price"],
        color="navy",
        linestyle=":",
        linewidth=1,
        label=f"Reference (${model['reference_price']:.0f}/oz)",
    )
    ax.set_xlabel("Tatonnement step")
    ax.set_ylabel("Gold price (USD/oz)")
    ax.set_title("Operation Grand Slam: supply-shock price dynamics")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    path = _figure_dir(output_dir) / "market_corner_trajectory.png"
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def plot_vault_layered_score(output_dir: Path | None = None) -> Path:
    """Render the layered vault-defense score figure (bars + composite)."""
    ratings = REFERENCE_RATINGS
    score = layered_security_score(ratings)
    names = list(ratings)
    values = [ratings[name] for name in names]
    fig, ax = plt.subplots(figsize=(7, 4.5))
    bars = ax.bar(names, values, color="#3b6ea5", alpha=0.9)
    for bar, value in zip(bars, values, strict=True):
        ax.text(
            bar.get_x() + bar.get_width() / 2, value + 0.01, f"{value:.2f}", ha="center", fontsize=8
        )
    ax.axhline(
        score, color="crimson", linestyle="--", linewidth=1.5, label=f"Composite score: {score:.3f}"
    )
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Defense rating (0–1)")
    ax.set_xlabel("Defensive layer")
    ax.set_title(
        f"Fort Knox-style layered defense "
        f"(penetration P = {penetration_probability(ratings) * 100:.1f}%)"
    )
    ax.tick_params(axis="x", rotation=20)
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    path = _figure_dir(output_dir) / "vault_layered_score.png"
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def plot_laser_burn_through(output_dir: Path | None = None) -> Path:
    """Render burn-through time vs laser power for the reference vault plate."""
    phys = REFERENCE_PHYSICS
    powers = [1000.0, 2000.0, 3000.0, 5000.0, 7500.0, 10000.0, 15000.0, 20000.0]
    times = [
        burn_through_time(
            p,
            phys["area"],
            phys["density"],
            phys["thickness"],
            phys["specific_heat"],
            phys["delta_temperature"],
            phys["absorptivity"],
        )
        for p in powers
    ]
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(powers, times, marker="o", linewidth=1.5, color="crimson")
    ax.set_xlabel("Laser power (W)")
    ax.set_ylabel("Burn-through time (s)")
    ax.set_title("Laser threat physics: time to breach a 50 mm steel plate")
    ax.grid(alpha=0.3, which="both")
    fig.tight_layout()
    path = _figure_dir(output_dir) / "laser_burn_through.png"
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path
