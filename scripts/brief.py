#!/usr/bin/env python
"""GRAND SLAM mission phase CLI: brief.

Prints the mission brief (film identity, objectives, assets, constraints).
Thin wrapper over ``goldfinger.mission.build_provider``.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))  # noqa: E402

from goldfinger.mission import build_provider  # noqa: E402


def main() -> None:
    brief = build_provider().brief()
    print(f"[GRAND SLAM] film={brief.film} codename={brief.codename}")
    print("Objectives:")
    for objective in brief.objectives:
        print(f"  - {objective}")
    print("Assets:")
    for asset in brief.assets:
        print(f"  - {asset.kind}:{asset.name}")
    print("Constraints:")
    for constraint in brief.constraints:
        print(f"  - {constraint.kind}: {constraint.detail}")


if __name__ == "__main__":
    main()
