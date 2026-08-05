#!/usr/bin/env python
"""GRAND SLAM mission phase CLI: execute.

Runs the plan's compute steps and prints the deterministic outcome across all
six concept models (market corner, reserve attack, layered vault defense,
vault threat network, laser burn-through, laser thermal engagement) with
provenance. Thin wrapper over ``goldfinger.mission.build_provider`` — all
computation lives in ``src/goldfinger/``.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))  # noqa: E402

from goldfinger.mission import build_provider  # noqa: E402


def main() -> None:
    provider = build_provider()
    plan = provider.plan(provider.brief())
    outcome = provider.execute(plan)
    results = outcome.results
    corner = results["corner"]
    reserve = results["reserve"]
    vault = results["vault"]
    vault_net = results["vault_network"]
    laser = results["laser"]
    thermal = results["laser_thermal"]
    print(f"[GRAND SLAM] success={outcome.success} steps={results['steps_completed']}")
    print(
        f"  market corner: shocked price ${corner['shocked_price']:.2f}/oz "
        f"(gain {corner['price_gain'] * 100:.1f}%)"
    )
    print(
        f"  reserve attack: peg falls at t={reserve['attack_time']:.2f} "
        f"(gradual floor {reserve['reserve_floor_time']:.2f}, "
        f"suddenness {reserve['attack_suddenness']:.2f}); "
        f"float depreciation {reserve['floating_depreciation'] * 100:.0f}%"
    )
    print(
        f"  vault defense: score {vault['layered_score']:.3f} "
        f"({vault['verdict']}), penetration {vault['penetration_probability'] * 100:.2e}%, "
        f"weakest layer {vault['weakest_layer']}"
    )
    print(
        f"  vault network: min effort {vault_net['min_effort']:.2f} via "
        f"{' -> '.join(vault_net['weak_path'])}; hardened to "
        f"{vault_net['hardened_effort']:.2f} (+{vault_net['effort_raised']:.2f})"
    )
    print(f"  laser threat: burn-through {laser['burn_through_time_s']:.3f}s ({laser['severity']})")
    print(
        f"  laser thermal: effective range {thermal['effective_burn_range_m']:.1f} m "
        f"({thermal['type']}), melt at focus "
        f"{thermal['surface_melt_time_at_focus_s']:.4f}s within a "
        f"{thermal['threat_window_s']:.1f}s window"
    )
    print(
        f"  provenance: {outcome.provenance.package_version} seed={outcome.provenance.seed} "
        f"hash={outcome.provenance.input_hash}"
    )


if __name__ == "__main__":
    main()
