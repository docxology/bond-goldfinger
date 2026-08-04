#!/usr/bin/env python
"""GRAND SLAM mission phase CLI: recon.

Accepts a recon goal (defaults to the flagship objective) and prints the
recon report findings. Thin wrapper over ``goldfinger.mission.build_provider``.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))  # noqa: E402

from bond_api.protocol import ReconRequest  # noqa: E402

from goldfinger.mission import build_provider  # noqa: E402

_DEFAULT_GOAL = "assess the feasibility of GRAND SLAM against the target"


def main(argv: list[str] | None = None) -> None:
    args = list(argv) if argv is not None else sys.argv[1:]
    goal = args[0] if args else _DEFAULT_GOAL
    provider = build_provider()
    request = ReconRequest(goal=goal)
    report = provider.recon(request)
    print(f"[GRAND SLAM] recon goal: {request.goal}")
    print("Findings:")
    for finding in report.findings:
        print(f"  - {finding.label}: {finding.detail}")


if __name__ == "__main__":
    main()
