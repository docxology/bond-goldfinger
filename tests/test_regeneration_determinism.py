"""Regeneration determinism: running the real generators twice is byte-identical.

The manuscript claims that regenerating the derived artifacts reproduces them
exactly. That claim was false for one release: ``manuscript_variables.py``
stamped ``datetime.now(timezone.utc)`` into ``GENERATION_TIMESTAMP``, which was
persisted into ``output/data/manuscript_variables.json`` and folded into
``GOLDFINGER_VERSION_HASH``, so every run wrote different bytes while the prose
said persisted artifacts carry no wall-clock dependence.

The suite could not catch it, because every existing test injected a fixed
``now=``. A test that pins the clock cannot detect a leaking clock — it *is*
the leak, held still. So this module deliberately does the opposite:

* it runs the **real** generator entry points as subprocesses (the production
  path, not an in-process call with helpful arguments),
* it lets the wall clock actually advance between the two runs, and
* it carries a positive control that reintroduces a clock into a throwaway copy
  of the source and proves the comparison goes red.

Everything happens inside a scratch copy of the package, so the committed tree
and the real ``output/`` are untouched.
"""

from __future__ import annotations

import hashlib
import shutil
import subprocess
import sys
import time
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[1]

#: Derived artifacts the byte-identical claim covers.
_COUNTS_RELPATH = Path("docs/_generated/COUNTS.md")

_IGNORED = shutil.ignore_patterns(
    ".venv",
    ".git",
    "output",
    "__pycache__",
    ".mypy_cache",
    ".ruff_cache",
    ".pytest_cache",
)


def _sandbox(tmp_path: Path) -> Path:
    """A scratch copy of the package with no pre-existing output tree."""
    sandbox = tmp_path / "pkg"
    shutil.copytree(_PROJECT_ROOT, sandbox, ignore=_IGNORED)
    return sandbox


def _regenerate(sandbox: Path) -> None:
    """Run both real generator CLIs in ``sandbox``, failing loudly on error."""
    for script in ("z_generate_manuscript_variables.py", "z_generate_counts.py"):
        proc = subprocess.run(
            [sys.executable, f"scripts/{script}"],
            capture_output=True,
            text=True,
            cwd=sandbox,
            check=False,
        )
        assert proc.returncode == 0, f"{script} failed:\n{proc.stdout}\n{proc.stderr}"


def _fingerprint(sandbox: Path) -> dict[str, str]:
    """SHA-256 of every generated artifact, keyed by package-relative path."""
    digests: dict[str, str] = {}
    for path in sorted((sandbox / "output").rglob("*")):
        if path.is_file():
            key = str(path.relative_to(sandbox))
            digests[key] = hashlib.sha256(path.read_bytes()).hexdigest()
    counts = sandbox / _COUNTS_RELPATH
    assert counts.is_file(), "the counts generator did not write COUNTS.md"
    digests[str(_COUNTS_RELPATH)] = hashlib.sha256(counts.read_bytes()).hexdigest()
    return digests


def test_regeneration_is_byte_identical_across_a_wall_clock_gap(tmp_path: Path) -> None:
    """The claim itself: two real regenerations, separated in time, agree byte for byte."""
    sandbox = _sandbox(tmp_path)

    _regenerate(sandbox)
    first = _fingerprint(sandbox)

    # Let the clock advance past the resolution of any plausible stamp format
    # before the second run, so a second-precision leak cannot hide.
    time.sleep(1.1)

    _regenerate(sandbox)
    second = _fingerprint(sandbox)

    assert first, "no generated artifacts were produced"
    assert set(first) == set(second), "the two runs produced different file sets"
    drifted = sorted(name for name, digest in first.items() if second[name] != digest)
    assert not drifted, f"regeneration is not byte-identical; these files changed: {drifted}"


def test_the_generated_token_map_contains_no_clock_derived_value(tmp_path: Path) -> None:
    """No token may carry sub-day precision that only a clock could supply."""
    sandbox = _sandbox(tmp_path)
    _regenerate(sandbox)
    import json

    payload = json.loads(
        (sandbox / "output" / "data" / "manuscript_variables.json").read_text(encoding="utf-8")
    )
    assert "GENERATION_TIMESTAMP" not in payload, (
        "the wall-clock token is back; persisted artifacts must not read a clock"
    )
    assert payload["MANUSCRIPT_DATE"], "the manuscript date must come from committed config"


def test_the_determinism_gate_can_actually_fail(tmp_path: Path) -> None:
    """Positive control: reintroduce the wall clock and the comparison goes red.

    Edits a throwaway copy of ``manuscript_variables.py`` so the manuscript date
    is derived from ``datetime.now`` again — exactly the defect this module
    exists to catch — then shows the same fingerprint comparison the gate
    performs now reports drift.
    """
    sandbox = _sandbox(tmp_path)
    module = sandbox / "src" / "goldfinger" / "manuscript_variables.py"
    source = module.read_text(encoding="utf-8")

    marker = "    return str(raw).strip()\n"
    assert source.count(marker) == 1, (
        "positive control could not locate its patch site — if _manuscript_date "
        "changed shape, update this control rather than letting it no-op"
    )
    leaking = source.replace(
        marker,
        "    import datetime as _dt\n\n"
        '    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f UTC")\n',
    )
    assert leaking != source, "the patch did not apply"
    module.write_text(leaking, encoding="utf-8")

    _regenerate(sandbox)
    first = _fingerprint(sandbox)
    _regenerate(sandbox)
    second = _fingerprint(sandbox)

    drifted = sorted(name for name, digest in first.items() if second[name] != digest)
    assert drifted, (
        "the determinism gate is green by construction: a wall clock was "
        "reintroduced into the token map and the comparison still passed"
    )
    assert "output/data/manuscript_variables.json" in drifted
