"""Subprocess smoke tests for the thin GRAND SLAM mission-phase CLIs."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _run_script(name: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(_PROJECT_ROOT / "scripts" / name), *args],
        capture_output=True,
        text=True,
        cwd=_PROJECT_ROOT,
        check=False,
    )


def test_brief_cli() -> None:
    proc = _run_script("brief.py")
    assert proc.returncode == 0
    assert "GRAND SLAM" in proc.stdout
    assert "corner the gold market" in proc.stdout


def test_recon_cli_with_goal() -> None:
    proc = _run_script("recon.py", "survey the vault")
    assert proc.returncode == 0
    assert "survey the vault" in proc.stdout
    assert "Findings" in proc.stdout


def test_plan_cli() -> None:
    proc = _run_script("plan.py")
    assert proc.returncode == 0
    assert "simulate_market_corner" in proc.stdout
    assert "assess_laser_threat" in proc.stdout


def test_execute_cli_reports_metrics() -> None:
    proc = _run_script("execute.py")
    assert proc.returncode == 0
    assert "shocked price $" in proc.stdout
    assert "vault defense" in proc.stdout
    assert "laser threat" in proc.stdout
    assert "provenance" in proc.stdout


def test_debrief_cli() -> None:
    proc = _run_script("debrief.py")
    assert proc.returncode == 0
    assert "success=True" in proc.stdout
    assert "Lessons learned" in proc.stdout


def test_generate_manuscript_variables_writes_artifacts(tmp_path: Path) -> None:
    # Run in a sandbox copy of the tree so we don't touch the real output/.
    import shutil

    sandbox = tmp_path / "pkg"
    shutil.copytree(
        _PROJECT_ROOT,
        sandbox,
        ignore=shutil.ignore_patterns(".venv", ".git", "output", "__pycache__"),
    )
    proc = subprocess.run(
        [sys.executable, "scripts/z_generate_manuscript_variables.py"],
        capture_output=True,
        text=True,
        cwd=sandbox,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    data_json = sandbox / "output" / "data" / "manuscript_variables.json"
    figs = sandbox / "output" / "figures"
    assert data_json.is_file()
    assert (figs / "market_corner_trajectory.png").is_file()
    assert (figs / "vault_layered_score.png").is_file()
    assert (figs / "laser_burn_through.png").is_file()
    import json

    payload = json.loads(data_json.read_text(encoding="utf-8"))
    assert "MARKET_PRICE_GAIN_PCT" in payload
    assert "VAULT_SCORE" in payload


def test_generate_counts_cli_writes_the_generated_file(tmp_path: Path) -> None:
    """The counts generator is a real generator, run in a sandbox copy."""
    import shutil

    sandbox = tmp_path / "pkg"
    shutil.copytree(
        _PROJECT_ROOT,
        sandbox,
        ignore=shutil.ignore_patterns(".venv", ".git", "output", "__pycache__"),
    )
    target = sandbox / "docs" / "_generated" / "COUNTS.md"
    target.unlink()
    proc = subprocess.run(
        [sys.executable, "scripts/z_generate_counts.py", "--tests", "151", "--coverage", "100.0"],
        capture_output=True,
        text=True,
        cwd=sandbox,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    assert target.is_file()
    body = target.read_text(encoding="utf-8")
    assert "**151 collected**" in body
    assert "**100.00%**" in body
    assert "Pure domain modules" in body
