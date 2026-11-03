# scripts/ — thin CLIs and the regenerators

`brief.py`, `recon.py`, `plan.py`, `execute.py` and `debrief.py` drive the mission protocol;
`z_generate_manuscript_variables.py` and `z_generate_counts.py` regenerate derived artifacts.

## Rules

- **Thin CLIs only**: argument parsing, printing and file writing, with a `sys.path` bootstrap
  marked `# noqa: E402`. Business logic lives in `src/goldfinger/`.
- **Regenerate derived artifacts after any structural change**:
  `uv run python scripts/z_generate_manuscript_variables.py` (tokens and figures) and
  `uv run python scripts/z_generate_counts.py --tests <N> --coverage <PCT>`. The `z_` prefix
  marks the generators; run them after the change they reflect.
- **Never hand-author a measured number in prose.** Metrics flow through
  `src/goldfinger/manuscript_variables.py` and land in `docs/_generated/COUNTS.md`.
- **Scope**: this package only; never sibling packages, bond root files or the template repo.
- `tests/test_scripts_smoke.py` covers these entry points; keep it passing when one changes.
