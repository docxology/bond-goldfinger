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
