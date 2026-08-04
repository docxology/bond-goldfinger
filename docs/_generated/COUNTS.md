# Live counts — goldfinger (GRAND SLAM)

Volatile, generated counters. Do not hardcode measured test totals or coverage
elsewhere; read them from here or regenerate.

- Test suite: **79 collected** (live gate: 0 skipped, 0 failed).
- Coverage on `src/goldfinger/` (line + branch): **97.3%** (gate: >=90%).
- Manuscript tokens: **25**.
- Figures: **3** (`market_corner_trajectory`, `vault_layered_score`,
  `laser_burn_through`).
- Result headline values (deterministic, from the pure core):
  - MARKET_PRICE_GAIN_PCT ≈ **33.0%**
  - VAULT_SCORE ≈ **0.780** (verdict *medium*), penetration ≈ **0.009%**
  - LASER_BURN_THROUGH_S ≈ **0.98 s**

Regenerate: `uv run python scripts/z_generate_manuscript_variables.py`
