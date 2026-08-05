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
from goldfinger.laser_thermal import (
    REFERENCE_BEAM,
    melt_time_at_distance,
    rayleigh_range,
)
from goldfinger.market_attack import REFERENCE_MODEL, simulate_corner
from goldfinger.reserve_attack import (
    REFERENCE_ATTACK,
    attack_time,
    reserve_floor_time,
    simulate_reserve_crisis,
)
from goldfinger.vault_security import (
    REFERENCE_RATINGS,
    layered_security_score,
    penetration_probability,
)
from goldfinger.vault_threat_network import (
    REFERENCE_GRAPH,
    harden_network,
    minimum_effort_path,
    path_effort,
)

__all__ = [
    "plot_laser_burn_through",
    "plot_laser_engagement",
    "plot_market_corner_trajectory",
    "plot_reserve_crisis",
    "plot_vault_layered_score",
    "plot_vault_network",
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


def plot_reserve_crisis(output_dir: Path | None = None) -> Path:
    """Render the speculative-attack reserve drain and shadow-exchange-rate path."""
    a = REFERENCE_ATTACK
    floor = reserve_floor_time(
        a["parity"], a["foreign_rate"], a["interest_elasticity"], a["credit_0"], a["growth"]
    )
    step = 0.5
    times = tuple(round(i * step, 1) for i in range(int(floor / step) + 1))
    crisis = simulate_reserve_crisis(
        times, a["parity"], a["foreign_rate"], a["interest_elasticity"], a["credit_0"], a["growth"]
    )
    attack = attack_time(
        a["parity"], a["foreign_rate"], a["interest_elasticity"], a["credit_0"], a["growth"]
    )
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(
        crisis["times"],
        crisis["reserves"],
        marker="o",
        markersize=2,
        linewidth=1.5,
        label="Gold reserves (peg)",
    )
    ax.axvline(
        attack, color="crimson", linestyle="--", linewidth=1, label=f"Attack time: {attack:.2f}"
    )
    ax.axhline(
        a["parity"], color="navy", linestyle=":", linewidth=1, label=f"Parity ({a['parity']:.2f})"
    )
    ax.set_xlabel("Time (units)")
    ax.set_ylabel("Reserves (normalised)")
    ax.set_title("Speculative attack on the gold peg: reserve drain")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    path = _figure_dir(output_dir) / "reserve_crisis.png"
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def plot_vault_network(output_dir: Path | None = None) -> Path:
    """Render the vault-zone graph: weak-path edge effort before/after hardening."""
    source, target = "perimeter", "gold_chamber"
    effort, weak_path = minimum_effort_path(REFERENCE_GRAPH, source, target)
    hardening = harden_network(REFERENCE_GRAPH, source, target, budget=10, gain_per_unit=0.5)
    labels = [f"{a}→{b}" for a, b in zip(weak_path, weak_path[1:], strict=False)]
    edge_costs = [
        path_effort(REFERENCE_GRAPH, weak_path[i : i + 2]) for i in range(len(weak_path) - 1)
    ]
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.bar(labels, edge_costs, color="#3b6ea5", alpha=0.9)
    ax.axhline(
        effort,
        color="crimson",
        linestyle="--",
        linewidth=1.5,
        label=f"Min path effort: {effort:.2f}",
    )
    ax.axhline(
        hardening["min_effort_after"],
        color="darkgreen",
        linestyle="--",
        linewidth=1.5,
        label=f"After hardening: {hardening['min_effort_after']:.2f}",
    )
    ax.set_ylabel("Intrusion effort (edge cost)")
    ax.set_xlabel("Weak-path zone transition")
    ax.set_title("Vault network: minimum-effort intrusion path (secret tunnel)")
    ax.tick_params(axis="x", rotation=30)
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    path = _figure_dir(output_dir) / "vault_network.png"
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def plot_laser_engagement(output_dir: Path | None = None) -> Path:
    """Render the Gaussian-beam melt-time vs distance (the laser engagement envelope)."""
    b = REFERENCE_BEAM
    z_r = rayleigh_range(b["waist"], b["wavelength"])
    distances = [round(d, 1) for d in range(0, 91, 3)]
    melt_times = [
        melt_time_at_distance(
            b["power"],
            b["waist"],
            b["wavelength"],
            d,
            b["absorptivity"],
            b["conductivity"],
            b["density"],
            b["specific_heat"],
            b["melt_temp"],
            b["ambient"],
        )
        for d in distances
    ]
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(distances, melt_times, marker="o", markersize=3, linewidth=1.5, color="crimson")
    ax.axhline(
        b["threat_window"],
        color="navy",
        linestyle="--",
        linewidth=1,
        label=f"Threat window: {b['threat_window']}s",
    )
    ax.axvline(z_r, color="gray", linestyle=":", linewidth=1, label=f"Rayleigh range: {z_r:.1f} m")
    ax.set_xlabel("Target distance (m)")
    ax.set_ylabel("Surface melt time (s)")
    ax.set_title("Laser engagement: defocusing lengthens melt time with range")
    ax.legend()
    ax.grid(alpha=0.3, which="both")
    fig.tight_layout()
    path = _figure_dir(output_dir) / "laser_engagement.png"
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path
