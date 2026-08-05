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

#: The exported figure renderers, in the order the generation script runs them.
#: ``manuscript_variables`` derives ``GOLDFINGER_FIGURE_COUNT`` from this tuple
#: so the manuscript never states a hand-counted number of figures.
FIGURE_RENDERERS: tuple[str, ...] = (
    "plot_market_corner_trajectory",
    "plot_reserve_crisis",
    "plot_vault_layered_score",
    "plot_vault_network",
    "plot_laser_burn_through",
    "plot_laser_engagement",
)

__all__ = [
    "FIGURE_RENDERERS",
    "plot_laser_burn_through",
    "plot_laser_engagement",
    "plot_market_corner_trajectory",
    "plot_reserve_crisis",
    "plot_vault_layered_score",
    "plot_vault_network",
]
