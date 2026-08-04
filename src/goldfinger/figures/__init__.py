"""Figure generation for the goldfinger manuscript.

Renders the GRAND SLAM concept models to publication-quality PNGs under
``output/figures/``: the market-corner price trajectory, the vault layered
defense score, and the laser burn-through time curve. Figures are generated
deterministically from the pure domain core (no sampled data).
"""

from __future__ import annotations

from goldfinger.figures.plots import (
    plot_laser_burn_through,
    plot_market_corner_trajectory,
    plot_vault_layered_score,
)

__all__ = [
    "plot_laser_burn_through",
    "plot_market_corner_trajectory",
    "plot_vault_layered_score",
]
