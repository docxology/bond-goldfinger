# Live counts — goldfinger (GRAND SLAM)

Volatile, generated counters. Do not hardcode measured test totals or coverage
elsewhere; read them from here or regenerate.

- Test suite: **119 collected** (live gate: 0 skipped, 0 failed).
- Coverage on `src/goldfinger/` (line + branch): **96.6%** (gate: >=90%).
- Pure domain modules: **6** (`market_attack`, `reserve_attack`,
  `vault_security`, `vault_threat_network`, `laser_physics`, `laser_thermal`).
- Manuscript tokens: **39**.
- Figures: **6** (`market_corner_trajectory`, `reserve_crisis`,
  `vault_layered_score`, `vault_network`, `laser_burn_through`,
  `laser_engagement`).
- Result headline values (deterministic, from the pure core):
  - MARKET_PRICE_GAIN_PCT ≈ **33.0%**
  - RESERVE_ATTACK_TIME ≈ **5.19** units (sudden, before `RESERVE_FLOOR_TIME`), depreciation ≈ **336%**
  - VAULT_SCORE ≈ **0.780** (verdict *medium*), penetration ≈ **0.009%**
  - VAULT_MIN_EFFORT ≈ **15.2** (secret tunnel) → hardened **20.2**
  - LASER_BURN_THROUGH_S ≈ **0.98 s**
  - LASER_EFFECTIVE_RANGE_M ≈ **65 m** (Rayleigh range ≈ 9.4 m)

Regenerate: `uv run python scripts/z_generate_manuscript_variables.py`
