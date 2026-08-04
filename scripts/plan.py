#!/usr/bin/env python
"""GRAND SLAM mission phase CLI: plan.

Prints the ordered plan steps derived from the mission brief. Thin wrapper
over ``goldfinger.mission.build_provider``.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))  # noqa: E402

from goldfinger.mission import build_provider  # noqa: E402


def main() -> None:
    provider = build_provider()
    plan = provider.plan(provider.brief())
    print("[GRAND SLAM] mission plan:")
    for index, step in enumerate(plan.steps, start=1):
        print(f"  {index}. {step.name} — {step.action} {step.params}")


if __name__ == "__main__":
    main()
