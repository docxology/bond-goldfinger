#!/usr/bin/env python
"""GRAND SLAM manuscript variable + figure generation.

Computes the ``{{TOKEN}} → value`` map from ``manuscript/config.yaml`` and the
deterministic domain core, writes it to ``output/data/manuscript_variables.json``,
renders the three concept figures to ``output/figures/``, and prints a summary.

Companion gate: ``tests/test_manuscript_variables.py`` asserts every token used
in the numbered prose sections exists in the generated map.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))  # noqa: E402

from goldfinger.figures import (  # noqa: E402
    plot_laser_burn_through,
    plot_laser_engagement,
    plot_market_corner_trajectory,
    plot_reserve_crisis,
    plot_vault_layered_score,
    plot_vault_network,
)
from goldfinger.manuscript_variables import generate_variables  # noqa: E402

_PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    variables = generate_variables(require_analysis_outputs=False, project_root=_PROJECT_ROOT)

    data_dir = _PROJECT_ROOT / "output" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    json_path = data_dir / "manuscript_variables.json"
    with json_path.open("w", encoding="utf-8") as handle:
        json.dump(variables, handle, indent=2, sort_keys=True)

    figures_dir = _PROJECT_ROOT / "output" / "figures"
    figure_paths = (
        plot_market_corner_trajectory(figures_dir),
        plot_reserve_crisis(figures_dir),
        plot_vault_layered_score(figures_dir),
        plot_vault_network(figures_dir),
        plot_laser_burn_through(figures_dir),
        plot_laser_engagement(figures_dir),
    )

    print(f"wrote {json_path}")
    print(
        f"  - {len(variables)} tokens (sample): "
        f"MARKET_PRICE_GAIN_PCT={variables['MARKET_PRICE_GAIN_PCT']}%, "
        f"VAULT_SCORE={variables['VAULT_SCORE']}, "
        f"LASER_BURN_THROUGH_S={variables['LASER_BURN_THROUGH_S']}s"
    )
    for path in figure_paths:
        print(f"  figure: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
