---
name: goldfinger
description: Build/maintain the goldfinger (GRAND SLAM) PROJECT BOND film package — market cornering, vault defense, laser threat physics.
---

# goldfinger — GRAND SLAM

PROJECT BOND film package for Goldfinger (1964). Scope = this directory only,
local-only (no remote), path-scoped commits.

## Concepts built (phase 2)

- `src/goldfinger/market_attack.py` — gold-market cornering: constant-elasticity
  inverse demand + tatonnement supply-shock price dynamics (`simulate_corner`,
  `shocked_equilibrium_price`, `price_gain`).
- `src/goldfinger/vault_security.py` — Fort Knox-style layered defense:
  weighted defense-in-depth score + product-rule sequential penetration
  (`layered_security_score`, `penetration_probability`, `expected_breach_time`).
- `src/goldfinger/laser_physics.py` — laser threat physics: energy-balance
  burn-through time vs material/power (`burn_through_time`).
- `src/goldfinger/mission.py` — BOND-API `MissionProvider` adapter (film
  `goldfinger`, codename `GRAND SLAM`), gadget registration, provenance.
- `manuscript_variables.py` (25 tokens), `figures/plots.py` (3 figures),
  thin `scripts/` CLIs.

## Quick reference

```bash
uv sync --extra dev
uv run python scripts/debrief.py
uv run python scripts/z_generate_manuscript_variables.py
uv run python -m pytest tests/ --cov=src/goldfinger --cov-fail-under=90
uv run ruff check src/ scripts/ tests/ && uv run ruff format --check src/ scripts/ tests/
uv run mypy src/goldfinger scripts
```

## Pitfalls

- Keep the pure core importable WITHOUT bond-api; only `mission.py` imports it.
- Inject all result metrics as `{{TOKEN}}`s; never hand-author numbers in prose.
- The mission adapter uses `bond_api` (FROZEN) — do not invent protocol types.
- Zero mocks; fixed seed 2026; `output/` is git-ignored.
