# goldfinger — Special-Agent Mission Software (GRAND SLAM)

Film: **Goldfinger** (1964) · Mission codename: **GRAND SLAM**

A PROJECT BOND film package that models the film's operational concepts as
small, deterministic, fully-tested scientific modules — across three attack
surfaces — then exposes them as a protocol-compliant BOND-API mission.

## Mission concept

Auric Goldfinger's scheme is treated as a *quantitative modelling exercise*
across six pure modules and three fronts:

**Macroeconomic attack (market + reserve)**
1. `market_attack.py` — Operation Grand Slam as a supply shock: removing a
   fraction of the floatable gold raises the clearing price along a
   constant-elasticity demand curve (tatonnement dynamics to the new
   equilibrium).
2. `reserve_attack.py` — the monetary front: a first-generation **speculative
   attack** (Flood–Garber) on the gold peg. Credit growth drains reserves; the
   peg collapses the moment the shadow floating rate crosses parity — an attack
   strictly *before* gradual exhaustion.

**Vault defense (layered + network)**
3. `vault_security.py` — Fort Knox-style layered assessment: per-layer ratings
   combine into a weighted defense-in-depth score; sequential-penetration
   probability follows the product rule.
4. `vault_threat_network.py` — the network front: minimum-effort vault
   penetration (Dijkstra over a zone graph, weak path through the secret
   tunnel) and greedy network hardening that raises the intruder's required
   effort.

**Laser threat (scalar + thermal)**
5. `laser_physics.py` — energy-balance burn-through time vs material and
   power.
6. `laser_thermal.py` — the spatio-temporal front: Gaussian beam focusing
   (Rayleigh range, defocusing), Carslaw–Jaeger heat conduction, and the
   effective burn range within a threat window.

All six are pure (no I/O), deterministic (fixed seed, no wall-clock
dependence), and importable with only NumPy — they do **not** depend on
bond-api. `src/goldfinger/mission.py` is the only module that imports the
frozen BOND-API protocol, implementing the `MissionProvider` lifecycle
(brief / recon / plan / execute / debrief) and registering six gadgets. The
adapter's **public shape is stable across phases** (film, lifecycle methods,
`GADGETS` registry, `register_market_gadgets`); only its internals deepen.

## Layout

```
src/goldfinger/
  market_attack.py        # gold-market cornering (supply-shock price dynamics)
  reserve_attack.py       # speculative attack on the gold peg (macro)
  vault_security.py       # layered vault defense scoring + penetration
  vault_threat_network.py # graph penetration + network hardening
  laser_physics.py        # burn-through time vs material/power
  laser_thermal.py        # Gaussian-beam + heat-conduction engagement
  mission.py              # BOND-API MissionProvider adapter (GRAND SLAM)
  manuscript_variables.py # {{TOKEN}} hydration from manuscript/config.yaml
  figures/plots.py        # six concept figures -> output/figures/
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
