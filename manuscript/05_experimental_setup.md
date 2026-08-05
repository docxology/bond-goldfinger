# Experimental Setup

## Reference intel

The deterministic reference parameters used by the pure domain core are
declared in `manuscript/config.yaml` under `grand_slam:` and mirrored in each
module's `REFERENCE_*` constant. Every value below is injected from that single
source of truth, so a change to the intel changes this section automatically.

**Market corner** (`market_attack.REFERENCE_MODEL`) — reference price
`${{MARKET_REFERENCE_PRICE}}`/oz clearing a normalized floatable-supply index
of `{{MARKET_SUPPLY_INDEX}}`; the corner sterilizes
`{{MARKET_FRACTION_REMOVED}}%` of that float against a constant demand
elasticity of `{{MARKET_ELASTICITY}}`. The tâtonnement runs `{{MARKET_STEPS}}`
steps at adjustment coefficient `{{MARKET_ADJUSTMENT}}`.

**Speculative reserve attack** (`reserve_attack.REFERENCE_ATTACK`) — a
normalised peg at parity `{{RESERVE_PARITY}}`, foreign interest rate
`{{RESERVE_FOREIGN_RATE}}`, money-demand semi-elasticity $\alpha$ =
`{{RESERVE_ALPHA}}`, initial domestic credit `{{RESERVE_CREDIT_0}}`, and
credit growth $\mu$ = `{{RESERVE_GROWTH}}`. The model validates its own
feasibility conditions ($0 < \alpha\mu < 1$, and initial credit small enough
that the peg has not already fallen) before computing an attack time.

**Vault — layered** (`vault_security.REFERENCE_RATINGS`) —
`{{VAULT_LAYER_COUNT}}` layers (perimeter, fence, guard response, vault door,
combination lock, gold storage), each rated in `[0,1]`, weighted by
`DEFAULT_WEIGHTS` and traversed in `LAYER_ORDER`.

**Vault — network** (`vault_threat_network.REFERENCE_GRAPH`) — an undirected
graph of `{{VAULT_ZONE_COUNT}}` defensive zones with intrusion-effort edge
costs. The reference intrusion problem is perimeter → gold chamber
(`REFERENCE_TARGET`); the reference defensive posture (`REFERENCE_HARDENING`)
is a budget of `{{VAULT_HARDENING_BUDGET}}` units buying
`{{VAULT_GAIN_PER_UNIT}}` effort each.

**Laser — scalar** (`laser_physics.REFERENCE_PHYSICS`) — power
`{{LASER_POWER_W}}` W onto a focused spot of `{{LASER_SPOT_AREA_M2}}` m²
against a steel plate of density `{{LASER_DENSITY_KGM3}}` kg/m³ and thickness
`{{LASER_THICKNESS_MM}}` mm, specific heat `{{LASER_SPECIFIC_HEAT}}` J/(kg·K),
$\Delta T$ = `{{LASER_DELTA_T_K}}` K, absorptivity `{{LASER_ABSORPTIVITY}}`.
A beam is classified *serious* at or above `{{LASER_SEVERITY_THRESHOLD_W}}` W.

**Laser — thermal** (`laser_thermal.REFERENCE_BEAM`) — an Nd:YAG-class
continuous-wave beam of wavelength `{{LASER_WAVELENGTH_NM}}` nm focused to a
waist of `{{LASER_WAIST_MM}}` mm, against steel of thermal conductivity
`{{LASER_CONDUCTIVITY}}` W/(m·K) melting at `{{LASER_MELT_TEMP_K}}` K from an
ambient of `{{LASER_AMBIENT_K}}` K, engaged within a
`{{LASER_THREAT_WINDOW_S}}` s threat window.

## Determinism policy

The mission declares a fixed seed of `{{GOLDFINGER_SEED}}` and performs **no**
random draws — the seed is recorded in provenance so a replay is auditable,
not because any sampling occurs. Persisted artifacts carry no wall-clock
dependence (`wall_time_s = 0.0` in provenance). The one deliberately varying
value is the `GENERATION_TIMESTAMP` token (currently
{{GENERATION_TIMESTAMP}}) and the `GOLDFINGER_VERSION_HASH` derived from the
full token map. Figure output is byte-deterministic for fixed inputs, which
`tests/test_figures.py` asserts by rendering twice and comparing.

## Software environment

- Python: as resolved by `uv` (the package requires `>=3.10`)
- Dependencies: NumPy, Matplotlib, PyYAML, and the frozen `bond-api` protocol
  (a local path dependency declared in `pyproject.toml` under
  `[tool.uv.sources]`; the sibling `bond-api` package in this working tree)
- Dev: pytest, pytest-cov, mypy, ruff, types-PyYAML

## Mission adapter

The BOND-API `MissionProvider` (`src/goldfinger/mission.py`) wraps all
{{GOLDFINGER_MODULE_COUNT}} models and registers six gadgets
(`market_corner`, `reserve_attack`, `vault_defense`, `vault_hardening`,
`laser_threat`, `laser_thermal`) with a module-level `GadgetRegistry`. It is
discoverable by slug `goldfinger` on `sys.path` and drives the full
brief–recon–plan–execute–debrief lifecycle with deterministic provenance. The
adapter's public shape is frozen across phases; the mission internals (assets,
plan steps, outcome results, lessons) are what deepen.
