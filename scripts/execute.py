#!/usr/bin/env python
"""GRAND SLAM mission phase CLI: execute.

Runs the plan's compute steps and prints the deterministic outcome (market
corner, vault defense, laser threat) with provenance. Thin wrapper over
``goldfinger.mission.build_provider``.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))  # noqa: E402

from goldfinger.mission import build_provider  # noqa: E402


def _fmt(value: float, digits: int = 3) -> str:
    return f"{value:.{digits}f}"


def main() -> None:
    provider = build_provider()
    plan = provider.plan(provider.brief())
    outcome = provider.execute(plan)
    results = outcome.results
    corner = results["corner"]
    vault = results["vault"]
    laser = results["laser"]
    print(f"[GRAND SLAM] success={outcome.success}")
    print(
        f"  market corner: shocked price ${corner['shocked_price']:.2f}/oz "
        f"(gain {corner['price_gain'] * 100:.1f}%)"
    )
    print(
        f"  vault defense: score {vault['layered_score']:.3f} "
        f"({vault['verdict']}), penetration {vault['penetration_probability'] * 100:.2e}%"
    )
    print(f"  laser threat: burn-through {laser['burn_through_time_s']:.3f}s ({laser['severity']})")
    print(
        f"  provenance: {outcome.provenance.package_version} seed={outcome.provenance.seed} "
        f"hash={outcome.provenance.input_hash}"
    )


if __name__ == "__main__":
    main()
