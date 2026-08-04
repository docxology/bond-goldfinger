# goldfinger — Special-Agent Mission Software (GRAND SLAM)

Film: **Goldfinger** (1964) · Mission codename: **GRAND SLAM**

A PROJECT BOND film package that models the three operational concepts of the
film as small, deterministic, fully-tested scientific modules — then exposes
them as a protocol-compliant BOND-API mission.

## Mission concept

Auric Goldfinger's scheme is treated as a *quantitative modelling exercise*:

1. **Market cornering** (`src/goldfinger/market_attack.py`) — Operation Grand
   Slam as a supply shock: removing a fraction of the floatable gold raises
   the clearing price along a constant-elasticity demand curve, and a
   tatonnement process traces convergence to the new equilibrium.
2. **Vault defense** (`src/goldfinger/vault_security.py`) — a Fort Knox-style
   layered assessment: per-layer ratings combine into a weighted
   defense-in-depth score, and sequential-penetration probability follows the
   product rule.
3. **Laser threat** (`src/goldfinger/laser_physics.py`) — burn-through time
   vs material and power from an energy-balance thermal model.

All three are pure (no I/O), deterministic (fixed seed, no wall-clock
dependence), and importable with only NumPy — they do **not** depend on
bond-api. `src/goldfinger/mission.py` is the only module that imports the
frozen BOND-API protocol, implementing the `MissionProvider` lifecycle
(brief / recon / plan / execute / debrief) and registering the mission's
gadgets.

## Layout

```
src/goldfinger/
  market_attack.py        # gold-market cornering model (GRAND SLAM supply shock)
  vault_security.py       # layered vault defense scoring + penetration
  laser_physics.py        # burn-through time vs material/power
  mission.py              # BOND-API MissionProvider adapter (GRAND SLAM)
  manuscript_variables.py # {{TOKEN}} hydration from manuscript/config.yaml
  figures/plots.py        # three concept figures -> output/figures/
scripts/
  brief.py recon.py plan.py execute.py debrief.py   # mission-phase CLIs
  z_generate_manuscript_variables.py                # tokens + figures
manuscript/               # identity + reference intel + numbered prose
tests/                    # real-data tests, zero mocks
```

## Install & run

```bash
uv sync --extra dev          # installs deps incl. the bond-api path dependency
uv run python scripts/debrief.py            # run the full mission flow
uv run python scripts/execute.py            # print the deterministic outcome
uv run python scripts/z_generate_manuscript_variables.py
```

## Verification gate

```bash
uv run python -m pytest tests/ --cov=src/goldfinger --cov-fail-under=90
uv run ruff check src/ scripts/ tests/ && uv run ruff format --check src/ scripts/ tests/
uv run mypy src/goldfinger scripts
```

Local-only working tree — there is no remote and this package is never pushed.
