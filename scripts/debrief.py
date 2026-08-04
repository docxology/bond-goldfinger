#!/usr/bin/env python
"""GRAND SLAM mission phase CLI: debrief.

Runs the full mission flow and prints the debrief lessons. Thin wrapper over
``goldfinger.mission.build_provider`` and ``bond_api.protocol.run_mission``.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))  # noqa: E402

from bond_api.protocol import ReconRequest, run_mission  # noqa: E402

from goldfinger.mission import build_provider  # noqa: E402

_DEFAULT_GOAL = "assess the feasibility of GRAND SLAM against the target"


def main(argv: list[str] | None = None) -> None:
    args = list(argv) if argv is not None else sys.argv[1:]
    goal = args[0] if args else _DEFAULT_GOAL
    debrief = run_mission(build_provider(), ReconRequest(goal=goal))
    success = debrief.outcome.success
    print(f"[GRAND SLAM] mission success={success}")
    print("Lessons learned:")
    for lesson in debrief.lessons:
        print(f"  - {lesson}")


if __name__ == "__main__":
    main()
