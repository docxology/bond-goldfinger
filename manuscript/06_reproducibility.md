# Reproducibility

## Deterministic regeneration

The package is fully deterministic. Re-running the mission or regenerating the
manuscript variables reproduces identical results:

```bash
uv run python scripts/z_generate_manuscript_variables.py
```

which rewrites `output/data/manuscript_variables.json`
({{GOLDFINGER_TOKEN_COUNT}} tokens) and the {{GOLDFINGER_FIGURE_COUNT}}
concept figures under `output/figures/`. Because inputs are fixed, the computed
result tokens (`MARKET_*`, `RESERVE_*`, `VAULT_*`, `LASER_*`) are stable; only
the `GENERATION_TIMESTAMP` — and the `GOLDFINGER_VERSION_HASH` derived from
the whole map — vary between runs.

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
