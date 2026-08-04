# goldfinger — agent directives (GRAND SLAM)

Film package in the PROJECT BOND suite. Scope is **exactly this directory** —
never touch sibling packages, bond root files, or the template repo.

## Identity

- Film: Goldfinger (1964) · mission codename GRAND SLAM
- Package: `goldfinger` · BOND-API slug: `goldfinger`
- Local-only tree: no remote, never push; path-scoped commits only.

## Architecture / layer contract

| Surface | Rule |
|---|---|
| `src/goldfinger/market_attack.py`, `vault_security.py`, `laser_physics.py` | **Pure domain core**: no I/O, no bond-api, no infrastructure imports; deterministic; importable standalone |
| `src/goldfinger/mission.py` | Thin BOND-API adapter: the only module that imports `bond_api`; implements `MissionProvider` (brief/recon/plan/execute/debrief); registers gadgets |
| `src/goldfinger/manuscript_variables.py`, `figures/` | Result-token hydration + figure rendering; deterministic |
| `scripts/` | Thin CLIs per mission phase; sys.path bootstrap `# noqa: E402` |

The pure core must remain importable **without** bond-api so the package keeps
working if the path dependency ever fails; keep bond-api imports confined to
`mission.py`.

## Protocol integration

- `bond-api` is a local path dependency (see `pyproject.toml`
  `[tool.uv.sources]`). Run `uv sync --extra dev` before pytest.
- `src/goldfinger/mission.py` exposes `MissionProvider` at module top level;
  discovery by slug `goldfinger` binds it and verifies identity.

## Guardrails

- No mock framework (no `MagicMock`/`mocker.patch`/`unittest.mock`). Real data
  + computation only.
- `>=90%` line+branch coverage on `src/goldfinger`.
- Deterministic: fixed seed (`2026`), no untracked RNG, no wall-clock in
  persisted results.
- Manuscript metrics injected as `{{TOKEN}}`s from `manuscript_variables.py` —
  never hand-author numbers in prose. Live token cross-reference test gates it.
- Zero leftover exemplar-lineage placeholder strings (aim zero; see TODO). When
  documenting the lineage grep, bracket-split the pattern so docs don't trip
  their own gate.
- Update README/AGENTS/TODO for THIS package (done in phase 2).

## Quality gates

```bash
uv run python -m pytest tests/ --cov=src/goldfinger --cov-fail-under=90
uv run ruff check src/ scripts/ tests/ && uv run ruff format --check src/ scripts/ tests/
uv run mypy src/goldfinger scripts
```
