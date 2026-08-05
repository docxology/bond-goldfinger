# Experimental Setup

## Reference intel

The deterministic reference parameters used by the pure domain core are
declared in `manuscript/config.yaml` under `grand_slam:` and mirrored in each
module's `REFERENCE_*` constant:

- **Market**: reference price `${{MARKET_REFERENCE_PRICE}}`/oz, normalized
  floatable supply index `100.0`, fraction removed
  `{{MARKET_FRACTION_REMOVED}}%`, elasticity `{{MARKET_ELASTICITY}}`,
  tatonnement adjustment `0.4`, steps `40`.
- **Reserve attack**: parity `1.0`, foreign rate `0.02`, interest elasticity
  `8.0`, initial credit `0.10`, credit growth `0.10` (Flood–Garber).
- **Vault**: six layers (perimeter, fence, guard response, vault door,
  combination lock, gold storage) each rated in `[0,1]`; weights in
  `DEFAULT_WEIGHTS`. Network zone graph in `vault_threat_network.REFERENCE_GRAPH`
  with hardening budget `10` at `0.5` effort/unit.
- **Laser**: power `{{LASER_POWER_W}}` W, spot area `1e-5` m², steel density
  `7800` kg/m³, thickness `{{LASER_THICKNESS_MM}}` mm, specific heat
  `500` J/(kg·K), $\Delta T$ `1500` K, absorptivity `0.6`; Gaussian beam intel
  (waist `{{LASER_WAIST_MM}}` mm, wavelength `1.064e-6` m, melt window
  `{{LASER_THREAT_WINDOW_S}}` s) in `laser_thermal.REFERENCE_BEAM`.

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

The BOND-API `MissionProvider` (`src/goldfinger/mission.py`) wraps the six
models and registers six gadgets (`market_corner`, `reserve_attack`,
`vault_defense`, `vault_hardening`, `laser_threat`, `laser_thermal`) with a
`GadgetRegistry`. It is discoverable by slug `goldfinger` on `sys.path` and
drives the full brief–recon–plan–execute–debrief lifecycle with deterministic
provenance. The adapter's public shape is stable; the mission internals
(assets, plan steps, outcome results, lessons) deepen with each phase.
