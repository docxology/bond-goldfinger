# Agent Instructions — goldfinger (GRAND SLAM)

Operational constraints for AI agents working in this film package. Read these
before modifying this project.

## Operational constraints

- **Scope**: work only inside this package directory. Never touch sibling
  BOND packages, bond root files, or the template repo.
- **Local-only**: there is no remote. Never push. Commit path-scoped within
  this repo only.
- **No mocks**: tests use real computation and real data only. No
  `MagicMock`, `mocker.patch`, or `unittest.mock`.
- **Determinism**: fixed seeds, no untracked RNG, no wall-clock dependence in
  persisted results. Figure output is byte-deterministic.
- **Layer contract**: the pure domain modules (`market_attack`,
  `vault_security`, `laser_physics`) must stay infrastructure-free and
  importable without `bond-api`. Only `mission.py` may import `bond_api`.
- **Manuscript metrics**: inject all result numbers as `{{TOKEN}}`s from
  `manuscript_variables.py`; never hardcode measured values in prose.
- **Lineage**: remove stray exemplar-lineage placeholder strings; when
  documenting the lineage grep, bracket-split the pattern so docs don't trip
  their own gate.

## Consensus procedures

- Run the full gate before declaring done:
  `uv run python -m pytest tests/ --cov=src/goldfinger --cov-fail-under=90`,
  `uv run ruff check src/ scripts/ tests/`,
  `uv run ruff format --check src/ scripts/ tests/`,
  `uv run mypy src/goldfinger scripts`.
- Verify `git status` is clean after committing.

## References

- `docs/architecture.md` — module boundaries and data flow.
- `docs/testing_philosophy.md` — how tests are written here.
- `../manuscript/AGENTS.md` — manuscript/token protocol.
