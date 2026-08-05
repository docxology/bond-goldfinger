# goldfinger — agent directives (GRAND SLAM)

Film package in the PROJECT BOND suite. Scope is **exactly this directory** —
never touch sibling packages, bond root files, or the template repo.

Detailed operational instructions: [`docs/agent_instructions.md`](docs/agent_instructions.md).
Structure: [`docs/architecture.md`](docs/architecture.md). Test doctrine:
[`docs/testing_philosophy.md`](docs/testing_philosophy.md).

## Identity

- Film: Goldfinger (1964) · mission codename GRAND SLAM
- Package: `goldfinger` · BOND-API slug: `goldfinger`
- Local-only tree: no remote, never push; path-scoped commits only.

## Build, test, verify

```bash
cd projects/working/bond/goldfinger
uv sync --extra dev          # deps incl. the bond-api path dependency — run before pytest

# The gate. Read the output, not just the exit code.
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/ tests/
uv run ruff format --check src/ scripts/ tests/
uv run mypy src/goldfinger scripts
rg -n "template[_]code_project" .        # expect zero hits

# Regenerate derived artifacts after any structural change
uv run python scripts/z_generate_manuscript_variables.py       # tokens + figures
uv run python scripts/z_generate_counts.py --tests <N> --coverage <PCT>

git status                   # expect clean after committing
```

Focused runs: `uv run pytest tests/test_<module>.py -v`, or
`uv run pytest tests/ -k <behaviour> -v`. Coverage is measured on
`src/goldfinger/` only; the floor is 90% line **and** branch. Currently measured
figures live in `docs/_generated/COUNTS.md` — cite that file rather than
copying a number into prose.

## Architecture / layer contract

| Surface | Rule |
|---|---|
| `market_attack.py`, `reserve_attack.py`, `vault_security.py`, `vault_threat_network.py`, `laser_physics.py`, `laser_thermal.py` | **Pure domain core** (six modules, three attack surfaces): no I/O, no `bond_api`, no infrastructure imports; deterministic; importable standalone |
| `mission.py` | Thin BOND-API adapter: the only module that imports `bond_api`; implements `MissionProvider` (brief/recon/plan/execute/debrief); registers six gadgets |
| `manuscript_variables.py`, `figures/` | Token hydration, `COUNTS.md` rendering, and figure rendering; deterministic; import the concept modules but never the adapter |
| `scripts/` | Thin CLIs only — argument parsing, printing, file writing. No business logic. `sys.path` bootstrap carries `# noqa: E402` |
| `__init__.py` | Public API plus the shared mission constants the adapter and the token map both read |

The pure core must remain importable **without** `bond-api` so the package keeps
working if the path dependency ever fails; keep `bond_api` imports confined to
`mission.py`.

## Protocol stability (deepen inside, never break the surface)

The adapter's public shape is **frozen across phases**: the module path
`goldfinger.mission`, the class name `MissionProvider`, the `film` value, the
five lifecycle methods, the module-level `GADGETS` registry,
`register_market_gadgets`, and `build_provider`. bond-cli, the coordinator
reconcile, and the orchestrator consume them across the fleet. Deepening happens
*inside* — new concept modules, richer assets/plan/outcome payloads — never in
the discovery contract. `tests/test_protocol_integration.py` is the tripwire.

## Guardrails

- No mock framework (`MagicMock`, `mocker.patch`, `unittest.mock`,
  `create_autospec`). Real data and real computation only — the domain core is
  pure functions, so there is nothing to mock.
- Deterministic: seed `MISSION_SEED` declared in `__init__.py` (no random draws
  are made), no untracked RNG, no wall-clock in persisted results. Inject `now=`
  wherever a timestamp would otherwise leak.
- **No hand-authored metrics anywhere.** Manuscript numbers are `{{TOKEN}}`s
  from `manuscript_variables.py`; doc numbers cite `docs/_generated/COUNTS.md`
  or describe the gate. Counts of modules, figures, and tokens are numbers too
  — they have derived tokens (`GOLDFINGER_MODULE_COUNT`,
  `GOLDFINGER_FIGURE_COUNT`, `GOLDFINGER_TOKEN_COUNT`).
- **Single source of truth for reference intel.** Parameters live in the module
  `REFERENCE_*` constants, mirrored by `manuscript/config.yaml`. The adapter,
  the token map, and the figures all read those constants; never repeat a
  literal in a second place.
- **Every gate must be able to fail.** State the input that turns a new
  assertion red, and prefer shipping that input as a positive-control test.
- Type hints and docstrings on every public function; ruff and mypy clean.
- Zero leftover exemplar-lineage placeholder strings. When documenting the
  lineage grep, bracket-split the pattern so docs don't trip their own gate.
- Keep `README.md`, this file, `TODO.md`, and `docs/` accurate to the package as
  it actually is. A stale doc is a defect, not a cosmetic issue.
