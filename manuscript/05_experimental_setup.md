# Experimental Setup

## Reference intel

The deterministic reference parameters used by the pure domain core are
declared in `manuscript/config.yaml` under `grand_slam:` and mirrored in each
module's `REFERENCE_*` constant:

- **Market**: reference price `${{MARKET_REFERENCE_PRICE}}`/oz, normalized
  floatable supply index `100.0`, fraction removed
  `{{MARKET_FRACTION_REMOVED}}%`, elasticity `{{MARKET_ELASTICITY}}`,
  tatonnement adjustment `0.4`, steps `40`.
- **Vault**: six layers (perimeter, fence, guard response, vault door,
  combination lock, gold storage) each rated in `[0,1]`; weights in
  `DEFAULT_WEIGHTS`.
- **Laser**: power `{{LASER_POWER_W}}` W, spot area `1e-5` m², steel density
  `7800` kg/m³, thickness `{{LASER_THICKNESS_MM}}` mm, specific heat
  `500` J/(kg·K), $\Delta T$ `1500` K, absorptivity `0.6`.

## Determinism policy

All computations use fixed seeds (`seed = 2026` in the mission adapter) and
make no random draws. Persisted artifacts carry no wall-clock dependence
(`wall_time_s = 0.0` in provenance; the only varying timestamp is the
`GENERATION_TIMESTAMP` manuscript token, which defaults to
{{GENERATION_TIMESTAMP}}). Figure outputs are byte-deterministic for fixed
inputs.

## Software environment

- Python: as resolved by `uv` (the package requires `>=3.10`)
- Dependencies: NumPy, Matplotlib, PyYAML, and the frozen `bond-api` protocol
  (local path dependency under
  `/Users/4d/Documents/GitHub/template/projects/working/bond/bond-api`)
- Dev: pytest, pytest-cov, mypy, ruff, types-PyYAML

## Mission adapter

The BOND-API `MissionProvider` (`src/goldfinger/mission.py`) wraps the three
models and registers three gadgets (`market_corner`, `vault_defense`,
`laser_threat`) with a `GadgetRegistry`. It is discoverable by slug
`goldfinger` on `sys.path` and drives the full brief–recon–plan–execute–
debrief lifecycle with deterministic provenance.
