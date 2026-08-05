# Reproducibility

## Deterministic regeneration

The package is fully deterministic. Re-running the mission or regenerating the
manuscript variables reproduces identical results:

```bash
uv run python scripts/z_generate_manuscript_variables.py
```

which rewrites `output/data/manuscript_variables.json`
({{GOLDFINGER_TOKEN_COUNT}} tokens) and the {{GOLDFINGER_FIGURE_COUNT}}
concept figures under `output/figures/`. Every persisted byte is a function of
the committed tree alone, so running that command twice — on different days,
on different machines — produces byte-identical files. Nothing in the token
map reads a clock: the manuscript's date is the committed `paper.date` in
`manuscript/config.yaml` (`MANUSCRIPT_DATE` = {{MANUSCRIPT_DATE}}), and
`GOLDFINGER_VERSION_HASH` hashes the whole map, which makes it a content
identifier rather than a run identifier.

That property is enforced, not asserted:
`tests/test_regeneration_determinism.py` copies the tree to a scratch
directory, runs the real generator twice with a wall-clock gap between the
runs, and compares every emitted byte — the JSON, all
{{GOLDFINGER_FIGURE_COUNT}} figures, and the generated counts file. The same
file carries a positive control that reintroduces a clock-derived value into
the map and shows the comparison goes red, so the gate is known to be able to
fail.

The token count and figure count above are themselves generated, not typed:
`GOLDFINGER_TOKEN_COUNT` is the length of the declared `GOLDFINGER_TOKENS`
tuple, `GOLDFINGER_FIGURE_COUNT` is the length of
`goldfinger.figures.FIGURE_RENDERERS`, and `GOLDFINGER_MODULE_COUNT`
(= {{GOLDFINGER_MODULE_COUNT}}) is computed by scanning the package directory
for concept modules. A test asserts the declared token tuple is exactly the key
set `generate_variables()` produces, so a token added to one and not the other
fails the suite rather than silently drifting into the prose.

## Verification gate

The enforced quality gate, run from the package root:

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/ tests/ && uv run ruff format --check src/ scripts/ tests/
uv run mypy src/goldfinger scripts
```

Coverage is measured on `src/goldfinger/` only (tests are excluded) and the
floor is 90% line **and** branch. The suite exercises every model error branch
through a real call with a real bad argument, every mission stage, protocol
discovery and serialization, the token cross-reference gate, figure rendering
determinism, and the thin CLI smoke paths — all with real computation, no
mocking framework anywhere.

## Change policy

- Result metrics in the prose are injected by
  `src/goldfinger/manuscript_variables.py` from the module `REFERENCE_*`
  constants; do not hardcode numbers in prose, including counts of modules,
  figures, tokens, or tests. The hardcode scan cannot police the count and
  category tokens (their values are too short or too word-like to search for),
  so that part of the rule is enforced by review, not by a gate.
- The pure domain modules must remain infrastructure-free and importable
  without `bond-api` (`mission.py` is the only module that imports it).
- Reference parameters live in exactly one place — the module `REFERENCE_*`
  constants. The mission adapter, the token map, and the figures all read those
  constants rather than repeating a literal, so the three cannot report
  different postures. `manuscript/config.yaml`'s `grand_slam:` block is a
  read-only mirror that no code loads; `tests/test_reference_intel.py` pins it
  to the constants value-for-value and also pins the two laser models to one
  physical steel plate.
