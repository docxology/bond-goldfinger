# Agent Instructions — goldfinger (GRAND SLAM)

Concrete operational instructions for an agent working in this film package.
Read this before modifying anything. Background is in
[`architecture.md`](architecture.md) and [`testing_philosophy.md`](testing_philosophy.md).

## Orientation (do this first)

```bash
cd <this package root>              # the checkout that holds pyproject.toml
uv sync --extra dev                 # installs deps; bond-api/bond-utilities resolve from sibling checkouts
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run python scripts/execute.py    # see all six models produce real numbers
cat docs/_generated/COUNTS.md       # current structural counts and headlines
```

If `uv sync` cannot resolve `bond-api`, the six concept modules still import
standalone — only `mission.py` and the phase CLIs need the protocol. Build
against the pure core and note the blocked integration in `TODO.md` rather than
stalling.

## Hard boundaries

- **Scope**: work only inside this package directory. Never touch a sibling
  BOND package, the bond root files, or the template repo.
- **Published tree**: `origin` is the GitHub repository
  (`docxology/bond-goldfinger`). Land a change through an ordinary branch, pull
  request and merge — never a force-push or a history rewrite — and commit this
  package's paths only.
- **Never change the frozen protocol surface.** `goldfinger.mission` must keep
  exporting `MissionProvider` (with `film = "goldfinger"` and the five lifecycle
  methods), the module-level `GADGETS` registry, `register_market_gadgets`, and
  `build_provider`. bond-cli, the coordinator reconcile, and the orchestrator
  consume these across the fleet. Deepen the internals freely; do not rename the
  surface. `tests/test_protocol_integration.py` is the tripwire.

## Where code goes

| If you are adding… | Put it in… |
|---|---|
| A model, formula, or algorithm | A module in `src/goldfinger/` — pure, typed, docstringed, no I/O, no `bond_api` |
| Something the mission should report | An `_*_intel()` helper in `mission.py`, surfaced through the `results` payload |
| A new number for the manuscript | `generate_variables()` **and** the `GOLDFINGER_TOKENS` tuple, then the `{{TOKEN}}` in the prose |
| A new figure | A `plot_*` renderer in `figures/plots.py`, its name in `FIGURE_RENDERERS`, a label row in `manuscript/SYNTAX.md`, and an anchor in `03_results.md` |
| A CLI | `scripts/` — argument parsing, printing, and file writing only; no computation |

Never place business logic in `scripts/`. A script that computes something is a
defect even if it works.

## Non-negotiables

- **No mocks.** No `MagicMock`, `mocker.patch`, `unittest.mock`, or
  `create_autospec`. The domain core is pure functions; call them for real.
- **Determinism.** Fixed inputs, no untracked RNG, and no clock reachable from
  a persisted artifact. Do not reintroduce a `now=` parameter: an injectable
  clock still leaks on the default path, and pinned-`now` tests hid exactly
  that defect here once. Dates come from `paper.date` in
  `manuscript/config.yaml` (`MANUSCRIPT_DATE`, required, no default).
  `tests/test_regeneration_determinism.py` regenerates twice across a
  wall-clock gap and compares bytes.
- **No hand-authored metrics in prose.** Every number in `manuscript/` arrives
  as a `{{TOKEN}}`; every number in `docs/` either cites
  `_generated/COUNTS.md` or describes the gate. Counts of modules, figures, and
  tokens are numbers too — they have tokens. The scan enforces this only for
  values that are numeric literals of three or more characters; counts and
  category words are listed as an acknowledged hole in
  `_UNSCANNABLE_RESULT_TOKENS`. Never write a count of something *outside* this
  package (sibling packages, the fleet) — there is no token or gate for it.
- **Single source of truth for reference intel.** Parameters live in the module
  `REFERENCE_*` constants. The adapter, the token map, and the figures read
  those constants. Do not repeat a literal in a second place — that is how
  three "authoritative" values diverge. The `grand_slam:` block in
  `manuscript/config.yaml` is a mirror no code loads; `test_reference_intel.py`
  pins it to the constants, so adding a `REFERENCE_*` constant means updating
  the mirror too.
- **Gates must be able to fail.** If you add an assertion, be able to state the
  input that turns it red, and prefer adding that input as a positive-control
  test. See `test_the_anti_hardcode_gate_can_actually_fail`.
- **Type hints and docstrings** on every public function; ruff and mypy clean.
- **No exemplar lineage strings.** When documenting the lineage grep,
  bracket-split the pattern so the doc does not trip its own check.

## The full gate

Run all of it before declaring done, and read the output rather than the exit
code alone:

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/ tests/
uv run ruff format --check src/ scripts/ tests/
uv run mypy src/goldfinger scripts
rg -n "template[_]code_project" .        # expect zero hits
```

Then regenerate anything derived and confirm the tree is clean:

```bash
uv run python scripts/z_generate_manuscript_variables.py
uv run python scripts/z_generate_counts.py --tests <N> --coverage <PCT>
git status
```

## Common traps in this package

- Adding a `.py` file to `src/goldfinger/` silently increments
  `GOLDFINGER_MODULE_COUNT`, because that count is derived from the package
  directory. If the new file is plumbing rather than a concept model, add it to
  `_NON_CONCEPT_MODULES` in `manuscript_variables.py`.
- Adding a token to `generate_variables()` without adding it to
  `GOLDFINGER_TOKENS` (or vice versa) fails
  `test_declared_token_tuple_equals_the_generated_key_set`. That is intended —
  the tuple is the declared contract.
- Formatting a small probability with too few digits silently rounds it to
  `0.0`. Sequential vault penetration is ~0.009%; check the rendered token, not
  just the float.
- `effective_burn_range` returns a `BurnRangeResult`, not a bare float: a zero
  `range_m` means either "melts only at focus" or "never melts in the window",
  and the companion `burns_at_focus` flag is what distinguishes them. Read the
  flag instead of re-running `melt_time_at_distance(..., 0.0)`.
