"""Figure generation for the goldfinger manuscript.

Renders the GRAND SLAM concept models to publication-quality PNGs under
``output/figures/``: market corner trajectory, speculative reserve attack,
layered and network vault defense, and laser burn-through / thermal engagement.
Figures are generated deterministically from the pure domain core (no sampled
data).
"""

from __future__ import annotations

from goldfinger.figures.plots import (
    plot_laser_burn_through,
    plot_laser_engagement,
    plot_market_corner_trajectory,
    plot_reserve_crisis,
    plot_vault_layered_score,
    plot_vault_network,
)

__all__ = [
    "plot_laser_burn_through",
    "plot_laser_engagement",
    "plot_market_corner_trajectory",
    "plot_reserve_crisis",
    "plot_vault_layered_score",
    "plot_vault_network",
]
