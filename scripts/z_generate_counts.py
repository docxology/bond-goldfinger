#!/usr/bin/env python
"""GRAND SLAM live-counts generation.

Writes ``docs/_generated/COUNTS.md`` from the deterministic token map, so the
counts file cannot drift from the manuscript it accompanies. Thin orchestrator
— the rendering lives in
``goldfinger.manuscript_variables.render_counts_markdown``.

Test count and coverage are *measurements*, not derivations: pass them in from
a real gate run, or omit them and the generated file states the enforced gate
instead of a number nobody measured.

    uv run python scripts/z_generate_counts.py --tests <N> --coverage <PCT>
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))  # noqa: E402

from goldfinger.manuscript_variables import (  # noqa: E402
    generate_variables,
    render_counts_markdown,
)

_PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--tests",
        type=int,
        default=None,
        help="test count observed in a real pytest run (omit if not measured)",
    )
    parser.add_argument(
        "--coverage",
        type=float,
        default=None,
        help="line+branch coverage percent observed in that run (omit if not measured)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    variables = generate_variables(require_analysis_outputs=False, project_root=_PROJECT_ROOT)
    document = render_counts_markdown(
        variables,
        tests_collected=args.tests,
        coverage_percent=args.coverage,
    )
    target = _PROJECT_ROOT / "docs" / "_generated" / "COUNTS.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(document, encoding="utf-8")
    print(f"wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
