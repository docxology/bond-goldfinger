# Reproducibility

## Deterministic regeneration

The package is fully deterministic. Re-running the mission or regenerating the
manuscript variables reproduces byte-identical results:

```bash
uv run python scripts/z_generate_manuscript_variables.py
```

which rewrites `output/data/manuscript_variables.json` (25 tokens) and the
three concept figures under `output/figures/`. Because inputs are fixed, the
computed result tokens (`MARKET_*`, `VAULT_*`, `LASER_*`) are stable; only the
`GENERATION_TIMESTAMP` (and the derived `GOLDFINGER_VERSION_HASH`) vary between
runs.

## Verification gate

The enforced quality gate, run from the package root:

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
```

Coverage is measured on `src/goldfinger/` only (tests are excluded). The suite
exercises every model error branch, every mission stage, protocol discovery
and serialization, the token cross-reference gate, figure rendering, and
the thin CLI smoke paths — all with real computation, no mocking.

## Change policy

- Result metrics in the prose are injected from `manuscript/config.yaml` and
  `src/goldfinger/manuscript_variables.py`; do not hardcode numbers in prose.
- The pure domain modules must remain infrastructure-free and importable
  without `bond-api` (mission.py is the only module that imports it).
- No leftover template scaffolding: `sys.path` discovery assumes the package
  layout of this film; keep `src/goldfinger/mission.py` as the adapter.
