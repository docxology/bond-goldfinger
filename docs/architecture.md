# Architecture — goldfinger (GRAND SLAM)

The package follows the PROJECT BOND layer contract: a pure, infrastructure-free
domain core wrapped by a thin protocol adapter, with thin CLIs on top.

```
            ┌───────────────────────────────┐
            │  bond_api.protocol (FROZEN)    │  MissionProvider, run_mission
            └───────────────▲───────────────┘
                            │ implements
            ┌───────────────┴───────────────┐
            │  src/goldfinger/mission.py      │  MissionProvider adapter;
            │  (the ONLY bond_api import)     │  GadgetRegistry registration
            └───────────────▲───────────────┘
                            │ uses
   ┌──────────────┐ ┌───────┴───────┐ ┌───────────────┐
   │ market_attack│ │vault_security │ │ laser_physics │   PURE DOMAIN CORE
   │ corner model │ │ layer scoring │ │ burn-through  │   (no I/O, no bond_api,
   └──────┬───────┘ └──────┬────────┘ └───────┬───────┘    deterministic)
          └────────────────┴────────┬────────┘
                                    ▼
            ┌───────────────────────────────┐
            │ manuscript_variables.py         │   {{TOKEN}} hydration
            │ figures/plots.py                │   3 concept figures
            └───────────────┬───────────────┘
                            ▼
                    scripts/ (thin CLIs)
              brief|recon|plan|execute|debrief.py
              z_generate_manuscript_variables.py
```

## Module responsibilities

- **market_attack.py** — gold-market cornering. `effective_supply`,
  `shocked_equilibrium_price`, `price_gain`, `simulate_corner` (tatonnement
  trajectory), `corner_valuation`. Reference intel in `REFERENCE_MODEL`
  (TypedDict).
- **vault_security.py** — layered defense. `layered_security_score` (weighted
  average), `penetration_probability` (product rule over `LAYER_ORDER`),
  `expected_breach_time`, `weakest_layer`, `marginal_improvements`,
  `vault_security_verdict`. Reference ratings in `REFERENCE_RATINGS`.
- **laser_physics.py** — laser threat. `burn_through_time`,
  `power_for_burn_through`, `max_burn_thickness`, `laser_threat_severity`,
  `energy_to_burn`, `absorbed_power`. Reference physics in `REFERENCE_PHYSICS`.
- **mission.py** — the BOND-API `MissionProvider` (film `goldfinger`, codename
  `GRAND SLAM`). Computes deterministic intel from the three cores, returns a
  `MissionOutcome` with provenance, registers gadgets `market_corner`,
  `vault_defense`, `laser_threat`.
- **manuscript_variables.py** — `generate_variables()` reads
  `manuscript/config.yaml` and the reference constants, producing the 25-token
  map; `GOLDFINGER_TOKENS` is the documented token set.
- **figures/plots.py** — three renderers to `output/figures/`.
- **scripts/** — thin wrappers forwarding to the mission adapter; `# noqa:
  E402` on the sys.path bootstrap.

## Data flow

`manuscript/config.yaml` (`grand_slam:`) mirrors the module `REFERENCE_*`
constants. The mission adapter and `manuscript_variables.py` both consume the
constants, so the numbered prose and the mission outcome always agree. No
measured metric appears as a literal outside the token pipeline.
