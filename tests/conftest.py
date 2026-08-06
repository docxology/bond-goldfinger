"""Test fixtures for the goldfinger package.

Adds the project ``src/`` to ``sys.path`` so both the pure domain modules and
the bond-api-dependent mission adapter import cleanly under pytest, and pins
the headless matplotlib backend so figure tests never open a display window.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))


import pytest  # noqa: E402


@pytest.fixture(scope="session")
def _live_test_count(request: pytest.FixtureRequest) -> int:
    """The number of tests collected in this session.

    pytest populates ``session.items`` after collection and before any test
    runs, so a session-scoped fixture observes the true live count. The V2
    COUNTS.md staleness gate uses it to bind the committed ``**N collected**``
    line to reality, so adding a test cannot silently leave a stale count in
    ``docs/_generated/COUNTS.md``.
    """
    return len(request.session.items)
