# goldfinger — Special-Agent Mission Software (GRAND SLAM)

Film: **Goldfinger** (1964) · Mission codename: **GRAND SLAM**

A PROJECT BOND film package that models the film's operational concepts as
small, deterministic, fully-tested scientific modules — across three attack
surfaces — then exposes them as a protocol-compliant BOND-API mission.

## The film, mapped to software

Auric Goldfinger's scheme is treated as a *quantitative modelling exercise*.
Each of the film's three technical ideas gets two modules: a closed-form model,
and a structural model that captures what the closed form cannot express.

| Film concept | Closed-form model | Structural model |
|---|---|---|
| Corner the gold market ("Operation Grand Slam") | `market_attack` — supply shock along a constant-elasticity demand curve | `reserve_attack` — speculative attack that collapses the gold peg itself |
| Breach Fort Knox | `vault_security` — layered defence-in-depth scoring | `vault_threat_network` — the intruder's actual route through the zone graph |
| The industrial laser | `laser_physics` — energy-balance burn-through time | `laser_thermal` — Gaussian defocusing plus heat conduction over range |

The film is the spec; the code is the implementation. No stubs, no lorem ipsum.

## Modules

Pure domain core — no I/O, no `bond_api`, no infrastructure imports, fully
deterministic, importable with only the standard library and NumPy:

| Module | Computes |
|---|---|
| `src/goldfinger/market_attack.py` | Effective supply after sterilisation, the shocked clearing price $P_0(S_0/S_\text{eff})^{1/\eta}$, fractional corner gain, the tâtonnement trajectory, and tolerance-based convergence (`convergence_residual`, `has_converged`) |
| `src/goldfinger/reserve_attack.py` | The first-generation speculative attack (Flood–Garber): reserve drain under a fixed peg, the rational-expectations shadow floating rate, the attack time at which it reaches parity, the *later* gradual-exhaustion floor, and post-float depreciation |
| `src/goldfinger/vault_security.py` | Weighted defence-in-depth score, product-rule sequential penetration probability, expected breach time, weakest layer, marginal fortification priorities, and the severity verdict |
| `src/goldfinger/vault_threat_network.py` | Deterministic Dijkstra minimum-effort intrusion path over the vault zone graph (the weak path runs through the secret tunnel), per-edge criticality, and greedy budget hardening that raises the intruder's required effort |
| `src/goldfinger/laser_physics.py` | Heat load of the illuminated material column, absorbed power, burn-through time, and its inverses for required power and maximum burnable thickness, plus threat-severity binning |
| `src/goldfinger/laser_thermal.py` | Gaussian beam Rayleigh range and spot growth with distance, absorbed flux, the Carslaw–Jaeger constant-flux surface temperature, surface melt time, and the effective burn range within a threat window |

Adapter and plumbing:

| Module | Role |
|---|---|
| `src/goldfinger/mission.py` | The BOND-API `MissionProvider` adapter — the only module that imports `bond_api` |
| `src/goldfinger/manuscript_variables.py` | Hydrates the `{{TOKEN}}` map — identity from `manuscript/config.yaml`, every intel value from the module `REFERENCE_*` constants; also defines the rendered-file set and renders `docs/_generated/COUNTS.md` |
| `src/goldfinger/figures/plots.py` | One deterministic PNG renderer per concept model, listed in `figures.FIGURE_RENDERERS` |
| `src/goldfinger/__init__.py` | Public API and the shared mission constants (`FILM`, `CODENAME`, `MISSION_SEED`, `LASER_SEVERITY_THRESHOLD_W`, `LASER_STANDOFF_RANGE_M`) |

## The MissionProvider surface

`src/goldfinger/mission.py` implements the frozen BOND-API protocol
structurally — no inheritance. The orchestrator discovers it by importing
`goldfinger.mission` and binding the class whose `film` matches the slug.

```python
from goldfinger.mission import GADGETS, MissionProvider, build_provider, register_market_gadgets

provider = build_provider()          # film == "goldfinger"
brief    = provider.brief()          # MissionBrief: codename, objectives, assets, constraints
report   = provider.recon(request)   # ReconReport: findings
plan     = provider.plan(brief)      # MissionPlan: one step per model, plus synthesis
outcome  = provider.execute(plan)    # MissionOutcome: results + Provenance(seed, hash, version)
debrief  = provider.debrief(outcome) # Debrief: outcome + lessons
```

`outcome.results` is keyed `corner`, `reserve`, `vault`, `vault_network`,
`laser`, `laser_thermal`, plus `steps_completed` and `all_converged`. The
module-level `GADGETS` registry receives six concept callables via
`register_market_gadgets()`: `market_corner`, `reserve_attack`,
`vault_defense`, `vault_hardening`, `laser_threat`, `laser_thermal`.

**This surface is frozen.** bond-cli, the coordinator reconcile, and the
orchestrator consume it across the fleet, so the module path, class name, `film`
value, five method names, `GADGETS`, `register_market_gadgets`, and
`build_provider` do not change between phases. Everything behind them —
assets, plan steps, result payloads, the concept modules themselves — is free to
deepen. See [`docs/architecture.md`](docs/architecture.md).

## Layout

```
src/goldfinger/       six concept modules + mission adapter + token map + figures/
scripts/              thin CLIs: brief recon plan execute debrief
                      z_generate_manuscript_variables.py  z_generate_counts.py
manuscript/           config.yaml (identity + intel mirror), numbered prose, references.bib
docs/                 architecture, testing philosophy, agent instructions, _generated/
tests/                real-data tests, zero mocks, one file per module
```

## Install and run

```bash
uv sync --extra dev                                    # deps incl. the bond-api path dependency

uv run python scripts/brief.py                         # mission brief
uv run python scripts/recon.py "survey the vault"      # recon findings
uv run python scripts/plan.py                          # ordered plan steps
uv run python scripts/execute.py                       # all six models, with provenance (also writes output/data/grand_slam_record.json)
uv run python scripts/debrief.py                       # full lifecycle + lessons

uv run python scripts/z_generate_manuscript_variables.py   # tokens + figures
uv run python scripts/z_generate_counts.py --tests <N> --coverage <PCT>   # docs/_generated/COUNTS.md (bare form drops the measured lines)
```

The six concept modules import standalone without `bond-api`; only
`mission.py` and the phase CLIs need the protocol.

## Verification gate

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/ tests/ && uv run ruff format --check src/ scripts/ tests/
uv run mypy src/goldfinger scripts
```

The floor is **90% line and branch** coverage on `src/goldfinger/`, zero
failures, zero skips, and no mocking framework anywhere. Current measured
figures live in [`docs/_generated/COUNTS.md`](docs/_generated/COUNTS.md), which
is generated — they are deliberately not restated here, because a number typed
into a README rots the next time someone adds a test.

Published working tree — `origin` is `docxology/bond-goldfinger`; changes land through an ordinary
branch, pull request and merge, never a force-push or a history rewrite.
